#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import json
import os
from threading import Thread
from collections import Counter

# 加载环境变量
from load_env import load_environment

load_environment()

from service.mood_service import MoodService
from service.event_service import EventService
from dao.database import Database
from service.analysis_report_service import AnalysisReportService
from service.chat_langgraph_optimized import optimized_chat  # 使用LangGraph优化版
from utils.chat_logger import chat_logger

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 获取环境变量配置
PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
DEBUG = os.environ.get("FLASK_ENV", "production") == "development"

# 初始化数据库和聊天服务
db = Database()
event_service = EventService()
analysis_service = AnalysisReportService()


def async_event_extraction(session_id, user_id, db, event_service):
    # 获取最近4条历史消息用于事件提取
    conversation = db.get_chat_history(session_id, limit=4)
    if conversation:
        events = event_service.extract_events(conversation)
        if events:
            db.save_events(session_id, events)


@app.route("/api/chat", methods=["POST"])
def chat():
    """处理聊天请求，获取AI回复"""
    try:
        # 获取请求数据
        data = request.json

        # 验证必要参数
        if not data or "user_id" not in data or "message" not in data:
            return jsonify({"error_code": 400, "error_message": "缺少必要参数"}), 400

        user_id = data["user_id"]
        message = data["message"]
        session_id = data["session_id"]
        if not session_id or session_id == "":
            # 如果没有提供session_id，则生成一个新的
            session_id = str(uuid.uuid4())
        # print(f"session_id: {session_id}")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        history = data.get("history", [])

        # 如果没有提供历史记录，但提供了session_id，则从数据库获取
        if not history and session_id and db.session_exists(session_id):
            history = db.get_chat_history(session_id)

        # 记录用户请求日志
        chat_logger.log_chat_request(user_id, session_id, message, timestamp)

        # 获取AI回复
        response = optimized_chat(
            user_input=message,
            user_id=user_id,
            session_id=session_id,
            history=history,
            enable_performance_monitoring=False,
        )
        # response = chat_service.get_response(message, history, session_id)

        # 构造响应消息
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        response_time = datetime.now().isoformat()

        # 保存对话记录到数据库
        db.save_message(session_id, user_id, "user", message, timestamp)
        db.save_message(
            session_id, user_id, "agent", response["response"], response_time
        )

        # 记录AI回复日志
        chat_logger.log_chat_response(
            user_id,
            session_id,
            response["response"],
            response.get("emotion", "neutral"),
            response.get("crisis_detected", False),
            response.get("search_results", None),
            response_time,
        )

        # 检查用户消息数量，每3条消息进行一次事件提取
        user_message_count = db.get_user_message_count(session_id)
        if user_message_count > 0 and user_message_count % 3 == 0:
            print(
                f"触发事件提取：会话 {session_id} 已有 {user_message_count} 条用户消息"
            )
            Thread(
                target=async_event_extraction,
                args=(session_id, user_id, db, event_service),
            ).start()

        # 构建基础响应
        response_data = {
            "message_id": message_id,
            "content": response["response"],
            "emotion": response.get("emotion", "neutral"),
            "timestamp": response_time,
            "session_id": session_id,
        }

        # 如果是知己报告回复，添加额外的报告数据
        if response.get("report_generated", False):
            response_data.update(
                {
                    "report_generated": True,
                    "report_summary": {
                        "sessions_analyzed": response.get("report_data", {})
                        .get("metadata", {})
                        .get("sessions_analyzed", 0),
                        "total_events": response.get("report_data", {})
                        .get("metadata", {})
                        .get("total_events", 0),
                        "emotion_records": response.get("report_data", {})
                        .get("metadata", {})
                        .get("emotion_records", 0),
                        "analysis_period_days": response.get("report_data", {})
                        .get("analysis_period", {})
                        .get("days", 30),
                    },
                }
            )

            # 如果前端需要完整报告数据，也可以包含（但通常不建议在聊天响应中包含大量数据）
            response_data["full_report_available"] = True

        # 返回响应
        return jsonify(response_data)

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return (
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}),
            500,
        )


@app.route("/api/chat/history", methods=["GET"])
def get_history():
    """获取历史对话记录"""
    try:
        user_id = request.args.get("user_id")
        session_id = request.args.get("session_id")

        if not user_id or not session_id:
            return jsonify({"error_code": 400, "error_message": "缺少必要参数"}), 400

        # 从数据库获取历史记录
        history = db.get_chat_history(session_id)

        # 返回历史记录
        return jsonify({"session_id": session_id, "messages": history})

    except Exception as e:
        print(f"Error in history endpoint: {str(e)}")
        return (
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}),
            500,
        )


@app.route("/api/mood", methods=["POST"])
def analyze_mood():
    """Analyze mood of messages and provide mood intensity, category, thinking, and scene."""
    try:
        # Get request data
        data = request.json

        # Validate required parameters
        if (
            not data
            or "user_id" not in data
            or "session_id" not in data
            or "messages" not in data
        ):
            return jsonify({"error_code": 400, "error_message": "缺少必要参数"}), 400

        user_id = data["user_id"]
        session_id = data["session_id"]
        messages = data["messages"]

        # Validate messages
        if not isinstance(messages, list) or not messages:
            return jsonify({"error_code": 400, "error_message": "消息内容无效"}), 400

        # Perform mood analysis
        mood_service = MoodService()
        mood_result = mood_service.analyze_mood(messages)

        # Extract results
        mood_intensity = mood_result["moodIntensity"]
        mood_category = mood_result["moodCategory"]
        thinking = mood_result["thinking"]
        scene = mood_result["scene"]

        # Generate a unique message ID and timestamp
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        response_time = datetime.now().isoformat()

        # Return mood analysis results
        return jsonify(
            {
                "message_id": message_id,
                "moodIntensity": mood_intensity,
                "moodCategory": mood_category,
                "thinking": thinking,
                "scene": scene,
                "timestamp": response_time,
                "session_id": session_id,
            }
        )

    except Exception as e:
        print(f"Error in mood analysis endpoint: {str(e)}")
        return (
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}),
            500,
        )


@app.route("/api/save_mood_data", methods=["POST"])
def save_mood_data():
    """保存情绪分析数据"""
    try:
        data = request.json
        print(data)
        if not data or "mood_data" not in data:  # session_id
            return jsonify({"error_code": 400, "error_message": "缺少必要参数"}), 400

        user_id = data["user_id"] if "user_id" in data else 0
        session_id = data["session_id"]
        mood_data = data["mood_data"]

        db.save_mood_data(user_id, session_id, mood_data)

        return (
            jsonify({"message": "情绪分析数据保存成功", "session_id": session_id}),
            200,
        )

    except Exception as e:
        print(f"Error in save_mood_data endpoint: {str(e)}")
        return (
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}),
            500,
        )


@app.route("/api/events/extract", methods=["POST"])
def extract_events():
    """从对话中提取事件"""
    try:
        # 获取请求数据
        data = request.json

        # 验证必要参数
        if not data or "conversation" not in data:
            return jsonify({"error_code": 400, "error_message": "缺少必要参数"}), 400

        conversation = data["conversation"]
        session_id = data.get("session_id", str(uuid.uuid4()))
        user_id = data.get("user_id")
        source_dialog_id = data.get(
            "source_dialog_id", f"dialog_{uuid.uuid4().hex[:8]}"
        )

        # 校验会话是否存在
        if not db.session_exists(session_id):
            return (
                jsonify(
                    {
                        "error_code": 404,
                        "error_message": f"会话 {session_id} 不存在，无法进行事件提取。请先创建对话。",
                    }
                ),
                404,
            )

        # 提取事件
        events = event_service.extract_events(conversation)

        # 添加对话来源ID
        for event in events:
            event["sourceDialogId"] = source_dialog_id

        # 保存事件到数据库
        if events:
            db.save_events(session_id, events)

        # 返回事件列表
        return jsonify(
            {
                "session_id": session_id,
                "events": events,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        print(f"Error in event extraction endpoint: {str(e)}")
        return (
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}),
            500,
        )


@app.route("/api/events", methods=["GET"])
def get_events():
    """获取事件列表"""
    try:
        session_id = request.args.get("session_id")
        limit = request.args.get("limit")

        if not session_id:
            return jsonify({"error_code": 400, "error_message": "缺少必要参数"}), 400

        # 从数据库获取事件列表
        events = db.get_events(session_id, int(limit) if limit else None)

        return jsonify(
            {
                "session_id": session_id,
                "events": events,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        print(f"Error in get events endpoint: {str(e)}")
        return (
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}),
            500,
        )


@app.route("/api/events/<event_id>", methods=["PUT"])
def update_event(event_id):
    """更新事件"""
    try:
        session_id = request.args.get("session_id")
        data = request.json

        if not session_id:
            return (
                jsonify({"error_code": 400, "error_message": "缺少session_id参数"}),
                400,
            )

        if not data:
            return jsonify({"error_code": 400, "error_message": "缺少更新数据"}), 400

        # 从数据库更新事件
        success = db.update_event(session_id, event_id, data)

        if not success:
            return jsonify({"error_code": 404, "error_message": "事件不存在"}), 404

        return jsonify(
            {
                "session_id": session_id,
                "event_id": event_id,
                "message": "事件更新成功",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        print(f"Error in update event endpoint: {str(e)}")
        return (
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}),
            500,
        )


@app.route("/api/events/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    """删除事件"""
    try:
        session_id = request.args.get("session_id")

        if not session_id:
            return jsonify({"error_code": 400, "error_message": "缺少必要参数"}), 400

        # 从数据库删除事件
        db.delete_event(session_id, event_id)

        return jsonify(
            {
                "session_id": session_id,
                "event_id": event_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        print(f"Error in delete event endpoint: {str(e)}")
        return (
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}),
            500,
        )


@app.route("/api/analysis/user-report", methods=["POST"])
def generate_user_analysis_report():
    """生成用户分析报告"""
    try:
        # 获取请求数据
        data = request.json

        # 验证必要参数
        if not data or "user_id" not in data:
            return (
                jsonify({"error_code": 400, "error_message": "缺少必要参数 user_id"}),
                400,
            )

        user_id = data["user_id"]
        session_ids = data.get("session_ids", [])
        time_period = data.get("time_period", 30)  # 默认30天

        # 如果没有提供session_ids，从数据库获取用户的所有会话
        if not session_ids:
            sessions = db.get_sessions(user_id)
            session_ids = list(sessions.keys())

        if not session_ids:
            return (
                jsonify(
                    {
                        "error_code": 404,
                        "error_message": f"用户 {user_id} 没有可分析的会话数据",
                    }
                ),
                404,
            )

        # 生成分析报告
        report = analysis_service.generate_user_report(
            user_id, session_ids, time_period
        )

        if "error" in report:
            return (
                jsonify(
                    {
                        "error_code": 500,
                        "error_message": f"生成报告失败: {report['error']}",
                    }
                ),
                500,
            )

        # 返回报告
        return jsonify(
            {"success": True, "report": report, "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        print(f"Error in user analysis report endpoint: {str(e)}")
        return (
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}),
            500,
        )


@app.route("/api/analysis/export-report", methods=["POST"])
def export_user_report():
    """导出用户分析报告"""
    try:
        # 获取请求数据
        data = request.json

        # 验证必要参数
        if not data or "user_id" not in data:
            return (
                jsonify({"error_code": 400, "error_message": "缺少必要参数 user_id"}),
                400,
            )

        user_id = data["user_id"]
        session_ids = data.get("session_ids", [])
        time_period = data.get("time_period", 30)
        export_format = data.get("format", "json")  # json 或 text

        # 如果没有提供session_ids，从数据库获取用户的所有会话
        if not session_ids:
            sessions = db.get_sessions(user_id)
            session_ids = list(sessions.keys())

        if not session_ids:
            return (
                jsonify(
                    {
                        "error_code": 404,
                        "error_message": f"用户 {user_id} 没有可导出的会话数据",
                    }
                ),
                404,
            )

        # 生成报告
        report = analysis_service.generate_user_report(
            user_id, session_ids, time_period
        )

        if "error" in report:
            return (
                jsonify(
                    {
                        "error_code": 500,
                        "error_message": f"生成报告失败: {report['error']}",
                    }
                ),
                500,
            )

        # 导出报告
        exported_content = analysis_service.export_report(report, export_format)

        # 根据格式设置响应头
        if export_format == "text":
            response = app.response_class(
                response=exported_content,
                mimetype="text/plain",
                headers={
                    "Content-Disposition": f'attachment; filename="user_analysis_report_{user_id}.txt"'
                },
            )
        else:  # json
            response = app.response_class(
                response=exported_content,
                mimetype="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="user_analysis_report_{user_id}.json"'
                },
            )

        return response

    except Exception as e:
        print(f"Error in export report endpoint: {str(e)}")
        return (
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}),
            500,
        )


@app.route("/api/analysis/summary", methods=["GET"])
def get_user_analysis_summary():
    """获取用户分析摘要信息"""
    try:
        user_id = request.args.get("user_id")
        time_period = int(request.args.get("time_period", 30))

        if not user_id:
            return (
                jsonify({"error_code": 400, "error_message": "缺少必要参数 user_id"}),
                400,
            )

        # 获取用户的所有会话
        sessions = db.get_sessions(user_id)
        session_ids = list(sessions.keys())

        if not session_ids:
            return (
                jsonify(
                    {
                        "error_code": 404,
                        "error_message": f"用户 {user_id} 没有可分析的数据",
                    }
                ),
                404,
            )

        # 生成快速摘要（不使用AI，只用统计数据）
        from dao.database import Database
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=time_period)

        # 收集基本统计数据
        total_events = 0
        total_patterns = 0
        emotions = db.get_emotion_history(user_id, limit=50)

        # 过滤时间范围内的情绪数据
        recent_emotions = [
            emotion
            for emotion in emotions
            if datetime.fromisoformat(emotion.get("timestamp", "1900-01-01"))
            >= cutoff_date
        ]

        # 统计事件和模式
        for session_id in session_ids:
            events = db.get_events(session_id)
            filtered_events = [
                event
                for event in events
                if datetime.fromisoformat(event.get("time", "1900-01-01"))
                >= cutoff_date
            ]
            total_events += len(filtered_events)

            pattern = db.get_pattern_analysis(session_id)
            if pattern:
                total_patterns += 1

        # 计算情绪统计
        emotion_stats = {}
        if recent_emotions:
            emotion_scores = [float(e.get("emotion_score", 0)) for e in recent_emotions]
            emotion_categories = [
                e.get("emotion_category", "unknown") for e in recent_emotions
            ]

            emotion_stats = {
                "average_score": sum(emotion_scores) / len(emotion_scores),
                "score_range": {"min": min(emotion_scores), "max": max(emotion_scores)},
                "most_common_emotion": (
                    Counter(emotion_categories).most_common(1)[0][0]
                    if emotion_categories
                    else "unknown"
                ),
                "total_records": len(recent_emotions),
            }

        # 返回摘要
        summary = {
            "user_id": user_id,
            "analysis_period": time_period,
            "data_availability": {
                "total_sessions": len(session_ids),
                "total_events": total_events,
                "total_patterns": total_patterns,
                "emotion_records": len(recent_emotions),
            },
            "emotion_summary": emotion_stats,
            "can_generate_report": total_events > 0
            or total_patterns > 0
            or len(recent_emotions) > 0,
            "generated_at": datetime.now().isoformat(),
        }

        return jsonify({"success": True, "summary": summary})

    except Exception as e:
        print(f"Error in analysis summary endpoint: {str(e)}")
        return (
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}),
            500,
        )


if __name__ == "__main__":
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)

    # 启动服务器
    print(f"Starting server on {HOST}:{PORT}, debug mode: {DEBUG}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
