#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LangGraph节点 - RAG和Web搜索节点
"""

import logging
import requests
from typing import Dict, List, Any, Optional

from .core.rag_service import RAGCoreService
from .intent_router import IntentRouter, IntentResult, RouteType

logger = logging.getLogger(__name__)


def create_intent_analysis_node(intent_router: IntentRouter):
    """创建意图分析节点"""
    
    def intent_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        意图分析节点 - 判断是否需要RAG或网络搜索
        
        Args:
            state: 状态字典，包含user_input, history等
            
        Returns:
            更新后的状态字典
        """
        user_input = state.get("user_input", "")
        history = state.get("history", [])
        
        logger.info(f"开始意图分析: {user_input[:50]}...")
        
        try:
            # 使用意图路由器分析
            intent_result = intent_router.analyze_intent(user_input, history)
            
            # 更新状态
            state.update({
                "intent_result": {
                    "route_type": intent_result.route_type.value,
                    "confidence": intent_result.confidence,
                    "reason": intent_result.reason,
                    "rag_needed": intent_result.rag_needed,
                    "web_search_needed": intent_result.web_search_needed,
                    "crisis_detected": intent_result.crisis_detected,
                    "search_keywords": intent_result.search_keywords
                },
                "need_rag": intent_result.rag_needed,
                "need_web_search": intent_result.web_search_needed,
                "crisis_detected": intent_result.crisis_detected,
                "route_decision": intent_result.route_type.value
            })
            
            logger.info(f"意图分析完成: {intent_result.route_type.value} (置信度: {intent_result.confidence:.2f})")
            
        except Exception as e:
            logger.error(f"意图分析失败: {e}")
            # 设置默认值
            state.update({
                "intent_result": {
                    "route_type": "direct_chat",
                    "confidence": 0.3,
                    "reason": f"意图分析异常: {str(e)}",
                    "rag_needed": False,
                    "web_search_needed": False,
                    "crisis_detected": False,
                    "search_keywords": None
                },
                "need_rag": False,
                "need_web_search": False,
                "crisis_detected": False,
                "route_decision": "direct_chat"
            })
        
        return state
    
    return intent_analysis_node


def create_rag_node(rag_service: RAGCoreService, top_k: int = 3):
    """创建RAG检索节点"""
    
    def rag_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        RAG检索节点 - 检索相关专业知识
        
        Args:
            state: 状态字典
            
        Returns:
            更新后的状态字典
        """
        user_input = state.get("user_input", "")
        need_rag = state.get("need_rag", False)
        
        if not need_rag:
            logger.debug("跳过RAG检索")
            state.update({
                "rag_context": "",
                "has_rag_context": False
            })
            return state
        
        logger.info(f"开始RAG检索: {user_input[:50]}...")
        
        try:
            if not rag_service.is_initialized:
                logger.warning("RAG服务未初始化")
                state.update({
                    "rag_context": "",
                    "has_rag_context": False
                })
                return state
            
            # 执行RAG检索
            context = rag_service.get_context_for_query(
                user_input, 
                top_k=top_k, 
                use_rerank=True
            )
            
            if context.strip():
                logger.info(f"RAG检索成功，获得 {len(context)} 字符的上下文")
                state.update({
                    "rag_context": context,
                    "has_rag_context": True
                })
            else:
                logger.warning("RAG检索未找到相关内容")
                state.update({
                    "rag_context": "",
                    "has_rag_context": False
                })
                
        except Exception as e:
            logger.error(f"RAG检索失败: {e}")
            state.update({
                "rag_context": "",
                "has_rag_context": False
            })
        
        return state
    
    return rag_node


def create_web_search_node(search_enabled: bool = False):
    """创建网络搜索节点"""
    
    def web_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        网络搜索节点 - 搜索最新信息
        
        Args:
            state: 状态字典
            
        Returns:
            更新后的状态字典
        """
        user_input = state.get("user_input", "")
        need_web_search = state.get("need_web_search", False)
        search_keywords = state.get("intent_result", {}).get("search_keywords", [])
        
        if not need_web_search or not search_enabled:
            logger.debug("跳过网络搜索")
            state.update({
                "search_results": "",
                "has_search_results": False
            })
            return state
        
        logger.info(f"开始网络搜索: {user_input[:50]}...")
        
        try:
            # 构建搜索查询
            if search_keywords:
                query = " ".join(search_keywords)
            else:
                query = user_input
            
            # 这里可以集成实际的搜索API，如DuckDuckGo、Bing等
            # 目前先返回模拟结果
            search_results = f"搜索查询: {query}\n[网络搜索功能暂未实现，请联系系统管理员获取最新信息]"
            
            logger.info(f"网络搜索完成: {query}")
            state.update({
                "search_results": search_results,
                "has_search_results": True
            })
            
        except Exception as e:
            logger.error(f"网络搜索失败: {e}")
            state.update({
                "search_results": "",
                "has_search_results": False
            })
        
        return state
    
    return web_search_node


def create_context_enrichment_node():
    """创建上下文增强节点"""
    
    def context_enrichment_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        上下文增强节点 - 整合RAG和搜索结果
        
        Args:
            state: 状态字典
            
        Returns:
            更新后的状态字典
        """
        user_input = state.get("user_input", "")
        rag_context = state.get("rag_context", "")
        search_results = state.get("search_results", "")
        has_rag_context = state.get("has_rag_context", False)
        has_search_results = state.get("has_search_results", False)
        
        # 构建增强上下文
        enhanced_context_parts = []
        
        if has_rag_context and rag_context.strip():
            enhanced_context_parts.append("【专业知识参考】")
            enhanced_context_parts.append(rag_context)
            enhanced_context_parts.append("")
        
        if has_search_results and search_results.strip():
            enhanced_context_parts.append("【搜索结果】")
            enhanced_context_parts.append(search_results)
            enhanced_context_parts.append("")
        
        enhanced_context = "\n".join(enhanced_context_parts)
        
        # 更新状态
        state.update({
            "enhanced_context": enhanced_context,
            "has_enhanced_context": bool(enhanced_context.strip())
        })
        
        if enhanced_context.strip():
            logger.info(f"上下文增强完成，总长度: {len(enhanced_context)} 字符")
        else:
            logger.debug("无需上下文增强")
        
        return state
    
    return context_enrichment_node


def create_route_decision_node():
    """创建路由决策节点"""
    
    def route_decision_node(state: Dict[str, Any]) -> str:
        """
        路由决策节点 - 决定下一步处理路径
        
        Args:
            state: 状态字典
            
        Returns:
            下一个节点名称
        """
        route_decision = state.get("route_decision", "direct_chat")
        crisis_detected = state.get("crisis_detected", False)
        
        # 危机情况优先处理
        if crisis_detected:
            logger.info("检测到危机情况，路由到危机干预")
            return "crisis_intervention"
        
        # 根据意图路由
        if route_decision == "rag_enhanced":
            logger.info("路由到RAG增强聊天")
            return "rag_enhanced_chat"
        elif route_decision == "web_search":
            logger.info("路由到网络搜索聊天")
            return "web_search_chat"
        else:
            logger.info("路由到直接聊天")
            return "direct_chat"
    
    return route_decision_node
