#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
心理咨询对话系统 - 统一版本
合并了原app.py和app_fixed.py的功能
支持新旧格式API，包含完整的错误处理和日志记录
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import json
import os
from threading import Thread
from collections import Counter

# 加载环境变量（避免与start.py重复输出）
if not os.environ.get('ENV_LOADED'):
    from load_env import load_environment
    load_environment()
    os.environ['ENV_LOADED'] = 'true'

from service.mood_service import MoodService
from service.event_service import EventService
from dao.database import Database
from service.analysis_report_service import AnalysisReportService

# RAG 增强的聊天服务
rag_enabled = os.environ.get("ENABLE_RAG", "true").lower() == "true"
if rag_enabled:
    try:
        from service.rag_enhanced_chat import optimized_chat_with_rag as optimized_chat
        print("✅ 使用 RAG 增强的聊天服务")
    except ImportError as e:
        print(f"⚠️ RAG 增强服务导入失败: {e}")
        from service.chat_langgraph_optimized import optimized_chat
        print("🔄 回退到标准聊天服务")
else:
    from service.chat_langgraph_optimized import optimized_chat
    print("ℹ️ RAG 功能已禁用，使用标准聊天服务")

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
    """异步事件提取"""
    try:
        # 获取最近4条历史消息用于事件提取
        conversation = db.get_chat_history(session_id, limit=4)
        if conversation:
            events = event_service.extract_events_from_conversation(conversation)
            if events:
                # 保存提取的事件
                for event in events:
                    event_service.save_event(session_id, event)
                print(f"为会话 {session_id} 提取了 {len(events)} 个事件")
    except Exception as e:
        print(f"异步事件提取失败: {e}")


def flatten_messages(messages):
    """
    处理嵌套列表的情况，将其展平为字符串列表
    兼容前端发送的不同格式
    """
    flattened_messages = []
    for msg in messages:
        if isinstance(msg, list):
            # 如果是列表，取列表中的所有字符串元素
            for submsg in msg:
                if isinstance(submsg, str) and submsg.strip():
                    flattened_messages.append(submsg)
        elif isinstance(msg, str) and msg.strip():
            # 如果是字符串，直接添加
            flattened_messages.append(msg)
    return flattened_messages


@app.route("/api/chat", methods=["POST"])
def chat():
    """聊天对话API"""
    try:
        data = request.get_json()
        
        # 获取必要参数
        user_id = data.get("user_id", "default_user")
        session_id = data.get("session_id", str(uuid.uuid4()))
        message = data.get("message", "")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        history = data.get("history", [])
        
        if not message.strip():
            return jsonify({"error": "消息内容不能为空"}), 400
        
        # 在处理开始时就记录用户消息
        try:
            chat_logger.log_user_message_start(
                user_id=user_id,
                session_id=session_id,
                user_message=message,
                timestamp=timestamp
            )
        except Exception as log_error:
            print(f"用户消息日志记录失败: {log_error}")
        
        # 使用优化的聊天服务
        response = optimized_chat(
            user_input=message,
            user_id=user_id,
            session_id=session_id,
            history=history,
            enable_performance_monitoring=True
        )
        
        # 构建响应
        result = {
            "content": response.get("response", ""),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "emotion": response.get("emotion", "neutral"),
            "crisis_detected": response.get("crisis_detected", False),
            "processing_time": response.get("processing_time", 0)
        }
        
        # 如果有RAG上下文，添加到响应中
        if response.get("rag_context"):
            result["rag_context"] = response.get("rag_context")
        
        if response.get("search_results"):
            result["search_results"] = response.get("search_results")
        
        # 记录AI响应日志
        try:
            chat_logger.log_chat_response(
                user_id=user_id,
                session_id=session_id,
                response=result["content"],
                emotion=result["emotion"],
                crisis_detected=result["crisis_detected"],
                search_results=response.get("search_results"),
                timestamp=timestamp
            )
            
            # 如果启用详细日志，记录处理时间
            if chat_logger.detailed_logging_enabled and result["processing_time"] > 0:
                print(f"⏱️  处理时间: {result['processing_time']:.3f}秒")
                print("-" * 50)
        except Exception as log_error:
            print(f"AI响应日志记录失败: {log_error}")
        
        # 异步启动事件提取
        try:
            thread = Thread(
                target=async_event_extraction,
                args=(session_id, user_id, db, event_service)
            )
            thread.daemon = True
            thread.start()
        except Exception as thread_error:
            print(f"启动异步事件提取失败: {thread_error}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"聊天API错误: {e}")
        return jsonify({
            "error": "系统内部错误",
            "error_message": str(e)
        }), 500


@app.route("/api/chat/history", methods=["GET"])
def get_chat_history():
    """获取聊天历史"""
    try:
        user_id = request.args.get("user_id", "default_user")
        session_id = request.args.get("session_id")
        limit = int(request.args.get("limit", 50))
        
        if not session_id:
            return jsonify({"error": "缺少session_id参数"}), 400
        
        # 从数据库获取消息历史
        messages = db.get_conversation_messages(session_id, limit=limit)
        
        return jsonify({
            "messages": messages,
            "session_id": session_id,
            "user_id": user_id,
            "total": len(messages)
        })
        
    except Exception as e:
        print(f"获取聊天历史错误: {e}")
        return jsonify({"error": "获取历史记录失败"}), 500


@app.route("/api/mood", methods=["POST"])
def mood_analysis():
    """情绪分析API - 兼容新旧格式"""
    try:
        data = request.get_json()
        
        # 检查请求数据
        if not data:
            return jsonify({"error": "请求数据为空"}), 400
        
        # 判断是新格式还是旧格式
        if "messages" in data:
            # 旧格式: {"user_id": "xxx", "session_id": "xxx", "messages": [...]}
            
            if "user_id" not in data or "session_id" not in data:
                return jsonify({
                    "error_code": 400, 
                    "error_message": "缺少必要参数: user_id, session_id"
                }), 400
            
            user_id = data["user_id"]
            session_id = data["session_id"]
            messages = data["messages"]
            
            # 如果session_id为空，生成一个新的
            if not session_id or session_id == "":
                session_id = str(uuid.uuid4())
            
            # 验证messages格式
            if not isinstance(messages, list) or not messages:
                return jsonify({
                    "error_code": 400, 
                    "error_message": "消息内容无效"
                }), 400
            
            # 处理嵌套列表的情况，将其展平为字符串列表
            flattened_messages = flatten_messages(messages)
            
            # 确保有有效的消息
            if not flattened_messages:
                return jsonify({
                    "error_code": 400, 
                    "error_message": "没有有效的消息内容"
                }), 400
            
            # 使用旧格式调用MoodService
            mood_service = MoodService()
            mood_result = mood_service.analyze_mood(flattened_messages)
            
            # 记录情绪分析结果的详细日志
            chat_logger.log_mood_analysis(
                user_id=user_id,
                session_id=session_id,
                messages=flattened_messages,  # 使用展平后的消息列表
                mood_result=mood_result,
                suppress_header=True  # 这是聊天流程的一部分，不需要额外的分隔符
            )
            
            # 返回旧格式响应
            message_id = f"msg_{uuid.uuid4().hex[:8]}"
            response_time = datetime.now().isoformat()
            
            return jsonify({
                "message_id": message_id,
                "moodIntensity": mood_result["moodIntensity"],
                "moodCategory": mood_result["moodCategory"],
                "thinking": mood_result["thinking"],
                "scene": mood_result["scene"],
                "timestamp": response_time,
                "session_id": session_id,
            })
        
        else:
            # 新格式: {"message"/"text"/"content": "xxx", "user_id": "xxx", "session_id": "xxx"}
            print(f"✨ 检测到新格式请求: {data}")
            
            text = data.get("message") or data.get("text") or data.get("content", "")
            user_id = data.get("user_id", "default_user")
            session_id = data.get("session_id", str(uuid.uuid4()))
            
            # 详细的错误信息
            if not text or not text.strip():
                return jsonify({
                    "error": "文本内容不能为空",
                    "received_data": {k: v for k, v in data.items() if k not in ["message", "text", "content"]}
                }), 400
            
            # 使用新格式调用MoodService
            mood_service = MoodService()
            result = mood_service.analyze_mood(
                text=text,
                user_id=user_id,
                session_id=session_id
            )
            
            # 记录情绪分析结果的详细日志
            chat_logger.log_mood_analysis(
                user_id=user_id,
                session_id=session_id,
                messages=[text],
                mood_result=result,
                suppress_header=False  # 新格式通常是独立调用，保留分隔符
            )
            
            return jsonify(result)
        
    except Exception as e:
        print(f"情绪分析API错误: {e}")
        print(f"请求数据: {request.get_json()}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "情绪分析失败",
            "detail": str(e)
        }), 500


@app.route("/api/events", methods=["GET"])
def get_events():
    """获取事件列表"""
    try:
        session_id = request.args.get("session_id")
        limit = int(request.args.get("limit", 10))
        
        if not session_id:
            return jsonify({"error": "缺少session_id参数"}), 400
        
        # 从数据库获取事件
        events = event_service.get_events_by_session(session_id, limit=limit)
        
        return jsonify({
            "events": events,
            "session_id": session_id,
            "total": len(events)
        })
        
    except Exception as e:
        print(f"获取事件列表错误: {e}")
        return jsonify({"error": "获取事件失败"}), 500


@app.route("/api/events/<event_id>", methods=["PUT"])
def update_event(event_id):
    """更新事件"""
    try:
        session_id = request.args.get("session_id")
        data = request.get_json()
        
        if not session_id:
            return jsonify({"error": "缺少session_id参数"}), 400
        
        # 更新事件
        success = event_service.update_event(event_id, data)
        
        if success:
            return jsonify({"message": "事件更新成功"})
        else:
            return jsonify({"error": "事件更新失败"}), 400
        
    except Exception as e:
        print(f"更新事件错误: {e}")
        return jsonify({"error": "更新事件失败"}), 500


@app.route("/api/events/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    """删除事件"""
    try:
        session_id = request.args.get("session_id")
        
        if not session_id:
            return jsonify({"error": "缺少session_id参数"}), 400
        
        # 删除事件
        success = event_service.delete_event(event_id)
        
        if success:
            return jsonify({"message": "事件删除成功"})
        else:
            return jsonify({"error": "事件删除失败"}), 400
        
    except Exception as e:
        print(f"删除事件错误: {e}")
        return jsonify({"error": "删除事件失败"}), 500


@app.route("/api/save_mood_data", methods=["POST"])
def save_mood_data():
    """保存情绪数据"""
    try:
        data = request.get_json()
        session_id = data.get("session_id")
        mood_data = data.get("mood_data", {})
        
        if not session_id:
            return jsonify({"error": "缺少session_id参数"}), 400
        
        # 保存情绪数据到数据库
        success = db.save_mood_score(
            session_id=session_id,
            mood_data=mood_data,
            timestamp=datetime.now().isoformat()
        )
        
        if success:
            return jsonify({"message": "情绪数据保存成功"})
        else:
            return jsonify({"error": "情绪数据保存失败"}), 400
        
    except Exception as e:
        print(f"保存情绪数据错误: {e}")
        return jsonify({"error": "保存情绪数据失败"}), 500


@app.route("/api/analysis/report", methods=["GET"])
def get_analysis_report():
    """获取分析报告"""
    try:
        user_id = request.args.get("user_id", "default_user")
        days = int(request.args.get("days", 7))
        
        # 生成分析报告
        report = analysis_service.generate_comprehensive_report(user_id, days)
        
        return jsonify(report)
        
    except Exception as e:
        print(f"获取分析报告错误: {e}")
        return jsonify({"error": "获取分析报告失败"}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0",  # 更新版本号
        "features": {
            "rag_enabled": rag_enabled,
            "guided_inquiry": os.environ.get("ENABLE_GUIDED_INQUIRY", "true").lower() == "true",
            "pattern_analysis": os.environ.get("ENABLE_PATTERN_ANALYSIS", "true").lower() == "true",
            "chat_logging": os.environ.get("ENABLE_CHAT_LOGGING", "true").lower() == "true",
            "emotion_logging": os.environ.get("ENABLE_EMOTION_LOGGING", "true").lower() == "true",
            "api_compatibility": "新旧格式兼容"
        }
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "API端点不存在"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "服务器内部错误"}), 500


if __name__ == "__main__":
    print(f"🚀 启动心理咨询API服务器...")
    print(f"📍 地址: http://{HOST}:{PORT}")
    print(f"🔧 调试模式: {'开启' if DEBUG else '关闭'}")
    print(f"🤖 RAG功能: {'启用' if rag_enabled else '禁用'}")
    print(f"🔄 API兼容性: 支持新旧格式")
    app.run(host=HOST, port=PORT, debug=DEBUG)
