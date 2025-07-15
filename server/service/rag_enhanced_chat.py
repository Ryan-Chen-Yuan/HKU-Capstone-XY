#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG增强聊天服务 v2
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from service.chat_langgraph_optimized import optimized_chat

logger = logging.getLogger(__name__)


def optimized_chat_with_rag(
    user_input: str,
    user_id: str = "default_user",
    session_id: str = None,
    history: List[Dict[str, str]] = None,
    enable_performance_monitoring: bool = False
) -> Dict[str, Any]:
    """
    RAG增强的优化聊天函数
    
    Args:
        user_input: 用户输入
        user_id: 用户ID
        session_id: 会话ID
        history: 对话历史
        enable_performance_monitoring: 是否启用性能监控
        
    Returns:
        包含回复信息的字典
    """
    try:
        # 直接调用基础的优化聊天函数，它已经集成了RAG功能
        response = optimized_chat(
            user_input=user_input,
            user_id=user_id,
            session_id=session_id,
            history=history,  # 传递历史记录
            enable_performance_monitoring=enable_performance_monitoring
        )
        
        # 返回标准格式的响应
        return {
            "response": response.get("response", ""),
            "emotion": response.get("emotion", "neutral"),
            "crisis_detected": response.get("crisis_detected", False),
            "search_results": response.get("search_results"),
            "rag_context": response.get("rag_context"),
            "processing_time": response.get("performance", {}).get("total_time", 0)
        }
        
    except Exception as e:
        logger.error(f"RAG增强聊天处理失败: {e}")
        return {
            "response": "抱歉，系统暂时遇到了问题。请稍后再试。",
            "emotion": "neutral",
            "crisis_detected": False,
            "search_results": None,
            "rag_context": None,
            "processing_time": 0
        }
