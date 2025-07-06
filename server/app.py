#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import json
import os
from threading import Thread

# 加载环境变量
from load_env import load_environment

load_environment()

from service.mood_service import MoodService
from service.chat_service import ChatService
from service.event_service import EventService
from dao.database import Database

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 获取环境变量配置
PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
DEBUG = os.environ.get("FLASK_ENV", "production") == "development"

# 初始化数据库和聊天服务
db = Database()
chat_service = ChatService()
event_service = EventService()

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

        # 获取AI回复
        response = chat_service.get_response(message, history, session_id)

        # 构造响应消息
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        response_time = datetime.now().isoformat()

        # 保存对话记录到数据库
        db.save_message(session_id, user_id, "user", message, timestamp)
        db.save_message(
            session_id, user_id, "agent", response["content"], response_time
        )

        # 检查用户消息数量，每3条消息进行一次事件提取
        user_message_count = db.get_user_message_count(session_id)
        if user_message_count > 0 and user_message_count % 3 == 0:
            print(f"触发事件提取：会话 {session_id} 已有 {user_message_count} 条用户消息")
            Thread(target=async_event_extraction, args=(session_id, user_id, db, event_service)).start()

        # 返回响应
        return jsonify(
            {
                "message_id": message_id,
                "content": response["content"],
                "emotion": response.get("emotion", "neutral"),
                "timestamp": response_time,
                "session_id": session_id,
            }
        )

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

        # Save mood analysis result to the database
        # db.save_sentiment_analysis(session_id, user_id, mood_intensity, mood_category, thinking, scene)

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
        source_dialog_id = data.get("source_dialog_id", f"dialog_{uuid.uuid4().hex[:8]}")

        # 校验会话是否存在
        if not db.session_exists(session_id):
            return jsonify({
                "error_code": 404,
                "error_message": f"会话 {session_id} 不存在，无法进行事件提取。请先创建对话。"
            }), 404

        # 提取事件
        events = event_service.extract_events(conversation)
        
        # 添加对话来源ID
        for event in events:
            event["sourceDialogId"] = source_dialog_id

        # 保存事件到数据库
        if events:
            db.save_events(session_id, events)

        # 返回事件列表
        return jsonify({
            "session_id": session_id,
            "events": events,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Error in event extraction endpoint: {str(e)}")
        return jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}), 500

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

        return jsonify({
            "session_id": session_id,
            "events": events,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Error in get events endpoint: {str(e)}")
        return jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}), 500

@app.route("/api/events/<event_id>", methods=["PUT"])
def update_event(event_id):
    """更新事件"""
    try:
        session_id = request.args.get("session_id")
        data = request.json
        
        if not session_id:
            return jsonify({"error_code": 400, "error_message": "缺少session_id参数"}), 400
            
        if not data:
            return jsonify({"error_code": 400, "error_message": "缺少更新数据"}), 400

        # 从数据库更新事件
        success = db.update_event(session_id, event_id, data)
        
        if not success:
            return jsonify({"error_code": 404, "error_message": "事件不存在"}), 404

        return jsonify({
            "session_id": session_id,
            "event_id": event_id,
            "message": "事件更新成功",
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Error in update event endpoint: {str(e)}")
        return jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}), 500

@app.route("/api/events/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    """删除事件"""
    try:
        session_id = request.args.get("session_id")
        
        if not session_id:
            return jsonify({"error_code": 400, "error_message": "缺少必要参数"}), 400

        # 从数据库删除事件
        db.delete_event(session_id, event_id)

        return jsonify({
            "session_id": session_id,
            "event_id": event_id,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Error in delete event endpoint: {str(e)}")
        return jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}), 500
      

if __name__ == "__main__":
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)

    # 启动服务器
    print(f"Starting server on {HOST}:{PORT}, debug mode: {DEBUG}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
