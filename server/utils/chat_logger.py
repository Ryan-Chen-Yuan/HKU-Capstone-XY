#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务端日志工具模块
提供可配置的聊天和情绪分析日志记录功能
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from snownlp import SnowNLP


class ChatLogger:
    """聊天日志记录器"""
    
    def __init__(self):
        self.chat_logging_enabled = os.environ.get("ENABLE_CHAT_LOGGING", "true").lower() == "true"
        self.emotion_logging_enabled = os.environ.get("ENABLE_EMOTION_LOGGING", "true").lower() == "true"
        self.detailed_logging_enabled = os.environ.get("ENABLE_DETAILED_LOGGING", "true").lower() == "true"
    
    def log_chat_request(self, user_id: str, session_id: str, message: str, timestamp: str = None):
        """记录聊天请求"""
        if not self.chat_logging_enabled:
            return
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 基础日志信息
        log_info = [
            f"🗣️  用户消息 [{timestamp}]",
            f"   用户ID: {user_id}",
            f"   会话ID: {session_id}",
            f"   消息: {message}"
        ]
        
        # 情绪分析
        if self.emotion_logging_enabled:
            emotion_score = SnowNLP(message).sentiments * 2 - 1
            emotion_category = self._classify_emotion(emotion_score, message)
            
            log_info.extend([
                f"   情绪评分: {emotion_score:.3f} ({self._get_emotion_description(emotion_score)})",
                f"   情绪分类: {emotion_category}"
            ])
        
        # 详细信息
        if self.detailed_logging_enabled:
            log_info.extend([
                f"   消息长度: {len(message)} 字符",
                f"   包含数字: {'是' if any(c.isdigit() for c in message) else '否'}",
                f"   包含标点: {'是' if any(c in '！？。，；：' for c in message) else '否'}"
            ])
        
        print("\n".join(log_info))
        # 不在这里打印分隔符，让后续的情绪分析紧跟其后
    
    def log_chat_response(self, user_id: str, session_id: str, response: str, emotion: str = None, 
                         crisis_detected: bool = False, search_results: str = None, timestamp: str = None):
        """记录聊天响应"""
        if not self.chat_logging_enabled:
            return
        
        if timestamp is None:
            # 使用与情绪分析一致的时间格式
            response_timestamp = datetime.now().isoformat()
        else:
            response_timestamp = timestamp
        
        # 基础日志信息
        log_info = [
            f"🤖 AI回复 [{response_timestamp}]",
            f"   用户ID: {user_id}",
            f"   会话ID: {session_id}",
            f"   回复: {response[:100]}{'...' if len(response) > 100 else ''}"
        ]
        
        # 情绪和危机信息
        if emotion:
            log_info.append(f"   检测情绪: {emotion}")
        
        if crisis_detected:
            log_info.append(f"   ⚠️  危机检测: 是")
        
        # 搜索结果信息
        if search_results:
            search_summary = search_results[:80] + "..." if len(search_results) > 80 else search_results
            log_info.append(f"   🔍 搜索结果: {search_summary}")
        else:
            log_info.append(f"   🔍 搜索结果: 未进行")
        
        # 详细信息
        if self.detailed_logging_enabled:
            log_info.extend([
                f"   回复长度: {len(response)} 字符",
                f"   生成时间: {response_timestamp}"
            ])
        
        print("\n".join(log_info))
        print("-" * 50)
    
    def log_mood_analysis(self, user_id: str, session_id: str, messages: List[str], 
                         mood_result: Dict[str, Any], timestamp: str = None, suppress_header: bool = False):
        """记录情绪分析结果"""
        if not self.emotion_logging_enabled:
            return
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 如果suppress_header为True，表示这是聊天流程的一部分，不需要额外的分隔符
        if not suppress_header:
            print("")  # 空行分隔
        
        log_info = [
            f"💭 情绪分析 [{timestamp}]",
            f"   用户ID: {user_id}",
            f"   会话ID: {session_id}",
            f"   分析消息数: {len(messages)}",
            f"   情绪强度: {mood_result.get('moodIntensity', 'N/A')}",
            f"   情绪类别: {mood_result.get('moodCategory', 'N/A')}",
            f"   内心独白: {mood_result.get('thinking', 'N/A')}",
            f"   情绪场景: {mood_result.get('scene', 'N/A')}"
        ]
        
        if self.detailed_logging_enabled:
            log_info.extend([
                f"   消息内容: {', '.join(msg[:20] + '...' if len(msg) > 20 else msg for msg in messages)}"
            ])
        
        print("\n".join(log_info))
        print("-" * 50)
    
    def log_system_event(self, event_type: str, message: str, details: Dict[str, Any] = None):
        """记录系统事件"""
        if not self.detailed_logging_enabled:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_info = [
            f"⚙️  系统事件 [{timestamp}]",
            f"   事件类型: {event_type}",
            f"   消息: {message}"
        ]
        
        if details:
            for key, value in details.items():
                log_info.append(f"   {key}: {value}")
        
        print("\n".join(log_info))
        print("-" * 50)
    
    def _classify_emotion(self, score: float, message: str) -> str:
        """分类情绪"""
        # 关键词检测
        message_lower = message.lower()
        if any(word in message_lower for word in ["开心", "高兴", "快乐", "很好", "很棒", "兴奋"]):
            return "积极"
        elif any(word in message_lower for word in ["悲伤", "难过", "伤心", "痛苦", "抑郁"]):
            return "消极"
        elif any(word in message_lower for word in ["生气", "愤怒", "恼火", "烦躁", "烦恼"]):
            return "愤怒"
        elif any(word in message_lower for word in ["累了", "疲惫", "困", "睡觉", "休息"]):
            return "疲惫"
        
        # 基于分数分类
        if score > 0.1:
            return "积极"
        elif score < -0.1:
            return "消极"
        else:
            return "中性"
    
    def _get_emotion_description(self, score: float) -> str:
        """获取情绪描述"""
        if score > 0.5:
            return "非常积极"
        elif score > 0.1:
            return "积极"
        elif score > -0.1:
            return "中性"
        elif score > -0.5:
            return "消极"
        else:
            return "非常消极"
    
    def log_statistics(self, session_id: str, stats: Dict[str, Any]):
        """记录统计信息"""
        if not self.detailed_logging_enabled:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_info = [
            f"📊 会话统计 [{timestamp}]",
            f"   会话ID: {session_id}",
            f"   消息总数: {stats.get('total_messages', 0)}",
            f"   平均情绪分: {stats.get('avg_emotion_score', 0):.3f}",
            f"   危机检测次数: {stats.get('crisis_count', 0)}",
            f"   会话时长: {stats.get('session_duration', 'N/A')}"
        ]
        
        print("\n".join(log_info))
        print("=" * 50)
    
    def log_chat(self, user_id: str, session_id: str, user_message: str, ai_response: str, 
                 emotion: str = None, crisis_detected: bool = False, timestamp: str = None, 
                 processing_time: float = 0, search_results: str = None):
        """统一记录聊天对话日志（仅记录AI响应）"""
        if not self.chat_logging_enabled:
            return
        
        # 记录AI响应
        self.log_chat_response(user_id, session_id, ai_response, emotion, crisis_detected, search_results, timestamp)
        
        # 如果启用详细日志，记录处理时间
        if self.detailed_logging_enabled and processing_time > 0:
            print(f"⏱️  处理时间: {processing_time:.3f}秒")
            print("-" * 50)
    
    def log_user_message_start(self, user_id: str, session_id: str, user_message: str, timestamp: str = None):
        """记录用户消息（聊天开始时调用）"""
        if not self.chat_logging_enabled:
            return
        
        # 记录用户请求（包含NLP情绪分析）
        self.log_chat_request(user_id, session_id, user_message, timestamp)


# 创建全局日志记录器实例
chat_logger = ChatLogger()
