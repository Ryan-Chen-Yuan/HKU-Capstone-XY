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

                        event["id"] = (
                            f"evt_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
                        )
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

    def get_user_profile(self, user_id):
        """获取用户画像数据

        Args:
            user_id: 用户ID

        Returns:
            dict: 用户画像数据
        """
        try:
            profiles_file = os.path.join(self.data_dir, "user_profiles.json")

            if not os.path.exists(profiles_file):
                return {}

            with self.lock:
                with open(profiles_file, "r", encoding="utf-8") as f:
                    profiles = json.load(f)

            return profiles.get(user_id, {})

        except Exception as e:
            print(f"Error getting user profile: {str(e)}")
            return {}

    def save_long_term_memory(self, user_id, memory_content):
        """保存长期记忆

        Args:
            user_id: 用户ID
            memory_content: 记忆内容
        """
        try:
            memory_file = os.path.join(self.data_dir, "long_term_memory.json")

            with self.lock:
                # 读取现有长期记忆
                if os.path.exists(memory_file):
                    with open(memory_file, "r", encoding="utf-8") as f:
                        memories = json.load(f)
                else:
                    memories = {}

                # 添加新记忆
                if user_id not in memories:
                    memories[user_id] = []

                memory_entry = {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "content": memory_content,
                }
                memories[user_id].append(memory_entry)

                # 保存长期记忆
                with open(memory_file, "w", encoding="utf-8") as f:
                    json.dump(memories, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving long term memory: {str(e)}")

    def get_long_term_memory(self, user_id, limit=None):
        """获取长期记忆

        Args:
            user_id: 用户ID
            limit: 获取的记忆数量限制

        Returns:
            list: 长期记忆列表
        """
        try:
            memory_file = os.path.join(self.data_dir, "long_term_memory.json")

            if not os.path.exists(memory_file):
                return []

            with self.lock:
                with open(memory_file, "r", encoding="utf-8") as f:
                    memories = json.load(f)

            user_memories = memories.get(user_id, [])

            if limit is not None and limit > 0:
                user_memories = user_memories[-limit:]

            return user_memories

        except Exception as e:
            print(f"Error getting long term memory: {str(e)}")
            return []

    def save_emotion_score(
        self, user_id, session_id, emotion_score, emotion_category=None
    ):
        """保存情绪评分

        Args:
            user_id: 用户ID
            session_id: 会话ID
            emotion_score: 情绪评分
            emotion_category: 情绪类别（可选）
        """
        try:
            emotions_file = os.path.join(self.data_dir, "emotion_scores.json")

            with self.lock:
                # 读取现有情绪数据
                if os.path.exists(emotions_file):
                    with open(emotions_file, "r", encoding="utf-8") as f:
                        emotions = json.load(f)
                else:
                    emotions = {}

                # 添加情绪数据
                if user_id not in emotions:
                    emotions[user_id] = []

                emotion_entry = {
                    "session_id": session_id,
                    "emotion_score": emotion_score,
                    "emotion_category": emotion_category,
                    "timestamp": datetime.now().isoformat(),
                }
                emotions[user_id].append(emotion_entry)

                # 保存情绪数据
                with open(emotions_file, "w", encoding="utf-8") as f:
                    json.dump(emotions, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving emotion score: {str(e)}")

    def get_emotion_history(self, user_id, limit=None):
        """获取用户情绪历史

        Args:
            user_id: 用户ID
            limit: 获取的数量限制

        Returns:
            list: 情绪历史列表
        """
        try:
            emotions_file = os.path.join(self.data_dir, "emotion_scores.json")

            if not os.path.exists(emotions_file):
                return []

            with self.lock:
                with open(emotions_file, "r", encoding="utf-8") as f:
                    emotions = json.load(f)

            user_emotions = emotions.get(user_id, [])

            if limit is not None and limit > 0:
                user_emotions = user_emotions[-limit:]

            return user_emotions

        except Exception as e:
            print(f"Error getting emotion history: {str(e)}")
            return []

    def save_session_plan(self, session_id, plan_data):
        """保存会话计划

        Args:
            session_id: 会话ID
            plan_data: 计划数据
        """
        try:
            plans_dir = os.path.join(self.data_dir, "plans")
            os.makedirs(plans_dir, exist_ok=True)

            plan_file = os.path.join(plans_dir, f"{session_id}.json")

            with self.lock:
                with open(plan_file, "w", encoding="utf-8") as f:
                    json.dump(plan_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving session plan: {str(e)}")

    def get_session_plan(self, session_id):
        """获取会话计划

        Args:
            session_id: 会话ID

        Returns:
            dict: 会话计划数据
        """
        try:
            plans_dir = os.path.join(self.data_dir, "plans")
            plan_file = os.path.join(plans_dir, f"{session_id}.json")

            if not os.path.exists(plan_file):
                return {}

            with self.lock:
                with open(plan_file, "r", encoding="utf-8") as f:
                    return json.load(f)

        except Exception as e:
            print(f"Error getting session plan: {str(e)}")
            return {}

    def save_user_profile(self, user_id, profile_data):
        """保存用户画像数据

        Args:
            user_id: 用户ID
            profile_data: 用户画像数据字典
        """
        try:
            profiles_file = os.path.join(self.data_dir, "user_profiles.json")

            with self.lock:
                # 读取现有用户画像
                if os.path.exists(profiles_file):
                    with open(profiles_file, "r", encoding="utf-8") as f:
                        profiles = json.load(f)
                else:
                    profiles = {}

                # 更新用户画像
                if user_id not in profiles:
                    profiles[user_id] = {}
                profiles[user_id].update(profile_data)
                profiles[user_id]["updated_at"] = datetime.now().isoformat()

                # 保存用户画像
                with open(profiles_file, "w", encoding="utf-8") as f:
                    json.dump(profiles, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving user profile: {str(e)}")

    def get_user_profile(self, user_id):
        """获取用户画像数据

        Args:
            user_id: 用户ID

        Returns:
            dict: 用户画像数据
        """
        try:
            profiles_file = os.path.join(self.data_dir, "user_profiles.json")

            if not os.path.exists(profiles_file):
                return {}

            with self.lock:
                with open(profiles_file, "r", encoding="utf-8") as f:
                    profiles = json.load(f)

            return profiles.get(user_id, {})

        except Exception as e:
            print(f"Error getting user profile: {str(e)}")
            return {}

    def save_inquiry_result(self, session_id, inquiry_data):
        """保存引导性询问结果

        Args:
            session_id: 会话ID
            inquiry_data: 引导性询问结果数据
        """
        try:
            inquiry_dir = os.path.join(self.data_dir, "inquiry_results")
            os.makedirs(inquiry_dir, exist_ok=True)

            inquiry_file = os.path.join(inquiry_dir, f"{session_id}.json")

            # 添加时间戳
            inquiry_data["saved_at"] = datetime.now().isoformat()

            with self.lock:
                with open(inquiry_file, "w", encoding="utf-8") as f:
                    json.dump(inquiry_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving inquiry result: {str(e)}")

    def get_inquiry_result(self, session_id):
        """获取引导性询问结果

        Args:
            session_id: 会话ID

        Returns:
            dict: 引导性询问结果数据
        """
        try:
            inquiry_dir = os.path.join(self.data_dir, "inquiry_results")
            inquiry_file = os.path.join(inquiry_dir, f"{session_id}.json")

            if not os.path.exists(inquiry_file):
                return {}

            with self.lock:
                with open(inquiry_file, "r", encoding="utf-8") as f:
                    return json.load(f)

        except Exception as e:
            print(f"Error getting inquiry result: {str(e)}")
            return {}

    def save_pattern_analysis(self, session_id, pattern_data):
        """保存模式分析结果

        Args:
            session_id: 会话ID
            pattern_data: 模式分析结果数据
        """
        try:
            patterns_dir = os.path.join(self.data_dir, "patterns")
            os.makedirs(patterns_dir, exist_ok=True)

            pattern_file = os.path.join(patterns_dir, f"{session_id}.json")

            # 添加时间戳
            pattern_data["saved_at"] = datetime.now().isoformat()

            with self.lock:
                with open(pattern_file, "w", encoding="utf-8") as f:
                    json.dump(pattern_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving pattern analysis: {str(e)}")

    def get_pattern_analysis(self, session_id):
        """获取模式分析结果

        Args:
            session_id: 会话ID

        Returns:
            dict: 模式分析结果数据
        """
        try:
            patterns_dir = os.path.join(self.data_dir, "patterns")
            pattern_file = os.path.join(patterns_dir, f"{session_id}.json")

            if not os.path.exists(pattern_file):
                return {}

            with self.lock:
                with open(pattern_file, "r", encoding="utf-8") as f:
                    return json.load(f)

        except Exception as e:
            print(f"Error getting pattern analysis: {str(e)}")
            return {}

    def save_inquiry_history(self, session_id, inquiry_data):
        """保存引导性询问历史记录

        Args:
            session_id: 会话ID
            inquiry_data: 引导性询问数据
        """
        try:
            inquiry_dir = os.path.join(self.data_dir, "inquiry_history")
            os.makedirs(inquiry_dir, exist_ok=True)

            inquiry_file = os.path.join(inquiry_dir, f"{session_id}.json")

            # 添加时间戳
            inquiry_data["timestamp"] = datetime.now().isoformat()

            with self.lock:
                # 读取现有历史记录
                if os.path.exists(inquiry_file):
                    with open(inquiry_file, "r", encoding="utf-8") as f:
                        inquiry_history = json.load(f)
                else:
                    inquiry_history = []

                # 添加新的询问记录
                inquiry_history.append(inquiry_data)

                # 保存更新后的历史记录
                with open(inquiry_file, "w", encoding="utf-8") as f:
                    json.dump(inquiry_history, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving inquiry history: {str(e)}")

    def get_inquiry_history(self, session_id, limit=None):
        """获取引导性询问历史记录

        Args:
            session_id: 会话ID
            limit: 获取的记录数量限制

        Returns:
            list: 引导性询问历史记录列表
        """
        try:
            inquiry_dir = os.path.join(self.data_dir, "inquiry_history")
            inquiry_file = os.path.join(inquiry_dir, f"{session_id}.json")

            if not os.path.exists(inquiry_file):
                return []

            with self.lock:
                with open(inquiry_file, "r", encoding="utf-8") as f:
                    inquiry_history = json.load(f)

            if limit is not None and limit > 0:
                inquiry_history = inquiry_history[-limit:]

            return inquiry_history

        except Exception as e:
            print(f"Error getting inquiry history: {str(e)}")
            return []

    def save_analysis_report(self, user_id, report_data):
        """保存分析报告

        Args:
            user_id: 用户ID
            report_data: 分析报告数据
        """
        try:
            reports_dir = os.path.join(self.data_dir, "analysis_reports")
            os.makedirs(reports_dir, exist_ok=True)

            # 使用时间戳作为文件名的一部分
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(reports_dir, f"{user_id}_{timestamp}.json")

            # 添加保存时间戳
            report_data["saved_at"] = datetime.now().isoformat()

            with self.lock:
                with open(report_file, "w", encoding="utf-8") as f:
                    json.dump(report_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving analysis report: {str(e)}")

    def get_latest_analysis_report(self, user_id):
        """获取用户最新的分析报告

        Args:
            user_id: 用户ID

        Returns:
            dict: 最新的分析报告数据
        """
        try:
            reports_dir = os.path.join(self.data_dir, "analysis_reports")
            
            if not os.path.exists(reports_dir):
                return {}

            # 获取用户的所有报告文件
            user_reports = []
            for filename in os.listdir(reports_dir):
                if filename.startswith(f"{user_id}_") and filename.endswith(".json"):
                    user_reports.append(filename)

            if not user_reports:
                return {}

            # 按时间戳排序，获取最新的
            user_reports.sort(reverse=True)
            latest_report_file = os.path.join(reports_dir, user_reports[0])

            with self.lock:
                with open(latest_report_file, "r", encoding="utf-8") as f:
                    return json.load(f)

        except Exception as e:
            print(f"Error getting latest analysis report: {str(e)}")
            return {}

    def get_analysis_reports_history(self, user_id, limit=None):
        """获取用户的分析报告历史

        Args:
            user_id: 用户ID
            limit: 获取的报告数量限制

        Returns:
            list: 分析报告历史列表
        """
        try:
            reports_dir = os.path.join(self.data_dir, "analysis_reports")
            
            if not os.path.exists(reports_dir):
                return []

            # 获取用户的所有报告文件
            user_reports = []
            for filename in os.listdir(reports_dir):
                if filename.startswith(f"{user_id}_") and filename.endswith(".json"):
                    user_reports.append(filename)

            if not user_reports:
                return []

            # 按时间戳排序（最新的在前）
            user_reports.sort(reverse=True)

            if limit is not None and limit > 0:
                user_reports = user_reports[:limit]

            # 读取报告数据
            reports = []
            for filename in user_reports:
                try:
                    report_file = os.path.join(reports_dir, filename)
                    with self.lock:
                        with open(report_file, "r", encoding="utf-8") as f:
                            report_data = json.load(f)
                            reports.append(report_data)
                except Exception as e:
                    print(f"Error reading report file {filename}: {str(e)}")
                    continue

            return reports

        except Exception as e:
            print(f"Error getting analysis reports history: {str(e)}")
            return []
