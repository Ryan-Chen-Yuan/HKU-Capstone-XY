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

        # 创建线程池用于并行处理
        self.executor = ThreadPoolExecutor(max_workers=3)

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


# === 构建 LangGraph ===

# 创建工作流
workflow = StateGraph(OptimizedSessionState)

# 添加节点
workflow.add_node("preprocess", preprocess_input)
workflow.add_node("crisis_check", detect_crisis)
workflow.add_node("context_build", build_context)
workflow.add_node("search_info", search_information)
workflow.add_node("plan_update", update_plan)
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
workflow.add_edge("plan_update", "generate_response")
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
