#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import threading
from datetime import datetime


class Database:
    """简单的基于文件的数据库实现，用于存储聊天历史记录和事件"""

    def __init__(self, data_dir="data"):
        """初始化数据库

        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        self.messages_dir = os.path.join(data_dir, "messages")
        self.events_dir = os.path.join(data_dir, "events")
        self.lock = threading.Lock()

        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.messages_dir, exist_ok=True)
        os.makedirs(self.events_dir, exist_ok=True)

        # 初始化会话文件
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _get_message_file(self, session_id):
        """获取消息存储文件的路径"""
        return os.path.join(self.messages_dir, f"{session_id}.json")

    def _get_events_file(self, session_id):
        """获取事件存储文件的路径"""
        return os.path.join(self.events_dir, f"{session_id}.json")
     
    def _get_mood_file(self, session_id):
        """获取情绪分析数据存储文件的路径"""
        return os.path.join(self.messages_dir, f"{session_id}_mood.json")

    def session_exists(self, session_id):
        """检查会话是否存在

        Args:
            session_id: 会话ID

        Returns:
            bool: 会话是否存在
        """
        try:
            with self.lock:
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    sessions = json.load(f)
                return session_id in sessions
        except Exception as e:
            print(f"Error checking session existence: {str(e)}")
            return False

    def save_message(self, session_id, user_id, role, content, timestamp=None):
        """保存消息

        Args:
            session_id: 会话ID
            user_id: 用户ID
            role: 消息发送者角色 ('user' 或 'agent')
            content: 消息内容
            timestamp: 时间戳，如果不提供则使用当前时间
        """
        try:
            if timestamp is None:
                timestamp = datetime.now().isoformat()

            message = {"role": role, "content": content, "timestamp": timestamp}

            with self.lock:
                # 确保会话存在
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    sessions = json.load(f)

                if session_id not in sessions:
                    sessions[session_id] = {
                        "user_id": user_id,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                    }
                else:
                    sessions[session_id]["updated_at"] = datetime.now().isoformat()

                with open(self.sessions_file, "w", encoding="utf-8") as f:
                    json.dump(sessions, f, ensure_ascii=False, indent=2)

                # 保存消息
                message_file = self._get_message_file(session_id)

                if os.path.exists(message_file):
                    with open(message_file, "r", encoding="utf-8") as f:
                        messages = json.load(f)
                else:
                    messages = []

                messages.append(message)

                with open(message_file, "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving message: {str(e)}")

    def get_chat_history(self, session_id, limit=None):
        """获取聊天历史记录

        Args:
            session_id: 会话ID
            limit: 最大消息数量，None表示获取全部

        Returns:
            list: 消息列表
        """
        try:
            message_file = self._get_message_file(session_id)

            if not os.path.exists(message_file):
                return []

            with self.lock:
                with open(message_file, "r", encoding="utf-8") as f:
                    messages = json.load(f)

            if limit is not None and limit > 0:
                messages = messages[-limit:]

            return messages

        except Exception as e:
            print(f"Error getting chat history: {str(e)}")
            return []

    def get_sessions(self, user_id=None):
        """获取会话列表

        Args:
            user_id: 用户ID，None表示获取所有会话

        Returns:
            dict: 会话列表
        """
        try:
            with self.lock:
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    sessions = json.load(f)

            if user_id is not None:
                return {
                    sid: data
                    for sid, data in sessions.items()
                    if data.get("user_id") == user_id
                }
            return sessions

        except Exception as e:
            print(f"Error getting sessions: {str(e)}")
            return {}

    def save_events(self, session_id, events):
        """保存事件列表

        Args:
            session_id: 会话ID
            events: 事件列表
        """
        try:
            with self.lock:
                # 确保会话存在
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    sessions = json.load(f)

                if session_id not in sessions:
                    print(f"Warning: Session {session_id} does not exist")
                    return

                # 保存事件
                events_file = self._get_events_file(session_id)

                if os.path.exists(events_file):
                    with open(events_file, "r", encoding="utf-8") as f:
                        existing_events = json.load(f)
                else:
                    existing_events = []

                # 添加新事件
                for event in events:
                    # 只有当事件没有ID时才生成新ID（保持EventService生成的ID）
                    if "id" not in event or not event["id"]:
                        import uuid
                        event["id"] = f"evt_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
                    event["created_at"] = datetime.now().isoformat()
                    existing_events.append(event)

                with open(events_file, "w", encoding="utf-8") as f:
                    json.dump(existing_events, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving events: {str(e)}")

    def get_events(self, session_id, limit=None):
        """获取事件列表

        Args:
            session_id: 会话ID
            limit: 最大事件数量，None表示获取全部

        Returns:
            list: 事件列表
        """
        try:
            events_file = self._get_events_file(session_id)

            if not os.path.exists(events_file):
                return []

            with self.lock:
                with open(events_file, "r", encoding="utf-8") as f:
                    events = json.load(f)

            if limit is not None and limit > 0:
                events = events[-limit:]

            return events

        except Exception as e:
            print(f"Error getting events: {str(e)}")
            return []

    def update_event(self, session_id, event_id, update_data):
        """更新事件

        Args:
            session_id: 会话ID
            event_id: 事件ID
            update_data: 更新数据字典

        Returns:
            bool: 更新是否成功
        """
        try:
            events_file = self._get_events_file(session_id)

            if not os.path.exists(events_file):
                return False

            with self.lock:
                with open(events_file, "r", encoding="utf-8") as f:
                    events = json.load(f)

                # 查找并更新事件
                updated = False
                for event in events:
                    if event.get("id") == event_id:
                        # 更新字段
                        for key, value in update_data.items():
                            event[key] = value
                        # 更新时间戳
                        event["updateTime"] = datetime.now().isoformat()
                        updated = True
                        break

                if updated:
                    with open(events_file, "w", encoding="utf-8") as f:
                        json.dump(events, f, ensure_ascii=False, indent=2)

                return updated

        except Exception as e:
            print(f"Error updating event: {str(e)}")
            return False

    def delete_event(self, session_id, event_id):
        """删除事件

        Args:
            session_id: 会话ID
            event_id: 事件ID
        """
        try:
            events_file = self._get_events_file(session_id)

            if not os.path.exists(events_file):
                return

            with self.lock:
                with open(events_file, "r", encoding="utf-8") as f:
                    events = json.load(f)

                # 过滤掉要删除的事件
                events = [event for event in events if event["id"] != event_id]

                with open(events_file, "w", encoding="utf-8") as f:
                    json.dump(events, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error deleting event: {str(e)}")

    def get_user_message_count(self, session_id):
        """获取会话中用户消息的数量

        Args:
            session_id: 会话ID

        Returns:
            int: 用户消息数量
        """
        try:
            message_file = self._get_message_file(session_id)

            if not os.path.exists(message_file):
                return 0

            with self.lock:
                with open(message_file, "r", encoding="utf-8") as f:
                    messages = json.load(f)

            # 只计算用户消息
            user_message_count = sum(1 for msg in messages if msg.get("role") == "user")
            return user_message_count

        except Exception as e:
            print(f"Error getting user message count: {str(e)}")
            return 0
        
     def save_mood_data(self, user_id, session_id, mood_data):
        """保存情绪分析数据
        Args:
            session_id: 会话ID
            mood_data: 情绪分析数据（dict 或 list）
        """
        try:
            with self.lock:
                # 确保会话存在
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    sessions = json.load(f)

                if session_id not in sessions:
                    print(f"Warning: Session {session_id} does not exist")
                    return

                mood_file = self._get_mood_file(session_id)

                if os.path.exists(mood_file):
                    with open(mood_file, "r", encoding="utf-8") as f:
                        existing_moods = json.load(f)
                else:
                    existing_moods = []

                # mood_data 可以是单个 dict 或 list
                if isinstance(mood_data, dict):
                    mood_data["created_at"] = datetime.now().isoformat()
                    existing_moods.append(mood_data)
                elif isinstance(mood_data, list):
                    for mood in mood_data:
                        mood["created_at"] = datetime.now().isoformat()
                        existing_moods.append(mood)

                with open(mood_file, "w", encoding="utf-8") as f:
                    json.dump(existing_moods, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving mood analysis: {str(e)}")

    def get_mood_analysis(self, session_id, limit=None):
        """获取情绪分析数据
        Args:
            session_id: 会话ID
            limit: 最大数量，None表示获取全部
        Returns:
            list: 情绪分析数据列表
        """
        try:
            mood_file = self._get_mood_file(session_id)

            if not os.path.exists(mood_file):
                return []

            with self.lock:
                with open(mood_file, "r", encoding="utf-8") as f:
                    moods = json.load(f)

            if limit is not None and limit > 0:
                moods = moods[-limit:]

            return moods

        except Exception as e:
            print(f"Error getting mood analysis: {str(e)}")
            return []

    def update_mood_analysis(self, session_id, mood_id, update_data):
        """更新情绪分析数据
        Args:
            session_id: 会话ID
            mood_id: 情绪分析数据ID
            update_data: 更新数据字典
        Returns:
            bool: 更新是否成功
        """
        try:
            mood_file = self._get_mood_file(session_id)

            if not os.path.exists(mood_file):
                return False

            with self.lock:
                with open(mood_file, "r", encoding="utf-8") as f:
                    moods = json.load(f)

                updated = False
                for mood in moods:
                    if mood.get("id") == mood_id:
                        for key, value in update_data.items():
                            mood[key] = value
                        mood["updateTime"] = datetime.now().isoformat()
                        updated = True
                        break

                if updated:
                    with open(mood_file, "w", encoding="utf-8") as f:
                        json.dump(moods, f, ensure_ascii=False, indent=2)

                return updated

        except Exception as e:
            print(f"Error updating mood analysis: {str(e)}")
            return False

    def delete_mood_analysis(self, session_id, mood_id):
        """删除情绪分析数据
        Args:
            session_id: 会话ID
            mood_id: 情绪分析数据ID
        """
        try:
            mood_file = self._get_mood_file(session_id)

            if not os.path.exists(mood_file):
                return

            with self.lock:
                with open(mood_file, "r", encoding="utf-8") as f:
                    moods = json.load(f)

                moods = [mood for mood in moods if mood.get("id") != mood_id]

                with open(mood_file, "w", encoding="utf-8") as f:
                    json.dump(moods, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error deleting mood analysis: {str(e)}")
