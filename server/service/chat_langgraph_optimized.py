#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
心理咨询对话系统 - LangGraph优化版本

该版本将对话流程拆分为多个独立的节点，通过LangGraph进行编排：
1. 输入预处理节点
2. 危机检测节点
3. 上下文构建节点
4. 搜索节点（可选）
5. 计划更新节点
6. LLM响应节点
7. 后处理节点
8. 数据保存节点

优化点：
- 并行处理非依赖操作
- 条件路由减少不必要的计算
- 优化数据库操作批次
- 异步处理搜索功能
"""

import os
import json
import sys
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Any, Optional

sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
import re
import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from snownlp import SnowNLP

from utils.extract_json import extract_json
from dao.database import Database
from service.analysis_report_service import AnalysisReportService

import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# 加载环境变量
load_dotenv()


# 扩展的会话状态数据模型
class OptimizedSessionState(BaseModel):
    # 基本信息
    user_input: str
    user_id: str = "default_user"
    session_id: str | None = None

    # 响应相关
    response: str | None = None
    emotion: str = "neutral"

    # 历史记录
    history: List[Dict[str, str]] = Field(default_factory=list)

    # 用户画像和上下文
    user_profile: Dict[str, Any] = Field(default_factory=dict)
    memory_context: str = ""

    # 危机检测
    crisis_detected: bool = False
    crisis_reason: str | None = None

    # 搜索相关
    need_search: bool = False
    search_results: str | None = None

    # 计划和分析
    plan: Dict[str, Any] = Field(default_factory=dict)
    pattern_analysis: Dict[str, Any] | None = None
    
    # 引导性询问
    inquiry_result: Dict[str, Any] | None = None
    need_guided_inquiry: bool = False
    
    # 模式分析
    need_pattern_analysis: bool = False
    
    # 分析报告
    need_analysis_report: bool = False
    analysis_report: Dict[str, Any] | None = None

    # 处理状态
    processing_stage: str = "init"
    skip_search: bool = False
    skip_plan_update: bool = False

    # 性能监控
    stage_timings: Dict[str, float] = Field(default_factory=dict)
    total_start_time: float = 0.0


# 优化的危机检测器
class OptimizedCrisisDetector:
    def __init__(self):
        self._keywords = {
            "high_risk": {"自杀", "想死", "活不下去", "结束生命", "杀人", "伤害自己"},
            "medium_risk": {"受不了", "绝望", "崩溃", "痛苦", "没有希望"},
        }
        self._sentiment_threshold = -0.3
        self._cache = {}  # 简单的结果缓存

    def check(self, text: str) -> Tuple[bool, str | None, str]:
        """
        检测危机程度
        返回：(是否危机, 原因, 严重程度)
        """
        if text in self._cache:
            return self._cache[text]

        # 检查高风险关键词
        for keyword in self._keywords["high_risk"]:
            if keyword in text:
                result = (True, f"检测到高危词: '{keyword}'", "high")
                self._cache[text] = result
                return result

        # 检查中风险关键词
        for keyword in self._keywords["medium_risk"]:
            if keyword in text:
                result = (True, f"检测到中危词: '{keyword}'", "medium")
                self._cache[text] = result
                return result

        # 情感分析
        # try:
        #     polarity = SnowNLP(text).sentiments * 2 - 1
        #     if polarity <= self._sentiment_threshold:
        #         result = (True, f"情感极性过低 (polarity={polarity:.2f})", "low")
        #         self._cache[text] = result
        #         return result
        # except Exception:
        #     pass

        result = (False, None, "none")
        self._cache[text] = result
        return result


# 优化的搜索服务
class OptimizedSearchService:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        self.search_triggers = [
            "什么是",
            "如何",
            "为什么",
            "怎么办",
            "最新",
            "现在",
            "今天",
            "新闻",
            "天气",
            "查询",
            "搜索",
        ]
        self.timeout = 8  # 减少超时时间
        self.max_results = 3

    def should_search(self, text: str) -> bool:
        """判断是否需要搜索"""
        return any(trigger in text for trigger in self.search_triggers)

    async def search_async(self, query: str) -> str:
        """异步搜索"""
        if not self.api_key:
            return "⚠️ [搜索功能未启用: 未设置 SERPAPI_KEY]"

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._sync_search, query)
            return result
        except Exception as e:
            return f"搜索出错: {e}"

    def _sync_search(self, query: str) -> str:
        """同步搜索实现"""
        try:
            r = requests.get(
                "https://serpapi.com/search",
                params={
                    "q": query,
                    "api_key": self.api_key,
                    "hl": "zh-cn",
                    "num": self.max_results,
                },
                timeout=self.timeout,
            )
            r.raise_for_status()
            data = r.json()

            snippets = []
            for item in data.get("organic_results", [])[: self.max_results]:
                snippets.append(
                    f"标题: {item.get('title', '').strip()}\n"
                    f"摘要: {item.get('snippet', '').strip()}\n"
                    f"链接: {item.get('link', '').strip()}"
                )

            return "\n\n".join(snippets) if snippets else "未找到相关搜索结果"
        except Exception as e:
            return f"搜索出错: {e}"


# 优化的聊天服务
class OptimizedChatService:
    def __init__(self, database: Database):
        self.db = database
        self.model = os.environ.get("MODEL_NAME", "deepseek-chat")
        self.client = ChatOpenAI(
            model=self.model,
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("BASE_URL", "https://api.deepseek.com/v1"),
            temperature=float(os.environ.get("TEMPERATURE", "0.7")),
            max_tokens=int(os.environ.get("MAX_TOKENS", "1000")),
            timeout=30,  # 减少超时时间
        )

        self.enable_guided_inquiry = (
            os.environ.get("ENABLE_GUIDED_INQUIRY", "true").lower() == "true"
        )
        self.enable_pattern_analysis = (
            os.environ.get("ENABLE_PATTERN_ANALYSIS", "true").lower() == "true"
        )

        # 加载提示词模板
        self.prompt_template = self._load_prompt_template()
        self.planning_prompt = self._load_planning_prompt()
        self.guided_inquiry_prompt = self._load_guided_inquiry_prompt()
        self.pattern_analysis_prompt = self._load_pattern_analysis_prompt()

        # 创建线程池用于并行处理
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # 初始化分析报告服务
        self.analysis_service = AnalysisReportService()

    def _load_prompt_template(self) -> str:
        """加载咨询师提示词模板"""
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        os.makedirs(prompt_dir, exist_ok=True)
        prompt_file = os.path.join(prompt_dir, "counselor_prompt.txt")

        if not os.path.exists(prompt_file):
            default_prompt = """你是一位专业的心理咨询师，名叫"知己咨询师"。你的目标是通过对话帮助用户解决心理困扰、情绪问题，并提供专业的心理支持。

请注意以下指导原则：
1. 保持共情、尊重和支持的态度
2. 提供循证的心理学建议
3. 不要给出医疗诊断或处方
4. 当用户需要专业医疗帮助时，建议他们寻求专业医生的帮助
5. 回复要简洁、清晰，易于用户理解
6. 适当使用开放式问题鼓励用户表达

示例回复格式：
"我理解你现在的感受。这种情况下，你可以尝试...
希望这些建议对你有所帮助！"
"""
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(default_prompt)
            return default_prompt

        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _load_planning_prompt(self) -> str:
        """加载计划提示词模板"""
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "planning_prompt.txt")

        if not os.path.exists(prompt_file):
            # 创建默认的计划提示词
            default_planning_prompt = """你是一个对话计划分析器。根据用户的输入和历史对话，更新对话计划。

返回JSON格式的计划，包含以下字段：
- user_intent: 用户意图分析
- current_state: 当前对话状态
- steps: 建议的对话步骤
- context: 上下文信息
- inquiry_status: 引导式询问状态

请保持JSON格式的完整性。"""

            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(default_planning_prompt)
            return default_planning_prompt

        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _load_guided_inquiry_prompt(self) -> str:
        """加载引导性询问提示词模板"""
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "guided_inquiry_prompt.txt")

        if not os.path.exists(prompt_file):
            raise FileNotFoundError("Guided inquiry prompt file not found")

        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _load_pattern_analysis_prompt(self) -> str:
        """加载行为模式分析提示词模板"""
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "pattern_analysis_prompt.txt")

        if not os.path.exists(prompt_file):
            raise FileNotFoundError("Pattern analysis prompt file not found")

        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def batch_get_user_data(self, user_id: str) -> Dict[str, Any]:
        """批量获取用户数据"""
        try:
            # 并行获取用户数据
            futures = {
                "profile": self.executor.submit(self.db.get_user_profile, user_id),
                "memory": self.executor.submit(
                    self.db.get_long_term_memory, user_id, 5
                ),
                "emotion_history": self.executor.submit(
                    self.db.get_emotion_history, user_id
                ),
            }

            results = {}
            for key, future in futures.items():
                try:
                    results[key] = future.result(timeout=2)
                except Exception as e:
                    print(f"Error getting {key}: {e}")
                    results[key] = {} if key == "profile" else []

            return results
        except Exception as e:
            print(f"Error in batch_get_user_data: {e}")
            return {"profile": {}, "memory": [], "emotion_history": []}

    def get_session_analysis_data(self, session_id: str) -> Dict[str, Any]:
        """获取会话分析数据（引导性询问和模式分析结果）"""
        try:
            # 并行获取会话分析数据
            futures = {
                "inquiry_result": self.executor.submit(self.db.get_inquiry_result, session_id),
                "pattern_analysis": self.executor.submit(self.db.get_pattern_analysis, session_id),
                "inquiry_history": self.executor.submit(self.db.get_inquiry_history, session_id, 5),
            }

            results = {}
            for key, future in futures.items():
                try:
                    results[key] = future.result(timeout=2)
                except Exception as e:
                    print(f"Error getting {key}: {e}")
                    results[key] = {} if key != "inquiry_history" else []

            return results
        except Exception as e:
            print(f"Error in get_session_analysis_data: {e}")
            return {"inquiry_result": {}, "pattern_analysis": {}, "inquiry_history": []}

    def format_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """格式化记忆上下文"""
        if not memories:
            return ""
        return "\n".join(
            f"{m.get('time', '')}: {m.get('content', '')}" for m in memories
        )

    def extract_emotion(self, content: str) -> Tuple[str, str]:
        """提取情绪信息"""
        # 检查显式情绪标记
        emotion_match = re.search(
            r"#(happy|sad|angry|sleepy|neutral)\b", content, re.IGNORECASE
        )
        if emotion_match:
            emotion = emotion_match.group(1).lower()
            clean_content = re.sub(
                r"\s*#(happy|sad|angry|sleepy|neutral)\b",
                "",
                content,
                flags=re.IGNORECASE,
            )
            return clean_content, emotion

        # 基于关键词的情绪识别
        content_lower = content.lower()
        emotion_keywords = {
            "happy": ["开心", "高兴", "快乐", "很好", "很棒", "兴奋", "满意"],
            "sad": ["悲伤", "难过", "伤心", "痛苦", "抑郁", "失落"],
            "angry": ["生气", "愤怒", "恼火", "烦躁", "烦恼", "不满"],
            "sleepy": ["累了", "疲惫", "困", "睡觉", "休息", "疲劳"],
        }

        for emotion, keywords in emotion_keywords.items():
            if any(word in content_lower for word in keywords):
                return content, emotion

        return content, "neutral"

    def _parse_inquiry_manually(self, text: str) -> Dict[str, Any] | None:
        """手动解析引导性询问结果的备用方法"""
        try:
            # 从文本中提取关键信息
            result = {
                "need_inquiry": True,
                "current_stage": "基础情况了解",
                "missing_info": [],
                "suggested_questions": [],
                "information_completeness": 50,
                "reason": "手动解析结果"
            }
            
            # 查找信息完整度
            completeness_match = re.search(r'信息完整[度性]?[：:]\s*(\d+)%?', text)
            if completeness_match:
                result["information_completeness"] = int(completeness_match.group(1))
            
            # 查找当前阶段
            stage_match = re.search(r'当前阶段[：:]\s*([^\n]+)', text)
            if stage_match:
                result["current_stage"] = stage_match.group(1).strip()
            
            # 查找建议的问题
            questions = re.findall(r'[12]\.?\s*([^？?]*[？?])', text)
            if questions:
                result["suggested_questions"] = [q.strip() for q in questions[:2]]
            
            # 判断是否需要询问
            if result["information_completeness"] >= 80:
                result["need_inquiry"] = False
                result["current_stage"] = "信息充分"
            
            return result
            
        except Exception as e:
            print(f"Manual parsing failed: {e}")
            return None

    def _parse_pattern_manually(self, text: str) -> Dict[str, Any] | None:
        """手动解析行为模式分析结果的备用方法"""
        try:
            # 创建基础的模式分析结构
            pattern_analysis = {
                "pattern_analysis": {
                    "trigger_patterns": {
                        "common_triggers": [],
                        "trigger_intensity": "中",
                        "trigger_frequency": "经常"
                    },
                    "cognitive_patterns": {
                        "thinking_styles": [],
                        "cognitive_biases": [],
                        "core_beliefs": []
                    },
                    "emotional_patterns": {
                        "primary_emotions": [],
                        "emotion_regulation": "部分有效",
                        "emotion_duration": "中等"
                    },
                    "behavioral_patterns": {
                        "coping_strategies": [],
                        "behavior_effectiveness": "部分有效",
                        "behavior_habits": []
                    },
                    "interpersonal_patterns": {
                        "interaction_style": "被动",
                        "support_utilization": "部分",
                        "social_behaviors": []
                    },
                    "resource_patterns": {
                        "personal_strengths": [],
                        "successful_experiences": [],
                        "growth_potential": []
                    }
                },
                "pattern_summary": "基于对话内容进行的手动模式分析",
                "key_insights": ["需要进一步分析", "模式识别中", "持续关注"],
                "consultation_recommendations": ["保持开放沟通", "建立信任关系", "逐步深入了解"]
            }
            
            return pattern_analysis
            
        except Exception as e:
            print(f"Manual pattern parsing failed: {e}")
            return None

    def _assess_information_completeness(self, session_id: str, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """评估信息完整性并生成引导性询问"""
        try:
            # 准备消息历史用于分析
            conversation_context = {
                "current_message": message,
                "history": history,
                "session_id": session_id
            }

            messages = [
                {"role": "system", "content": self.guided_inquiry_prompt},
                {
                    "role": "user",
                    "content": f"请评估以下对话的信息完整性并决定是否需要引导性询问：\n\n{json.dumps(conversation_context, ensure_ascii=False)}"
                }
            ]

            response = self.client.invoke(messages)
            reply = response.content.strip()
            
            # 解析响应
            print(f"Attempting to parse JSON with extract_json...")
            inquiry_result = extract_json(reply)
            print(f"Parse result: {inquiry_result}")
            
            if inquiry_result is None:
                print(f"JSON parser failed. Raw reply length: {len(reply)}")
                print(f"First 500 chars: {repr(reply[:500])}")
                # 尝试手动解析关键信息
                inquiry_result = self._parse_inquiry_manually(reply)
                if inquiry_result is None:
                    return {
                        "need_inquiry": False,
                        "current_stage": "信息充分",
                        "information_completeness": 50,
                        "reason": "分析失败，默认不进行询问"
                    }

            return inquiry_result

        except Exception as e:
            print(f"Error assessing information completeness: {str(e)}")
            return {
                "need_inquiry": False,
                "current_stage": "信息充分",
                "information_completeness": 50,
                "reason": f"分析错误: {str(e)}"
            }

    def _analyze_behavior_pattern(self, session_id: str, collected_info: Dict[str, Any]) -> Dict[str, Any] | None:
        """分析行为模式"""
        try:
            messages = [
                {"role": "system", "content": self.pattern_analysis_prompt},
                {
                    "role": "user",
                    "content": f"请基于以下收集到的信息分析客户的行为模式：\n\n{json.dumps(collected_info, ensure_ascii=False)}"
                }
            ]

            response = self.client.invoke(messages)
            reply = response.content.strip()
            
            # 解析响应
            pattern_analysis = extract_json(reply)
            if pattern_analysis is None:
                print(f"Failed to extract JSON from pattern analysis: {reply}")
                # 尝试手动解析模式分析信息
                pattern_analysis = self._parse_pattern_manually(reply)
                if pattern_analysis is None:
                    return None

            # 添加分析时间戳
            pattern_analysis["analyzed_at"] = datetime.now().isoformat()
            pattern_analysis["session_id"] = session_id

            return pattern_analysis

        except Exception as e:
            print(f"Error analyzing behavior pattern: {str(e)}")
            return None


# 初始化服务
db = Database()
crisis_detector = OptimizedCrisisDetector()
search_service = OptimizedSearchService()
chat_service = OptimizedChatService(db)

# === LangGraph 节点函数 ===


def preprocess_input(state: OptimizedSessionState) -> OptimizedSessionState:
    """输入预处理节点"""
    start_time = datetime.now().timestamp()
    state.total_start_time = start_time

    # 基本信息设置
    state.user_input = state.user_input.strip()
    state.session_id = state.session_id or state.user_id
    state.processing_stage = "preprocessed"

    # 判断是否需要搜索
    state.need_search = search_service.should_search(state.user_input)
    
    # 检测是否需要生成分析报告
    analysis_keywords = ["知己报告", "生成报告", "分析报告", "心理分析", "综合分析", "个人报告", "健康报告", "心理报告", "总结报告", "评估报告"]
    state.need_analysis_report = any(keyword in state.user_input for keyword in analysis_keywords)

    # 记录时间
    state.stage_timings["preprocess"] = datetime.now().timestamp() - start_time

    return state


def detect_crisis(state: OptimizedSessionState) -> OptimizedSessionState:
    """危机检测节点"""
    start_time = datetime.now().timestamp()

    crisis, reason, severity = crisis_detector.check(state.user_input)
    state.crisis_detected = crisis
    state.crisis_reason = reason

    if crisis:
        # 根据严重程度生成不同的响应
        if severity == "high":
            state.response = (
                f"⚠️ 检测到高危情绪危机: {reason}\n\n"
                "请立即联系专业人士或拨打心理援助热线 400-161-9995。\n"
                "您的生命很宝贵，请寻求帮助。我们关心您。"
            )
        elif severity == "medium":
            state.response = (
                f"⚠️ 检测到情绪困扰: {reason}\n\n"
                "我理解您现在的感受很困难。让我们一起面对这个挑战。\n"
                "如果需要，也可以联系专业心理援助热线 400-161-9995。"
            )
        else:
            state.response = (
                f"我注意到您可能情绪不太好: {reason}\n\n"
                "我在这里陪伴您，让我们一起聊聊吧。"
            )

        state.processing_stage = "crisis_handled"
        # 保存危机记录
        chat_service.db.save_long_term_memory(
            state.user_id, f"[CRISIS-{severity.upper()}] {state.user_input} – {reason}"
        )

    state.stage_timings["crisis_detection"] = datetime.now().timestamp() - start_time
    return state


def build_context(state: OptimizedSessionState) -> OptimizedSessionState:
    """上下文构建节点"""
    start_time = datetime.now().timestamp()

    # 批量获取用户数据
    user_data = chat_service.batch_get_user_data(state.user_id)

    state.user_profile = user_data.get("profile", {})
    state.memory_context = chat_service.format_memory_context(
        user_data.get("memory", [])
    )

    # 获取会话分析数据（引导性询问和模式分析结果）
    analysis_data = chat_service.get_session_analysis_data(state.session_id)
    
    # 如果存在之前的分析结果，加载到状态中
    if analysis_data.get("inquiry_result"):
        state.inquiry_result = analysis_data["inquiry_result"]
        print(f"Loaded previous inquiry result: {state.inquiry_result.get('current_stage', 'N/A')}")
    
    if analysis_data.get("pattern_analysis"):
        state.pattern_analysis = analysis_data["pattern_analysis"]
        print(f"Loaded previous pattern analysis: {len(state.pattern_analysis.get('key_insights', []))} insights")

    state.processing_stage = "context_built"
    state.stage_timings["context_building"] = datetime.now().timestamp() - start_time

    return state


def search_information(state: OptimizedSessionState) -> OptimizedSessionState:
    """搜索信息节点（同步版本）"""
    start_time = datetime.now().timestamp()

    if state.need_search and not state.skip_search:
        try:
            search_results = search_service._sync_search(state.user_input)
            state.search_results = search_results
        except Exception as e:
            state.search_results = f"搜索功能暂时不可用: {e}"

    state.processing_stage = "search_completed"
    state.stage_timings["search"] = datetime.now().timestamp() - start_time

    return state


def update_plan(state: OptimizedSessionState) -> OptimizedSessionState:
    """更新对话计划节点"""
    start_time = datetime.now().timestamp()

    if state.skip_plan_update:
        state.stage_timings["plan_update"] = 0
        return state

    try:
        # 获取或创建计划
        plan = chat_service.db.get_session_plan(state.session_id)
        if not plan:
            plan = {
                "session_id": state.session_id,
                "user_intent": {
                    "type": "unknown",
                    "description": "",
                    "confidence": 0.0,
                    "identified_at": datetime.now().isoformat(),
                },
                "current_state": {
                    "stage": "intent_identification",
                    "progress": 0.0,
                    "last_updated": datetime.now().isoformat(),
                },
                "steps": [],
                "context": {"key_points": [], "emotions": [], "concerns": []},
                "inquiry_status": {
                    "stage": "初始阶段",
                    "information_completeness": 0,
                    "collected_info": {},
                    "pattern_analyzed": False,
                },
            }

        # 构建消息
        messages = [
            {"role": "system", "content": chat_service.planning_prompt},
            {
                "role": "user",
                "content": f"Current plan: {json.dumps(plan, ensure_ascii=False)}\n\n"
                f"Current message: {state.user_input}\n\n"
                f"History: {json.dumps(state.history, ensure_ascii=False)}",
            },
        ]

        # 调用LLM更新计划
        response = chat_service.client.invoke(messages)
        reply = response.content.strip()

        # 解析更新后的计划
        updated_plan = extract_json(reply)
        if updated_plan:
            if "inquiry_status" not in updated_plan:
                updated_plan["inquiry_status"] = plan.get(
                    "inquiry_status",
                    {
                        "stage": "初始阶段",
                        "information_completeness": 0,
                        "collected_info": {},
                        "pattern_analyzed": False,
                    },
                )

            chat_service.db.save_session_plan(state.session_id, updated_plan)
            state.plan = updated_plan
        else:
            plan["current_state"]["last_updated"] = datetime.now().isoformat()
            state.plan = plan

    except Exception as e:
        print(f"Error updating plan: {e}")
        state.plan = {}

    state.processing_stage = "plan_updated"
    state.stage_timings["plan_update"] = datetime.now().timestamp() - start_time

    return state


def generate_response(state: OptimizedSessionState) -> OptimizedSessionState:
    """生成AI响应节点"""
    start_time = datetime.now().timestamp()

    try:
        # 格式化历史记录
        messages = [{"role": "system", "content": chat_service.prompt_template}]

        # 添加历史对话
        for msg in state.history:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "agent":
                messages.append({"role": "assistant", "content": msg["content"]})

        # 添加当前用户输入
        messages.append({"role": "user", "content": state.user_input})

        # 准备附加上下文
        additional_context = ""

        if state.plan:
            additional_context += (
                f"\n\n当前对话计划：{json.dumps(state.plan, ensure_ascii=False)}"
            )

        if state.search_results:
            additional_context += f"\n\n相关搜索信息：{state.search_results}"

        if state.memory_context:
            additional_context += f"\n\n相关记忆：{state.memory_context}"

        # 添加引导性询问上下文
        if state.inquiry_result:
            additional_context += f"\n\n引导性询问评估：{json.dumps(state.inquiry_result, ensure_ascii=False)}"
            
            # 如果需要引导性询问，修改系统提示
            if state.inquiry_result.get("need_inquiry", False):
                suggested_questions = state.inquiry_result.get("suggested_questions", [])
                if suggested_questions:
                    additional_context += f"\n\n建议的引导性问题：{suggested_questions}"
                    additional_context += "\n\n请在给出共情回应后，适当地提出1-2个引导性问题来了解更多信息。"

        # 添加模式分析上下文
        if state.pattern_analysis:
            additional_context += f"\n\n行为模式分析已完成，关键洞察：{state.pattern_analysis.get('key_insights', [])}"
            additional_context += f"\n\n咨询建议：{state.pattern_analysis.get('consultation_recommendations', [])}"

        if additional_context:
            messages[0]["content"] += additional_context

        # 调用LLM生成响应
        ai_response = chat_service.client.invoke(messages)
        reply = ai_response.content.strip() or "抱歉，暂时无法回答。"

        # 提取情绪
        clean_content, emotion = chat_service.extract_emotion(reply)
        state.response = clean_content
        state.emotion = emotion

    except Exception as e:
        print(f"Error generating response: {e}")
        state.response = f"对话处理出错: {e}"
        state.emotion = "neutral"

    state.processing_stage = "response_generated"
    state.stage_timings["response_generation"] = datetime.now().timestamp() - start_time

    return state


def guided_inquiry_assessment(state: OptimizedSessionState) -> OptimizedSessionState:
    """引导性询问评估节点"""
    start_time = datetime.now().timestamp()
    
    # 判断是否需要进行引导性询问
    if (chat_service.enable_guided_inquiry and 
        len(state.history) <= 10 and 
        not state.plan.get("inquiry_status", {}).get("pattern_analyzed", False)):
        
        state.need_guided_inquiry = True
        
        # 评估信息完整性
        inquiry_result = chat_service._assess_information_completeness(
            state.session_id, state.user_input, state.history
        )
        
        state.inquiry_result = inquiry_result
        
        # 更新计划中的询问状态
        if not state.plan.get("inquiry_status"):
            state.plan["inquiry_status"] = {
                "stage": "初始阶段",
                "information_completeness": 0,
                "collected_info": {},
                "pattern_analyzed": False
            }
        
        state.plan["inquiry_status"]["information_completeness"] = inquiry_result.get("information_completeness", 0)
        state.plan["inquiry_status"]["stage"] = inquiry_result.get("current_stage", "初始阶段")
        
        # 保存引导性询问结果
        chat_service.db.save_inquiry_result(state.session_id, inquiry_result)
        
        # 保存引导性询问历史记录
        chat_service.db.save_inquiry_history(state.session_id, inquiry_result)
        
        print(f"Information completeness: {inquiry_result.get('information_completeness', 0)}%")
        
        # 判断是否需要进行模式分析
        should_analyze = (
            chat_service.enable_pattern_analysis and
            (inquiry_result.get("information_completeness", 0) >= 80 or 
             len(state.history) >= 4)  # 测试模式：4轮对话后强制分析
        )
        
        if should_analyze and not state.plan["inquiry_status"]["pattern_analyzed"]:
            state.need_pattern_analysis = True
            
    elif not chat_service.enable_guided_inquiry:
        print("Guided inquiry is disabled by configuration.")
        
        # 即使引导性询问被禁用，仍然检查是否需要进行模式分析
        if (chat_service.enable_pattern_analysis and
            len(state.history) >= 4 and
            not state.plan.get("inquiry_status", {}).get("pattern_analyzed", False)):
            state.need_pattern_analysis = True
    
    state.processing_stage = "inquiry_assessed"
    state.stage_timings["guided_inquiry"] = datetime.now().timestamp() - start_time
    
    return state


def pattern_analysis(state: OptimizedSessionState) -> OptimizedSessionState:
    """用户模式分析节点"""
    start_time = datetime.now().timestamp()
    
    if state.need_pattern_analysis:
        print("Triggering behavior pattern analysis...")
        
        # 收集所有对话信息用于模式分析
        collected_info = {
            "session_id": state.session_id,
            "conversation_history": state.history + [{"role": "user", "content": state.user_input}],
            "plan_context": state.plan.get("context", {}),
            "inquiry_stage": state.inquiry_result.get("current_stage", "信息充分") if state.inquiry_result else "信息充分",
            "inquiry_result": state.inquiry_result
        }
        
        pattern_analysis_result = chat_service._analyze_behavior_pattern(state.session_id, collected_info)
        
        if pattern_analysis_result:
            state.pattern_analysis = pattern_analysis_result
            
            # 更新计划状态
            if not state.plan.get("inquiry_status"):
                state.plan["inquiry_status"] = {
                    "stage": "初始阶段",
                    "information_completeness": 0,
                    "collected_info": {},
                    "pattern_analyzed": False
                }
            
            state.plan["inquiry_status"]["pattern_analyzed"] = True
            state.plan["inquiry_status"]["pattern_analysis_completed_at"] = datetime.now().isoformat()
            
            # 保存模式分析结果到数据库
            chat_service.db.save_pattern_analysis(state.session_id, pattern_analysis_result)
            
            # 保存更新后的会话计划
            chat_service.db.save_session_plan(state.session_id, state.plan)
            
            print("Behavior pattern analysis completed and saved.")
        else:
            print("Behavior pattern analysis failed.")
    
    state.processing_stage = "pattern_analyzed"
    state.stage_timings["pattern_analysis"] = datetime.now().timestamp() - start_time
    
    return state


def generate_analysis_report(state: OptimizedSessionState) -> OptimizedSessionState:
    """生成分析报告节点"""
    start_time = datetime.now().timestamp()
    
    if state.need_analysis_report:
        print("Generating user analysis report...")
        
        try:
            # 生成用户分析报告
            report = chat_service.analysis_service.generate_user_report(
                user_id=state.user_id,
                session_ids=None,  # 自动获取所有会话
                time_period=30  # 最近30天
            )
            
            if "error" not in report:
                state.analysis_report = report
                
                # 生成系统性的详细分析报告
                ai_analysis = report.get("ai_analysis", {})
                metadata = report.get("metadata", {})
                
                # 构建完整的系统性分析报告
                report_response = "📊 知己报告 - 全面心理健康分析报告\n"
                report_response += "=" * 50 + "\n\n"
                
                # === 1. 报告基本信息 ===
                report_response += "🔍 报告基本信息\n"
                report_response += f"• 用户ID: {state.user_id}\n"
                report_response += f"• 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                report_response += f"• 分析时间范围: 最近30天\n"
                report_response += f"• 数据完整度: {metadata.get('data_completeness', 0):.1f}%\n"
                report_response += f"• 分析可信度: {metadata.get('analysis_confidence', 0):.1f}%\n\n"
                
                # === 2. 数据概览 ===
                report_response += "📋 数据概览\n"
                report_response += f"• 会话总数: {metadata.get('total_sessions', 0)}\n"
                report_response += f"• 对话记录: {metadata.get('total_conversations', 0)}\n"
                report_response += f"• 事件记录: {metadata.get('total_events', 0)}\n"
                report_response += f"• 情绪记录: {metadata.get('total_emotions', 0)}\n"
                report_response += f"• 行为模式: {metadata.get('total_patterns', 0)}\n"
                report_response += f"• 心情记录: {metadata.get('total_moods', 0)}\n\n"
                
                # === 3. 执行摘要 ===
                executive_summary = ai_analysis.get("executive_summary", {})
                if executive_summary:
                    report_response += "🎯 执行摘要\n"
                    report_response += f"• 整体状态: {executive_summary.get('overall_status', '需要更多数据')}\n"
                    report_response += f"• 进步趋势: {executive_summary.get('progress_trend', '稳定')}\n"
                    report_response += f"• 风险等级: {executive_summary.get('risk_level', '未知')}\n"
                    report_response += f"• 评估可信度: {executive_summary.get('confidence_level', '中等')}\n"
                    report_response += f"• 分析时间段: {executive_summary.get('report_period', '最近30天')}\n\n"
                    
                    # 关键发现
                    key_findings = executive_summary.get("key_findings", [])
                    if key_findings:
                        report_response += "🔍 关键发现\n"
                        for i, finding in enumerate(key_findings, 1):
                            report_response += f"{i}. {finding}\n"
                        report_response += "\n"
                    
                    # 个人优势
                    strengths = executive_summary.get("strengths", [])
                    if strengths:
                        report_response += "💪 个人优势\n"
                        for strength in strengths:
                            report_response += f"• {strength}\n"
                        report_response += "\n"
                    
                    # 主要关注点
                    concerns = executive_summary.get("primary_concerns", [])
                    if concerns:
                        report_response += "⚠️ 主要关注点\n"
                        for concern in concerns:
                            report_response += f"• {concern}\n"
                        report_response += "\n"
                
                # === 4. 详细分析 ===
                detailed_analysis = ai_analysis.get("detailed_analysis", {})
                if detailed_analysis:
                    report_response += "📈 详细分析\n"
                    report_response += "-" * 40 + "\n\n"
                    
                    # 沟通模式分析
                    communication_patterns = detailed_analysis.get("communication_patterns", {})
                    if communication_patterns:
                        report_response += "🗣️ 沟通模式分析\n"
                        report_response += f"• 交流频率: {communication_patterns.get('interaction_frequency', '未知')}\n"
                        report_response += f"• 消息复杂度: {communication_patterns.get('message_complexity', '未知')}\n"
                        report_response += f"• 情感表达: {communication_patterns.get('emotional_expression', '未知')}\n"
                        report_response += f"• 沟通风格: {communication_patterns.get('communication_style', '未知')}\n"
                        report_response += f"• 开放程度: {communication_patterns.get('openness_trend', '未知')}\n"
                        
                        topic_preferences = communication_patterns.get("topic_preferences", [])
                        if topic_preferences:
                            report_response += f"• 常讨论话题: {', '.join(topic_preferences)}\n"
                        report_response += "\n"
                    
                    # 事件分析
                    event_analysis = detailed_analysis.get("event_analysis", {})
                    if event_analysis:
                        report_response += "📅 事件分析\n"
                        report_response += f"• 生活事件概览: {event_analysis.get('life_events_overview', '无重要事件')}\n"
                        report_response += f"• 事件影响分析: {event_analysis.get('event_impact_analysis', '影响轻微')}\n"
                        report_response += f"• 恢复模式: {event_analysis.get('recovery_patterns', '恢复良好')}\n"
                        report_response += f"• 事件频率趋势: {event_analysis.get('event_frequency_trend', '稳定')}\n"
                        
                        event_patterns = event_analysis.get("event_patterns", [])
                        if event_patterns:
                            report_response += f"• 事件模式: {', '.join(event_patterns)}\n"
                        
                        trigger_events = event_analysis.get("trigger_events", [])
                        if trigger_events:
                            report_response += f"• 触发事件: {', '.join(trigger_events)}\n"
                        report_response += "\n"
                    
                    # 情绪画像
                    emotional_profile = detailed_analysis.get("emotional_profile", {})
                    if emotional_profile:
                        report_response += "💭 情绪画像\n"
                        report_response += f"• 情绪稳定性: {emotional_profile.get('emotion_stability', '未知')}\n"
                        report_response += f"• 情绪调节: {emotional_profile.get('emotion_regulation', '未知')}\n"
                        report_response += f"• 情绪波动范围: {emotional_profile.get('emotional_range', '未知')}\n"
                        report_response += f"• 情绪复杂度: {emotional_profile.get('emotional_complexity', '未知')}\n"
                        report_response += f"• 积极情绪趋势: {emotional_profile.get('positive_emotions_trend', '未知')}\n"
                        report_response += f"• 消极情绪趋势: {emotional_profile.get('negative_emotions_trend', '未知')}\n"
                        
                        dominant_emotions = emotional_profile.get("dominant_emotions", [])
                        if dominant_emotions:
                            report_response += f"• 主要情绪: {', '.join(dominant_emotions)}\n"
                        
                        trigger_emotions = emotional_profile.get("trigger_emotions", [])
                        if trigger_emotions:
                            report_response += f"• 易触发情绪: {', '.join(trigger_emotions)}\n"
                        report_response += "\n"
                    
                    # 行为模式分析
                    behavioral_patterns = detailed_analysis.get("behavioral_patterns", {})
                    if behavioral_patterns:
                        report_response += "🎭 行为模式分析\n"
                        report_response += f"• 行为效果评估: {behavioral_patterns.get('behavior_effectiveness', '未知')}\n"
                        report_response += f"• 行为模式演变: {behavioral_patterns.get('behavior_evolution', '未知')}\n"
                        
                        primary_behaviors = behavioral_patterns.get("primary_behaviors", [])
                        if primary_behaviors:
                            report_response += f"• 主要行为模式: {', '.join(primary_behaviors)}\n"
                        
                        coping_strategies = behavioral_patterns.get("coping_strategies", [])
                        if coping_strategies:
                            report_response += f"• 应对策略: {', '.join(coping_strategies)}\n"
                        
                        adaptive_behaviors = behavioral_patterns.get("adaptive_behaviors", [])
                        if adaptive_behaviors:
                            report_response += f"• 适应性行为: {', '.join(adaptive_behaviors)}\n"
                        
                        maladaptive_behaviors = behavioral_patterns.get("maladaptive_behaviors", [])
                        if maladaptive_behaviors:
                            report_response += f"• 不良行为模式: {', '.join(maladaptive_behaviors)}\n"
                        
                        behavior_triggers = behavioral_patterns.get("behavior_triggers", [])
                        if behavior_triggers:
                            report_response += f"• 行为触发因素: {', '.join(behavior_triggers)}\n"
                        report_response += "\n"
                    
                    # 认知模式分析
                    cognitive_patterns = detailed_analysis.get("cognitive_patterns", {})
                    if cognitive_patterns:
                        report_response += "🧠 认知模式分析\n"
                        report_response += f"• 问题解决方式: {cognitive_patterns.get('problem_solving_approach', '未知')}\n"
                        report_response += f"• 认知灵活性: {cognitive_patterns.get('cognitive_flexibility', '未知')}\n"
                        report_response += f"• 元认知意识: {cognitive_patterns.get('metacognitive_awareness', '未知')}\n"
                        
                        thinking_styles = cognitive_patterns.get("thinking_styles", [])
                        if thinking_styles:
                            report_response += f"• 思维风格: {', '.join(thinking_styles)}\n"
                        
                        cognitive_biases = cognitive_patterns.get("cognitive_biases", [])
                        if cognitive_biases:
                            report_response += f"• 认知偏差: {', '.join(cognitive_biases)}\n"
                        
                        core_beliefs = cognitive_patterns.get("core_beliefs", [])
                        if core_beliefs:
                            report_response += f"• 核心信念: {', '.join(core_beliefs)}\n"
                        
                        cognitive_distortions = cognitive_patterns.get("cognitive_distortions", [])
                        if cognitive_distortions:
                            report_response += f"• 认知扭曲: {', '.join(cognitive_distortions)}\n"
                        report_response += "\n"
                    
                    # 社交互动分析
                    social_interaction = detailed_analysis.get("social_interaction", {})
                    if social_interaction:
                        report_response += "🤝 社交互动分析\n"
                        report_response += f"• 互动风格: {social_interaction.get('interaction_style', '未知')}\n"
                        report_response += f"• 求助行为: {social_interaction.get('support_seeking', '未知')}\n"
                        report_response += f"• 社会支持利用: {social_interaction.get('social_support_utilization', '未知')}\n"
                        report_response += f"• 社交参与度: {social_interaction.get('social_engagement', '未知')}\n"
                        report_response += f"• 人际交往技能: {social_interaction.get('interpersonal_skills', '未知')}\n"
                        
                        relationship_patterns = social_interaction.get("relationship_patterns", [])
                        if relationship_patterns:
                            report_response += f"• 人际关系模式: {', '.join(relationship_patterns)}\n"
                        report_response += "\n"
                    
                    # 成长轨迹分析
                    growth_trajectory = detailed_analysis.get("growth_trajectory", {})
                    if growth_trajectory:
                        report_response += "📈 成长轨迹分析\n"
                        report_response += f"• 自我洞察力: {growth_trajectory.get('insight_development', '未知')}\n"
                        report_response += f"• 韧性建设: {growth_trajectory.get('resilience_building', '未知')}\n"
                        report_response += f"• 目标达成: {growth_trajectory.get('goal_achievement', '未知')}\n"
                        report_response += f"• 变化准备度: {growth_trajectory.get('change_readiness', '未知')}\n"
                        
                        progress_indicators = growth_trajectory.get("progress_indicators", [])
                        if progress_indicators:
                            report_response += f"• 进步指标: {', '.join(progress_indicators)}\n"
                        
                        skill_development = growth_trajectory.get("skill_development", [])
                        if skill_development:
                            report_response += f"• 技能发展: {', '.join(skill_development)}\n"
                        
                        learning_patterns = growth_trajectory.get("learning_patterns", [])
                        if learning_patterns:
                            report_response += f"• 学习模式: {', '.join(learning_patterns)}\n"
                        report_response += "\n"
                
                # === 5. 综合建议 ===
                recommendations = ai_analysis.get("comprehensive_recommendations", {})
                if recommendations:
                    report_response += "💡 综合建议\n"
                    report_response += "-" * 40 + "\n\n"
                    
                    # 立即行动建议
                    immediate_actions = recommendations.get("immediate_actions", {})
                    if immediate_actions:
                        report_response += "🚨 立即行动建议\n"
                        
                        high_priority = immediate_actions.get("high_priority", [])
                        if high_priority:
                            report_response += "高优先级:\n"
                            for action in high_priority:
                                report_response += f"• {action}\n"
                        
                        medium_priority = immediate_actions.get("medium_priority", [])
                        if medium_priority:
                            report_response += "中优先级:\n"
                            for action in medium_priority:
                                report_response += f"• {action}\n"
                        
                        low_priority = immediate_actions.get("low_priority", [])
                        if low_priority:
                            report_response += "低优先级:\n"
                            for action in low_priority:
                                report_response += f"• {action}\n"
                        report_response += "\n"
                    
                    # 治疗干预建议
                    therapeutic = recommendations.get("therapeutic_interventions", {})
                    if therapeutic:
                        report_response += "🏥 治疗干预建议\n"
                        
                        approaches = therapeutic.get("recommended_approaches", [])
                        if approaches:
                            report_response += f"• 推荐治疗方法: {', '.join(approaches)}\n"
                        
                        skill_building = therapeutic.get("skill_building", [])
                        if skill_building:
                            report_response += f"• 技能建设: {', '.join(skill_building)}\n"
                        
                        coping_enhancement = therapeutic.get("coping_enhancement", [])
                        if coping_enhancement:
                            report_response += f"• 应对能力增强: {', '.join(coping_enhancement)}\n"
                        
                        cognitive_restructuring = therapeutic.get("cognitive_restructuring", [])
                        if cognitive_restructuring:
                            report_response += f"• 认知重构: {', '.join(cognitive_restructuring)}\n"
                        report_response += "\n"
                    
                    # 生活方式调整
                    lifestyle = recommendations.get("lifestyle_modifications", {})
                    if lifestyle:
                        report_response += "🌱 生活方式调整\n"
                        
                        daily_habits = lifestyle.get("daily_habits", [])
                        if daily_habits:
                            report_response += f"• 日常习惯: {', '.join(daily_habits)}\n"
                        
                        stress_management = lifestyle.get("stress_management", [])
                        if stress_management:
                            report_response += f"• 压力管理: {', '.join(stress_management)}\n"
                        
                        social_connections = lifestyle.get("social_connections", [])
                        if social_connections:
                            report_response += f"• 社交关系: {', '.join(social_connections)}\n"
                        
                        self_care = lifestyle.get("self_care", [])
                        if self_care:
                            report_response += f"• 自我照顾: {', '.join(self_care)}\n"
                        report_response += "\n"
                    
                    # 长期目标
                    long_term_goals = recommendations.get("long_term_goals", {})
                    if long_term_goals:
                        report_response += "🎯 长期目标\n"
                        
                        personal_development = long_term_goals.get("personal_development", [])
                        if personal_development:
                            report_response += f"• 个人发展: {', '.join(personal_development)}\n"
                        
                        mental_health_maintenance = long_term_goals.get("mental_health_maintenance", [])
                        if mental_health_maintenance:
                            report_response += f"• 心理健康维护: {', '.join(mental_health_maintenance)}\n"
                        
                        skill_mastery = long_term_goals.get("skill_mastery", [])
                        if skill_mastery:
                            report_response += f"• 技能精进: {', '.join(skill_mastery)}\n"
                        
                        relationship_enhancement = long_term_goals.get("relationship_enhancement", [])
                        if relationship_enhancement:
                            report_response += f"• 关系提升: {', '.join(relationship_enhancement)}\n"
                        report_response += "\n"
                
                # === 6. 风险评估 ===
                risk_assessment = ai_analysis.get("risk_assessment", {})
                if risk_assessment:
                    report_response += "🚨 风险评估\n"
                    report_response += "-" * 40 + "\n\n"
                    
                    intervention_priority = risk_assessment.get("intervention_priority", "")
                    if intervention_priority:
                        priority_text = {"high": "高", "medium": "中", "low": "低"}.get(intervention_priority, intervention_priority)
                        report_response += f"• 干预优先级: {priority_text}\n\n"
                    
                    # 当前风险
                    current_risks = risk_assessment.get("current_risks", {})
                    if current_risks:
                        report_response += "⚠️ 当前风险\n"
                        
                        immediate_risks = current_risks.get("immediate_risks", [])
                        if immediate_risks:
                            report_response += "即时风险:\n"
                            for risk in immediate_risks:
                                report_response += f"• {risk}\n"
                        
                        short_term_risks = current_risks.get("short_term_risks", [])
                        if short_term_risks:
                            report_response += "短期风险:\n"
                            for risk in short_term_risks:
                                report_response += f"• {risk}\n"
                        
                        long_term_risks = current_risks.get("long_term_risks", [])
                        if long_term_risks:
                            report_response += "长期风险:\n"
                            for risk in long_term_risks:
                                report_response += f"• {risk}\n"
                        report_response += "\n"
                    
                    # 保护因素
                    protective_factors = risk_assessment.get("protective_factors", {})
                    if protective_factors:
                        report_response += "🛡️ 保护因素\n"
                        
                        personal_strengths = protective_factors.get("personal_strengths", [])
                        if personal_strengths:
                            report_response += f"• 个人优势: {', '.join(personal_strengths)}\n"
                        
                        social_support = protective_factors.get("social_support", [])
                        if social_support:
                            report_response += f"• 社会支持: {', '.join(social_support)}\n"
                        
                        coping_resources = protective_factors.get("coping_resources", [])
                        if coping_resources:
                            report_response += f"• 应对资源: {', '.join(coping_resources)}\n"
                        
                        environmental_factors = protective_factors.get("environmental_factors", [])
                        if environmental_factors:
                            report_response += f"• 环境因素: {', '.join(environmental_factors)}\n"
                        report_response += "\n"
                    
                    # 预警信号
                    warning_signals = risk_assessment.get("warning_signals", {})
                    if warning_signals:
                        report_response += "⚠️ 预警信号\n"
                        
                        behavioral_indicators = warning_signals.get("behavioral_indicators", [])
                        if behavioral_indicators:
                            report_response += f"• 行为指标: {', '.join(behavioral_indicators)}\n"
                        
                        emotional_indicators = warning_signals.get("emotional_indicators", [])
                        if emotional_indicators:
                            report_response += f"• 情绪指标: {', '.join(emotional_indicators)}\n"
                        
                        cognitive_indicators = warning_signals.get("cognitive_indicators", [])
                        if cognitive_indicators:
                            report_response += f"• 认知指标: {', '.join(cognitive_indicators)}\n"
                        
                        social_indicators = warning_signals.get("social_indicators", [])
                        if social_indicators:
                            report_response += f"• 社交指标: {', '.join(social_indicators)}\n"
                        report_response += "\n"
                    
                    # 监控建议
                    monitoring_recommendations = risk_assessment.get("monitoring_recommendations", [])
                    if monitoring_recommendations:
                        report_response += "📊 监控建议\n"
                        for rec in monitoring_recommendations:
                            report_response += f"• {rec}\n"
                        report_response += "\n"
                    
                    # 危机预防
                    crisis_prevention = risk_assessment.get("crisis_prevention", [])
                    if crisis_prevention:
                        report_response += "🚨 危机预防策略\n"
                        for strategy in crisis_prevention:
                            report_response += f"• {strategy}\n"
                        report_response += "\n"
                
                # === 7. 数据洞察 ===
                data_insights = ai_analysis.get("data_insights", {})
                if data_insights:
                    report_response += "📊 数据洞察\n"
                    report_response += "-" * 40 + "\n\n"
                    
                    report_response += f"• 数据质量: {data_insights.get('data_quality', '未知')}\n"
                    report_response += f"• 分析可信度: {data_insights.get('analysis_confidence', '未知')}\n"
                    
                    data_gaps = data_insights.get("data_gaps", [])
                    if data_gaps:
                        report_response += f"• 数据缺口: {', '.join(data_gaps)}\n"
                    
                    trending_patterns = data_insights.get("trending_patterns", [])
                    if trending_patterns:
                        report_response += f"• 趋势模式: {', '.join(trending_patterns)}\n"
                    
                    predictive_indicators = data_insights.get("predictive_indicators", [])
                    if predictive_indicators:
                        report_response += f"• 预测指标: {', '.join(predictive_indicators)}\n"
                    
                    anomaly_detection = data_insights.get("anomaly_detection", [])
                    if anomaly_detection:
                        report_response += f"• 异常检测: {', '.join(anomaly_detection)}\n"
                    report_response += "\n"
                
                # === 8. 后续建议 ===
                follow_up = ai_analysis.get("follow_up_recommendations", {})
                if follow_up:
                    report_response += "📋 后续建议\n"
                    report_response += "-" * 40 + "\n\n"
                    
                    report_response += f"• 监控计划: {follow_up.get('monitoring_schedule', '未设定')}\n"
                    report_response += f"• 重新评估时间: {follow_up.get('reassessment_timeline', '未设定')}\n"
                    
                    data_collection_focus = follow_up.get("data_collection_focus", [])
                    if data_collection_focus:
                        report_response += f"• 数据收集重点: {', '.join(data_collection_focus)}\n"
                    
                    intervention_adjustments = follow_up.get("intervention_adjustments", [])
                    if intervention_adjustments:
                        report_response += f"• 干预调整建议: {', '.join(intervention_adjustments)}\n"
                    
                    progress_metrics = follow_up.get("progress_metrics", [])
                    if progress_metrics:
                        report_response += f"• 进展指标: {', '.join(progress_metrics)}\n"
                    report_response += "\n"
                
                # === 9. 报告结尾 ===
                report_response += "=" * 50 + "\n"
                report_response += "📝 报告说明\n"
                report_response += "• 本报告基于用户的对话历史、事件记录、情绪数据等多维度信息生成\n"
                report_response += "• 分析结果仅供参考，不能替代专业心理咨询或医疗建议\n"
                report_response += "• 如需更详细的分析或专业帮助，请咨询专业心理健康专家\n"
                report_response += "• 系统会持续学习和优化，报告质量将不断提升\n\n"
                
                report_response += "💬 需要帮助?\n"
                report_response += "如果您对报告内容有疑问，或需要更详细的解释，请随时告诉我！\n"
                report_response += "我可以为您解读报告中的任何部分，或提供更具体的建议。"
                
                # 设置报告回复为响应
                state.response = report_response
                
                # 保存分析报告到数据库
                chat_service.db.save_analysis_report(state.user_id, report)
                
                print("Comprehensive analysis report generated and saved successfully.")
            else:
                error_msg = report.get("error", "未知错误")
                state.response = f"抱歉，生成分析报告时出现错误: {error_msg}\n\n请稍后再试，或联系技术支持。"
                print(f"Error generating analysis report: {error_msg}")
                
        except Exception as e:
            state.response = f"抱歉，生成分析报告时出现错误: {str(e)}\n\n请稍后再试，或联系技术支持。"
            print(f"Exception in analysis report generation: {str(e)}")
    
    state.processing_stage = "analysis_report_generated"
    state.stage_timings["analysis_report"] = datetime.now().timestamp() - start_time
    
    return state


def postprocess_and_save(state: OptimizedSessionState) -> OptimizedSessionState:
    """后处理和数据保存节点"""
    start_time = datetime.now().timestamp()

    try:
        # 计算情绪评分
        emotion_score = SnowNLP(state.user_input).sentiments * 2 - 1

        # 批量保存数据
        save_futures = []

        # 保存情绪评分
        save_futures.append(
            chat_service.executor.submit(
                chat_service.db.save_emotion_score,
                state.user_id,
                state.session_id,
                emotion_score,
                state.emotion,
            )
        )

        # 更新用户画像
        save_futures.append(
            chat_service.executor.submit(
                chat_service.db.save_user_profile,
                state.user_id,
                {
                    "last_interaction": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "recent_emotion_score": emotion_score,
                    "recent_emotion": state.emotion,
                },
            )
        )

        # 保存记忆（每3次对话保存一次到长期记忆）
        emotion_history = chat_service.db.get_emotion_history(state.user_id)
        is_long_term = (len(emotion_history) + 1) % 3 == 0

        if is_long_term:
            save_futures.append(
                chat_service.executor.submit(
                    chat_service.db.save_long_term_memory,
                    state.user_id,
                    f"用户: {state.user_input}\n咨询师: {state.response}",
                )
            )

        # 等待所有保存操作完成
        for future in as_completed(save_futures, timeout=3):
            try:
                future.result()
            except Exception as e:
                print(f"Save operation failed: {e}")

        # 更新历史记录
        state.history.append({"role": "user", "content": state.user_input})
        state.history.append({"role": "agent", "content": state.response})

        # 获取更新后的用户画像
        state.user_profile = chat_service.db.get_user_profile(state.user_id)

    except Exception as e:
        print(f"Error in postprocess_and_save: {e}")

    state.processing_stage = "completed"
    state.stage_timings["postprocess"] = datetime.now().timestamp() - start_time

    # 计算总处理时间
    total_time = datetime.now().timestamp() - state.total_start_time
    state.stage_timings["total"] = total_time

    return state


# === 路由函数 ===


def should_skip_to_response(state: OptimizedSessionState) -> str:
    """检查是否应该跳过某些步骤直接生成响应"""
    if state.crisis_detected:
        return "postprocess_save"
    return "context_build"


def should_search(state: OptimizedSessionState) -> str:
    """检查是否需要搜索"""
    if state.need_search:
        return "search_info"
    return "plan_update"


def should_update_plan(state: OptimizedSessionState) -> str:
    """检查是否需要更新计划"""
    # 简单的启发式：如果是问候语或简单回复，跳过计划更新
    simple_inputs = {"你好", "谢谢", "好的", "嗯", "是的", "不是"}
    if state.user_input in simple_inputs:
        state.skip_plan_update = True
        return "generate_response"
    return "plan_update"


def should_do_guided_inquiry(state: OptimizedSessionState) -> str:
    """检查是否需要进行引导性询问"""
    return "guided_inquiry"


def should_do_pattern_analysis(state: OptimizedSessionState) -> str:
    """检查是否需要进行模式分析"""
    if state.need_pattern_analysis:
        return "pattern_analysis_node"
    return "generate_analysis_report"


def should_generate_analysis_report(state: OptimizedSessionState) -> str:
    """检查是否需要生成分析报告"""
    if state.need_analysis_report:
        return "generate_analysis_report"
    return "generate_response"


# === 构建 LangGraph ===

# 创建工作流
workflow = StateGraph(OptimizedSessionState)

# 添加节点
workflow.add_node("preprocess", preprocess_input)
workflow.add_node("crisis_check", detect_crisis)
workflow.add_node("context_build", build_context)
workflow.add_node("search_info", search_information)
workflow.add_node("plan_update", update_plan)
workflow.add_node("guided_inquiry", guided_inquiry_assessment)
workflow.add_node("pattern_analysis_node", pattern_analysis)
workflow.add_node("generate_analysis_report", generate_analysis_report)
workflow.add_node("generate_response", generate_response)
workflow.add_node("postprocess_save", postprocess_and_save)

# 设置入口点
workflow.set_entry_point("preprocess")

# 添加边和条件路由
workflow.add_edge("preprocess", "crisis_check")
workflow.add_conditional_edges(
    "crisis_check",
    should_skip_to_response,
    {"context_build": "context_build", "postprocess_save": "postprocess_save"},
)
workflow.add_conditional_edges(
    "context_build",
    should_search,
    {"search_info": "search_info", "plan_update": "plan_update"},
)
workflow.add_conditional_edges(
    "search_info",
    should_update_plan,
    {"plan_update": "plan_update", "generate_response": "generate_response"},
)
workflow.add_conditional_edges(
    "plan_update",
    should_do_guided_inquiry,
    {"guided_inquiry": "guided_inquiry"},
)
workflow.add_conditional_edges(
    "guided_inquiry",
    should_do_pattern_analysis,
    {"pattern_analysis_node": "pattern_analysis_node", "generate_analysis_report": "generate_analysis_report"},
)
workflow.add_conditional_edges(
    "pattern_analysis_node",
    should_generate_analysis_report,
    {"generate_analysis_report": "generate_analysis_report", "generate_response": "generate_response"},
)
workflow.add_conditional_edges(
    "generate_analysis_report",
    lambda state: "postprocess_save" if state.need_analysis_report else "generate_response",
    {"postprocess_save": "postprocess_save", "generate_response": "generate_response"},
)
workflow.add_edge("generate_response", "postprocess_save")
workflow.add_edge("postprocess_save", END)

# 编译工作流
optimized_chat_app = workflow.compile()

# === 主要接口函数 ===


def optimized_chat(
    user_input: str,
    user_id: str = "default_user",
    session_id: str | None = None,
    history: List[Dict[str, str]] | None = None,
    enable_performance_monitoring: bool = False,
) -> Dict[str, Any]:
    """
    优化的聊天接口函数

    Args:
        user_input: 用户输入
        user_id: 用户ID
        session_id: 会话ID
        history: 对话历史
        enable_performance_monitoring: 是否启用性能监控

    Returns:
        包含响应和其他信息的字典
    """

    # 初始化状态
    init_state = OptimizedSessionState(
        user_input=user_input,
        user_id=user_id,
        session_id=session_id,
        history=history or [],
    )

    try:
        # 运行工作流
        result = optimized_chat_app.invoke(init_state)

        # 从结果中获取最终状态
        final_state = result

        # 构建响应
        response_data = {
            "response": final_state.get("response"),
            "emotion": final_state.get("emotion", "neutral"),
            "history": final_state.get("history", []),
            "crisis_detected": final_state.get("crisis_detected", False),
            "crisis_reason": final_state.get("crisis_reason"),
            "search_results": final_state.get("search_results"),
            "pattern_analysis": final_state.get("pattern_analysis"),
            "inquiry_result": final_state.get("inquiry_result"),
            "plan": final_state.get("plan"),
            "analysis_report": final_state.get("analysis_report"),
        }

        # 添加性能监控信息
        if enable_performance_monitoring:
            response_data["performance"] = {
                "stage_timings": final_state.get("stage_timings", {}),
                "total_time": final_state.get("stage_timings", {}).get("total", 0),
                "processing_stage": final_state.get("processing_stage", "unknown"),
            }

        return response_data

    except Exception as e:
        print(f"Error in optimized_chat: {e}")
        return {
            "response": f"对话处理出错: {e}",
            "emotion": "neutral",
            "history": history or [],
            "crisis_detected": False,
            "crisis_reason": None,
            "search_results": None,
            "pattern_analysis": None,
            "inquiry_result": None,
            "plan": None,
            "analysis_report": None,
        }


# === 测试和调试功能 ===


def test_performance():
    """性能测试函数"""
    test_messages = [
        "你好",
        "我最近感觉很焦虑",
        "什么是抑郁症",
        "我想要寻找一些放松的方法",
        "今天天气怎么样",
    ]

    print("🚀 开始性能测试...")

    for i, msg in enumerate(test_messages):
        print(f"\n--- 测试消息 {i+1}: {msg} ---")
        result = optimized_chat(msg, enable_performance_monitoring=True)

        if "performance" in result:
            perf = result["performance"]
            print(f"总时间: {perf['total_time']:.2f}s")
            print("各阶段耗时:")
            for stage, time_spent in perf["stage_timings"].items():
                if time_spent > 0:
                    print(f"  {stage}: {time_spent:.2f}s")

        print(f"响应: {result['response'][:100]}...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_performance()
    else:
        print("🩺 心理咨询对话系统 (LangGraph优化版) (输入 '退出' 结束)")
        print("💡 输入 'perf' 可查看性能信息")

        history = []
        while True:
            try:
                user_input = input("您: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 再见！")
                break

            if user_input.lower() in {"退出", "quit", "q"}:
                print("👋 再见！祝您一切顺利。")
                break

            enable_perf = user_input.lower() == "perf"
            if enable_perf:
                user_input = input("请输入要测试的消息: ").strip()

            result = optimized_chat(
                user_input, history=history, enable_performance_monitoring=enable_perf
            )

            print(f"咨询师: {result['response']}")

            if enable_perf and "performance" in result:
                perf = result["performance"]
                print(f"\n⚡ 性能信息:")
                print(f"总时间: {perf['total_time']:.2f}s")
                for stage, time_spent in perf["stage_timings"].items():
                    if time_spent > 0:
                        print(f"  {stage}: {time_spent:.2f}s")

            history = result["history"]
