#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
意图识别和路由器
"""

import json
import logging
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class RouteType(Enum):
    """路由类型"""
    DIRECT_CHAT = "direct_chat"          # 直接聊天
    RAG_ENHANCED = "rag_enhanced"        # RAG增强聊天
    WEB_SEARCH = "web_search"            # 网络搜索
    CRISIS_INTERVENTION = "crisis"       # 危机干预


@dataclass
class IntentResult:
    """意图识别结果"""
    route_type: RouteType
    confidence: float
    reason: str
    rag_needed: bool = False
    web_search_needed: bool = False
    crisis_detected: bool = False
    search_keywords: Optional[List[str]] = None


class IntentRouter:
    """意图识别路由器"""
    
    def __init__(self, llm: ChatOpenAI = None):
        """
        初始化意图路由器
        
        Args:
            llm: ChatOpenAI实例
        """
        if llm is None:
            # 使用项目配置创建LLM客户端
            import os
            self.llm = ChatOpenAI(
                model=os.environ.get("MODEL_NAME", "deepseek-chat"),
                temperature=float(os.environ.get("TEMPERATURE", "0.1")),
                api_key=os.environ.get("OPENAI_API_KEY"),
                base_url=os.environ.get("BASE_URL", "https://api.deepseek.com/v1"),
                max_tokens=int(os.environ.get("MAX_TOKENS", "1000"))
            )
        else:
            self.llm = llm
        
        # 系统提示词
        self.system_prompt = """你是一个心理咨询对话系统的意图识别模块。你需要分析用户消息，判断应该使用什么样的处理策略。

请分析用户消息并返回JSON格式的结果，包含以下字段：
- route_type: 路由类型 (direct_chat/rag_enhanced/web_search/crisis)
- confidence: 置信度 (0.0-1.0)
- reason: 判断理由
- rag_needed: 是否需要检索专业知识 (true/false)
- web_search_needed: 是否需要网络搜索 (true/false)
- crisis_detected: 是否检测到危机情况 (true/false)
- search_keywords: 搜索关键词列表（如果需要搜索）

判断规则：
1. **危机干预 (crisis)**: 用户表达自杀、自伤意图，或极度绝望情绪
2. **RAG增强 (rag_enhanced)**: 用户咨询专业心理学概念、治疗方法、症状诊断等
3. **网络搜索 (web_search)**: 用户询问最新信息、新闻事件、具体机构信息等
4. **直接聊天 (direct_chat)**: 一般性情感支持、日常交流、简单安慰等

示例：
用户: "我最近总是失眠，这是抑郁症的症状吗？"
返回: {"route_type": "rag_enhanced", "confidence": 0.9, "reason": "询问抑郁症症状，需要专业知识", "rag_needed": true, "web_search_needed": false, "crisis_detected": false, "search_keywords": ["抑郁症", "失眠", "症状"]}

用户: "我想结束这一切，活着太痛苦了"
返回: {"route_type": "crisis", "confidence": 0.95, "reason": "表达结束生命意图", "rag_needed": false, "web_search_needed": false, "crisis_detected": true, "search_keywords": null}

用户: "今天心情不太好，想找人聊聊"
返回: {"route_type": "direct_chat", "confidence": 0.8, "reason": "一般性情感支持需求", "rag_needed": false, "web_search_needed": false, "crisis_detected": false, "search_keywords": null}"""
    
    def analyze_intent(self, 
                      user_message: str, 
                      conversation_history: List[Dict[str, str]] = None) -> IntentResult:
        """
        分析用户意图
        
        Args:
            user_message: 用户消息
            conversation_history: 对话历史
            
        Returns:
            意图识别结果
        """
        try:
            # 构建上下文信息
            context = ""
            if conversation_history:
                # 取最近几轮对话作为上下文
                recent_history = conversation_history[-4:]  # 最近2轮对话
                context_lines = []
                for msg in recent_history:
                    role = "用户" if msg.get("role") == "user" else "助手"
                    content = msg.get("content", "")
                    context_lines.append(f"{role}: {content}")
                context = "\n".join(context_lines)
            
            # 构建分析消息
            analysis_prompt = f"""请分析以下用户消息的意图：

对话上下文：
{context}

当前用户消息：
{user_message}

请返回JSON格式的分析结果。"""
            
            # 调用LLM进行意图识别
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # 解析JSON响应
            response_text = response.content.strip()
            
            # 尝试提取JSON
            try:
                # 如果响应包含代码块，提取其中的JSON
                if "```json" in response_text:
                    start = response_text.find("```json") + 7
                    end = response_text.find("```", start)
                    json_text = response_text[start:end].strip()
                elif "```" in response_text:
                    start = response_text.find("```") + 3
                    end = response_text.find("```", start)
                    json_text = response_text[start:end].strip()
                else:
                    json_text = response_text
                
                result_data = json.loads(json_text)
                
            except json.JSONDecodeError:
                logger.warning(f"无法解析LLM响应为JSON: {response_text}")
                # 使用默认值
                result_data = {
                    "route_type": "direct_chat",
                    "confidence": 0.5,
                    "reason": "JSON解析失败，使用默认路由",
                    "rag_needed": False,
                    "web_search_needed": False,
                    "crisis_detected": False,
                    "search_keywords": None
                }
            
            # 构建结果对象
            route_type = RouteType(result_data.get("route_type", "direct_chat"))
            
            result = IntentResult(
                route_type=route_type,
                confidence=float(result_data.get("confidence", 0.5)),
                reason=result_data.get("reason", ""),
                rag_needed=bool(result_data.get("rag_needed", False)),
                web_search_needed=bool(result_data.get("web_search_needed", False)),
                crisis_detected=bool(result_data.get("crisis_detected", False)),
                search_keywords=result_data.get("search_keywords")
            )
            
            logger.debug(f"意图识别结果: {route_type.value}, 置信度: {result.confidence}")
            return result
            
        except Exception as e:
            logger.error(f"意图识别失败: {e}")
            # 返回默认结果
            return IntentResult(
                route_type=RouteType.DIRECT_CHAT,
                confidence=0.3,
                reason=f"意图识别异常: {str(e)}",
                rag_needed=False,
                web_search_needed=False,
                crisis_detected=False
            )
    
    def simple_keyword_analysis(self, user_message: str) -> IntentResult:
        """
        简单的基于关键词的意图识别（作为备选方案）
        
        Args:
            user_message: 用户消息
            
        Returns:
            意图识别结果
        """
        message_lower = user_message.lower()
        
        # 危机关键词
        crisis_keywords = {
            "自杀", "想死", "活不下去", "结束生命", "不想活", "轻生", 
            "结束一切", "解脱", "痛苦得想死"
        }
        
        # RAG相关关键词
        rag_keywords = {
            "抑郁症", "焦虑症", "治疗", "心理咨询", "心理医生", "药物",
            "认知行为疗法", "心理治疗", "症状", "诊断", "CBT", "PTSD",
            "强迫症", "恐慌症", "双相", "精神", "心理健康", "咨询师"
        }
        
        # 网络搜索关键词
        web_keywords = {
            "医院", "挂号", "预约", "地址", "电话", "最新", "新闻",
            "政策", "费用", "价格", "开放时间", "营业时间"
        }
        
        # 检查危机
        for keyword in crisis_keywords:
            if keyword in message_lower:
                return IntentResult(
                    route_type=RouteType.CRISIS_INTERVENTION,
                    confidence=0.9,
                    reason=f"检测到危机关键词: {keyword}",
                    crisis_detected=True
                )
        
        # 检查RAG需求
        for keyword in rag_keywords:
            if keyword in message_lower:
                return IntentResult(
                    route_type=RouteType.RAG_ENHANCED,
                    confidence=0.8,
                    reason=f"检测到专业术语: {keyword}",
                    rag_needed=True,
                    search_keywords=[keyword]
                )
        
        # 检查网络搜索需求
        for keyword in web_keywords:
            if keyword in message_lower:
                return IntentResult(
                    route_type=RouteType.WEB_SEARCH,
                    confidence=0.7,
                    reason=f"检测到搜索需求: {keyword}",
                    web_search_needed=True,
                    search_keywords=[keyword]
                )
        
        # 默认直接聊天
        return IntentResult(
            route_type=RouteType.DIRECT_CHAT,
            confidence=0.6,
            reason="无特殊需求，进行常规对话",
            rag_needed=False,
            web_search_needed=False,
            crisis_detected=False
        )
    
    def get_routing_decision(self, user_message: str, context: str = "") -> Dict[str, Any]:
        """
        获取路由决策（为兼容性提供的方法）
        
        Args:
            user_message: 用户消息
            context: 对话上下文
            
        Returns:
            包含意图和路由决策的字典
        """
        try:
            result = self.analyze_intent(user_message)
            
            # 映射路由类型
            route_mapping = {
                RouteType.DIRECT_CHAT: "direct_chat",
                RouteType.RAG_ENHANCED: "rag",
                RouteType.WEB_SEARCH: "web_search",
                RouteType.CRISIS_INTERVENTION: "crisis"
            }
            
            return {
                "intent": {
                    "route_type": result.route_type.value,
                    "confidence": result.confidence,
                    "reason": result.reason,
                    "rag_needed": result.rag_needed,
                    "web_search_needed": result.web_search_needed,
                    "crisis_detected": result.crisis_detected,
                    "search_keywords": result.search_keywords
                },
                "route": route_mapping.get(result.route_type, "direct_chat")
            }
        except Exception as e:
            logger.error(f"路由决策失败: {e}")
            return {
                "intent": {
                    "route_type": "direct_chat",
                    "confidence": 0.3,
                    "reason": f"路由异常: {str(e)}",
                    "rag_needed": False,
                    "web_search_needed": False,
                    "crisis_detected": False,
                    "search_keywords": None
                },
                "route": "direct_chat"
            }


class SimpleIntentRouter:
    """简化的意图路由器（备用方案）"""
    
    def __init__(self):
        self.rag_keywords = {
            "抑郁症", "焦虑症", "治疗", "心理咨询", "心理医生", "药物",
            "认知行为疗法", "心理治疗", "症状", "诊断", "CBT", "PTSD",
            "强迫症", "恐慌症", "双相", "精神", "心理健康", "咨询师"
        }
        
        self.web_keywords = {
            "医院", "挂号", "预约", "地址", "电话", "最新", "新闻",
            "政策", "费用", "价格", "开放时间", "营业时间"
        }
    
    def should_use_rag(self, message: str) -> bool:
        """判断是否需要使用RAG"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.rag_keywords)
    
    def should_use_web_search(self, message: str) -> bool:
        """判断是否需要网络搜索"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.web_keywords)
