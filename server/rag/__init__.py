#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG模块

提供检索增强生成(RAG)功能，包括：
- 知识库文件扫描和处理
- 基于Qwen模型的向量存储和检索
- 意图识别和路由
- LangGraph节点集成
"""

from .core.knowledge_scanner import KnowledgeScanner
from .core.qwen_vector_store import QwenVectorStore
from .core.rag_retriever import RAGRetriever
from .core.rag_service import RAGCoreService

from .intent_router import IntentRouter, RouteType, IntentResult, SimpleIntentRouter
from .langgraph_nodes import (
    create_intent_analysis_node,
    create_rag_node, 
    create_web_search_node,
    create_context_enrichment_node,
    create_route_decision_node
)

# 兼容性支持
try:
    from .knowledge_manager import KnowledgeManager
except ImportError:
    KnowledgeManager = None

# 为向后兼容，提供简化的导入
RAGService = RAGCoreService

__all__ = [
    # 核心组件
    "KnowledgeScanner",
    "QwenVectorStore", 
    "RAGRetriever",
    "RAGCoreService",
    "RAGService",  # 别名
    
    # 意图识别
    "IntentRouter",
    "SimpleIntentRouter",
    "RouteType", 
    "IntentResult",
    
    # 知识管理
    "KnowledgeManager",
    
    # LangGraph节点
    "create_intent_analysis_node",
    "create_rag_node",
    "create_web_search_node", 
    "create_context_enrichment_node",
    "create_route_decision_node"
]
