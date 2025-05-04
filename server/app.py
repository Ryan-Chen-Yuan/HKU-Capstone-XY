#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import json
import os

# 加载环境变量
from load_env import load_environment

load_environment()

from service.mood_service import MoodService
from service.chat_service import ChatService
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
        session_id = data.get("session_id", str(uuid.uuid4()))
        timestamp = data.get("timestamp", datetime.now().isoformat())
        history = data.get("history", [])

        # 如果没有提供历史记录，但提供了session_id，则从数据库获取
        if not history and session_id and db.session_exists(session_id):
            history = db.get_chat_history(session_id)

        # 获取AI回复
        response = chat_service.get_response(message, history)

        # 构造响应消息
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        response_time = datetime.now().isoformat()

        # 保存对话记录到数据库
        db.save_message(session_id, user_id, "user", message, timestamp)
        db.save_message(
            session_id, user_id, "agent", response["content"], response_time
        )

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
        if not data or "user_id" not in data or "session_id" not in data or "messages" not in data:
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
            jsonify({"error_code": 500, "error_message": f"服务器内部错误: {str(e)}"}), 500
        )
    
if __name__ == "__main__":
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)

    # 启动服务器
    print(f"Starting server on {HOST}:{PORT}, debug mode: {DEBUG}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
