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
import logging
import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from snownlp import SnowNLP

from utils.extract_json import extract_json
from dao.database import Database

# 分析报告服务导入
try:
    from service.analysis_report_service import AnalysisReportService

    ANALYSIS_REPORT_AVAILABLE = True
except ImportError:
    ANALYSIS_REPORT_AVAILABLE = False

# RAG相关导入
try:
    from rag import RAGService, IntentRouter
    from rag.langgraph_nodes import create_rag_node, create_web_search_node
    from rag.core.rag_retriever import RerankedResult

    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# 加载环境变量
load_dotenv()

# 创建logger
logger = logging.getLogger(__name__)


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

    # RAG相关
    need_rag: bool = False
    rag_context: str = ""
    has_rag_context: bool = False

    # 意图识别
    intent_result: Dict[str, Any] = Field(default_factory=dict)
    route_decision: str = "direct_chat"  # direct_chat, rag, web_search

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
        self.timeout = 15  # 增加超时时间到15秒
        self.max_results = 3
        self.retry_count = 2  # 添加重试次数

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
        for attempt in range(self.retry_count):
            try:
                print(
                    f"🔍 开始网络搜索（尝试 {attempt + 1}/{self.retry_count}），查询: {query}"
                )
                print(
                    f"📊 搜索配置: 最大结果数={self.max_results}, 超时时间={self.timeout}秒"
                )

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
                organic_results = data.get("organic_results", [])

                print(f"✅ 搜索API调用成功，获得 {len(organic_results)} 个原始结果")

                for i, item in enumerate(organic_results[: self.max_results], 1):
                    title = item.get("title", "").strip()
                    snippet = item.get("snippet", "").strip()
                    link = item.get("link", "").strip()

                    snippets.append(
                        f"标题: {title}\n" f"摘要: {snippet}\n" f"链接: {link}"
                    )

                final_result = (
                    "\n\n".join(snippets) if snippets else "未找到相关搜索结果"
                )
                print(f"📋 最终搜索结果长度: {len(final_result)} 字符")
                print("=" * 60)
                print("完整搜索结果:")
                print(final_result)
                print("=" * 60)

                return final_result

            except requests.exceptions.Timeout as e:
                error_msg = f"搜索超时 (尝试 {attempt + 1}/{self.retry_count}): {e}"
                print(f"⚠️ {error_msg}")
                if attempt == self.retry_count - 1:  # 最后一次尝试失败
                    return f"搜索服务暂时不可用，请稍后重试。原因：连接超时，可能是网络状况不佳或服务繁忙。"
                continue
            except Exception as e:
                error_msg = f"搜索出错 (尝试 {attempt + 1}/{self.retry_count}): {e}"
                print(f"❌ {error_msg}")
                if attempt == self.retry_count - 1:  # 最后一次尝试失败
                    return f"搜索服务遇到问题: {e}"
                continue


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
            timeout=60,  # 增加超时时间到60秒，避免计划更新超时
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
        self.analysis_service = None
        if ANALYSIS_REPORT_AVAILABLE:
            try:
                self.analysis_service = AnalysisReportService()
                print("   ✅ 分析报告服务初始化成功")
            except Exception as e:
                print(f"   ❌ 分析报告服务初始化失败: {e}")

        # 初始化RAG相关组件
        self.rag_service = None
        self.intent_router = None
        self.rag_node = None
        self.web_search_node = None

        if RAG_AVAILABLE:
            self._initialize_rag_components()

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
        os.makedirs(prompt_dir, exist_ok=True)
        prompt_file = os.path.join(prompt_dir, "guided_inquiry_prompt.txt")

        if not os.path.exists(prompt_file):
            default_prompt = """你是一个专业的心理咨询师助手，负责评估对话中的信息完整性。

基于当前会话历史和最新消息，评估信息的完整程度，并确定是否需要进行引导性询问。

返回JSON格式的评估结果，包含以下字段：
- need_inquiry: 是否需要引导性询问（boolean）
- current_stage: 当前对话阶段（string）
- information_completeness: 信息完整度百分比（0-100）
- missing_info: 缺失的重要信息列表
- suggested_questions: 建议的引导性问题（最多2个）
- reason: 评估原因

请保持JSON格式的完整性。"""
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(default_prompt)
            return default_prompt

        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _load_pattern_analysis_prompt(self) -> str:
        """加载模式分析提示词模板"""
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        os.makedirs(prompt_dir, exist_ok=True)
        prompt_file = os.path.join(prompt_dir, "pattern_analysis_prompt.txt")

        if not os.path.exists(prompt_file):
            default_prompt = """你是一个专业的心理学行为模式分析师。

基于用户的对话历史和收集的信息，进行深度的行为模式分析。

返回JSON格式的分析结果，包含以下结构：
{
    "pattern_analysis": {
        "trigger_patterns": {"common_triggers": [], "trigger_intensity": "", "trigger_frequency": ""},
        "cognitive_patterns": {"thinking_styles": [], "cognitive_biases": [], "core_beliefs": []},
        "emotional_patterns": {"primary_emotions": [], "emotion_regulation": "", "emotion_duration": ""},
        "behavioral_patterns": {"coping_strategies": [], "behavior_effectiveness": "", "behavior_habits": []},
        "interpersonal_patterns": {"interaction_style": "", "support_utilization": "", "social_behaviors": []},
        "resource_patterns": {"personal_strengths": [], "successful_experiences": [], "growth_potential": []}
    },
    "pattern_summary": "模式总结",
    "key_insights": ["关键洞察1", "关键洞察2"],
    "consultation_recommendations": ["咨询建议1", "咨询建议2"]
}

请保持JSON格式的完整性。"""
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(default_prompt)
            return default_prompt

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

    def _assess_information_completeness(
        self, session_id: str, user_input: str, history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """评估信息完整性"""
        try:
            # 构建历史对话上下文
            context = ""
            if history:
                recent_messages = history[-5:]  # 取最近5轮对话
                context = "\n".join(
                    [
                        f"用户: {msg.get('user', '')}\n咨询师: {msg.get('assistant', '')}"
                        for msg in recent_messages
                    ]
                )

            # 构建评估消息
            messages = [
                {"role": "system", "content": self.guided_inquiry_prompt},
                {
                    "role": "user",
                    "content": f"对话历史:\n{context}\n\n当前消息: {user_input}\n\n请评估信息完整性并返回JSON格式的结果。",
                },
            ]

            # 调用LLM进行评估
            response = self.client.invoke(messages)
            reply = response.content.strip()

            # 解析JSON结果
            inquiry_result = extract_json(reply)
            if inquiry_result:
                return inquiry_result
            else:
                # 手动解析备用方案
                return self._parse_inquiry_manually(reply)

        except Exception as e:
            print(f"Error in _assess_information_completeness: {e}")
            return {
                "need_inquiry": False,
                "current_stage": "评估失败",
                "information_completeness": 50,
                "missing_info": [],
                "suggested_questions": [],
                "reason": f"评估出错: {e}",
            }

    def _analyze_behavior_pattern(
        self, session_id: str, collected_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析行为模式"""
        try:
            # 构建分析上下文
            history = collected_info.get("conversation_history", [])
            context = ""
            if history:
                context = "\n".join(
                    [
                        f"用户: {msg.get('user', '')}\n咨询师: {msg.get('assistant', '')}"
                        for msg in history[-10:]  # 取最近10轮对话
                    ]
                )

            # 构建分析消息
            messages = [
                {"role": "system", "content": self.pattern_analysis_prompt},
                {
                    "role": "user",
                    "content": f"对话历史:\n{context}\n\n会话信息: {json.dumps(collected_info, ensure_ascii=False)}\n\n请进行深度的行为模式分析并返回JSON格式的结果。",
                },
            ]

            # 调用LLM进行分析
            response = self.client.invoke(messages)
            reply = response.content.strip()

            # 解析JSON结果
            pattern_result = extract_json(reply)
            if pattern_result:
                return pattern_result
            else:
                # 手动解析备用方案
                return self._parse_pattern_manually(reply)

        except Exception as e:
            print(f"Error in _analyze_behavior_pattern: {e}")
            return {
                "pattern_analysis": {
                    "trigger_patterns": {
                        "common_triggers": [],
                        "trigger_intensity": "未知",
                        "trigger_frequency": "未知",
                    },
                    "cognitive_patterns": {
                        "thinking_styles": [],
                        "cognitive_biases": [],
                        "core_beliefs": [],
                    },
                    "emotional_patterns": {
                        "primary_emotions": [],
                        "emotion_regulation": "未知",
                        "emotion_duration": "未知",
                    },
                    "behavioral_patterns": {
                        "coping_strategies": [],
                        "behavior_effectiveness": "未知",
                        "behavior_habits": [],
                    },
                    "interpersonal_patterns": {
                        "interaction_style": "未知",
                        "support_utilization": "未知",
                        "social_behaviors": [],
                    },
                    "resource_patterns": {
                        "personal_strengths": [],
                        "successful_experiences": [],
                        "growth_potential": [],
                    },
                },
                "pattern_summary": f"模式分析失败: {e}",
                "key_insights": ["需要更多信息进行分析"],
                "consultation_recommendations": ["继续对话收集信息"],
            }

    def _parse_inquiry_manually(self, text: str) -> Dict[str, Any]:
        """手动解析引导性询问结果的备用方法"""
        try:
            result = {
                "need_inquiry": True,
                "current_stage": "基础情况了解",
                "missing_info": [],
                "suggested_questions": [],
                "information_completeness": 50,
                "reason": "手动解析结果",
            }

            # 查找信息完整度
            completeness_match = re.search(r"信息完整[度性]?[：:]\s*(\d+)%?", text)
            if completeness_match:
                result["information_completeness"] = int(completeness_match.group(1))

            # 查找当前阶段
            stage_match = re.search(r"当前阶段[：:]\s*([^\n]+)", text)
            if stage_match:
                result["current_stage"] = stage_match.group(1).strip()

            # 查找建议的问题
            questions = re.findall(r"[12]\.?\s*([^？?]*[？?])", text)
            if questions:
                result["suggested_questions"] = [q.strip() for q in questions[:2]]

            # 判断是否需要询问
            if result["information_completeness"] >= 80:
                result["need_inquiry"] = False
                result["current_stage"] = "信息充分"

            return result

        except Exception as e:
            print(f"Manual parsing failed: {e}")
            return {
                "need_inquiry": False,
                "current_stage": "解析失败",
                "information_completeness": 50,
                "missing_info": [],
                "suggested_questions": [],
                "reason": f"解析错误: {e}",
            }

    def _parse_pattern_manually(self, text: str) -> Dict[str, Any]:
        """手动解析行为模式分析结果的备用方法"""
        try:
            pattern_analysis = {
                "pattern_analysis": {
                    "trigger_patterns": {
                        "common_triggers": [],
                        "trigger_intensity": "中",
                        "trigger_frequency": "经常",
                    },
                    "cognitive_patterns": {
                        "thinking_styles": [],
                        "cognitive_biases": [],
                        "core_beliefs": [],
                    },
                    "emotional_patterns": {
                        "primary_emotions": [],
                        "emotion_regulation": "部分有效",
                        "emotion_duration": "中等",
                    },
                    "behavioral_patterns": {
                        "coping_strategies": [],
                        "behavior_effectiveness": "部分有效",
                        "behavior_habits": [],
                    },
                    "interpersonal_patterns": {
                        "interaction_style": "被动",
                        "support_utilization": "部分",
                        "social_behaviors": [],
                    },
                    "resource_patterns": {
                        "personal_strengths": [],
                        "successful_experiences": [],
                        "growth_potential": [],
                    },
                },
                "pattern_summary": "基于对话内容进行的手动模式分析",
                "key_insights": ["需要进一步分析", "模式识别中", "持续关注"],
                "consultation_recommendations": [
                    "保持开放沟通",
                    "建立信任关系",
                    "逐步深入了解",
                ],
            }

            return pattern_analysis

        except Exception as e:
            print(f"Manual pattern parsing failed: {e}")
            return {
                "pattern_analysis": {
                    "trigger_patterns": {
                        "common_triggers": [],
                        "trigger_intensity": "未知",
                        "trigger_frequency": "未知",
                    },
                    "cognitive_patterns": {
                        "thinking_styles": [],
                        "cognitive_biases": [],
                        "core_beliefs": [],
                    },
                    "emotional_patterns": {
                        "primary_emotions": [],
                        "emotion_regulation": "未知",
                        "emotion_duration": "未知",
                    },
                    "behavioral_patterns": {
                        "coping_strategies": [],
                        "behavior_effectiveness": "未知",
                        "behavior_habits": [],
                    },
                    "interpersonal_patterns": {
                        "interaction_style": "未知",
                        "support_utilization": "未知",
                        "social_behaviors": [],
                    },
                    "resource_patterns": {
                        "personal_strengths": [],
                        "successful_experiences": [],
                        "growth_potential": [],
                    },
                },
                "pattern_summary": f"模式分析解析失败: {e}",
                "key_insights": ["需要重新分析"],
                "consultation_recommendations": ["继续收集信息"],
            }

    def _initialize_rag_components(self):
        """初始化RAG相关组件"""
        try:
            # 检查RAG是否启用
            rag_enabled = os.environ.get("ENABLE_RAG", "true").lower() == "true"
            if not rag_enabled:
                print("   ℹ️ RAG功能已禁用")
                return

            # 尝试从start.py模块获取RAG服务
            start_module = sys.modules.get("start")
            main_module = sys.modules.get("__main__")

            if start_module and hasattr(start_module, "rag_service"):
                self.rag_service = start_module.rag_service
                print("   ✅ 使用全局RAG服务")
                logger.info("从start模块获取RAG服务")
            elif main_module and hasattr(main_module, "rag_service"):
                self.rag_service = main_module.rag_service
                print("   ✅ 使用全局RAG服务")
                logger.info("从main模块获取RAG服务")
            else:
                # 如果获取不到，创建新的RAG服务（这通常发生在测试环境中）
                print("   ⚠️ 未找到全局RAG服务，创建新实例")
                logger.warning("未找到全局RAG服务，创建新的实例")
                from rag.core.rag_service import RAGCoreService

                knowledge_source_dir = str(
                    Path(__file__).parent.parent / "knowledge_source"
                )
                data_dir = str(Path(__file__).parent.parent / "data")
                embedding_model_path = str(
                    Path(__file__).parent.parent / "qwen_embeddings"
                )
                rerank_model_path = str(Path(__file__).parent.parent / "qwen_reranker")

                self.rag_service = RAGCoreService(
                    knowledge_source_dir=knowledge_source_dir,
                    data_dir=data_dir,
                    embedding_model_path=embedding_model_path,
                    rerank_model_path=rerank_model_path,
                    device="auto",
                )

                # 初始化服务
                success = self.rag_service.initialize()
                if success:
                    print("   ✅ 新RAG实例初始化成功")
                else:
                    print("   ❌ 新RAG实例初始化失败")

            # 初始化意图路由器
            self.intent_router = IntentRouter(self.client)

            # 初始化web搜索节点
            search_enabled = bool(os.getenv("SERPAPI_KEY"))
            self.web_search_node = create_web_search_node(search_enabled)
            if search_enabled:
                print("   ✅ 网络搜索组件就绪")
            else:
                print("   ⚠️ 网络搜索组件未启用: 未设置SERPAPI_KEY")

        except Exception as e:
            print(f"   ❌ RAG组件初始化失败: {e}")
            logger.error(f"RAG组件初始化失败: {e}")
            self.rag_service = None
            self.intent_router = None
            self.web_search_node = None


# 全局服务实例（延迟初始化）
_db_instance = None
_crisis_detector_instance = None
_search_service_instance = None
_chat_service_instance = None


def get_db_instance():
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def get_crisis_detector_instance():
    global _crisis_detector_instance
    if _crisis_detector_instance is None:
        _crisis_detector_instance = OptimizedCrisisDetector()
    return _crisis_detector_instance


def get_search_service_instance():
    global _search_service_instance
    if _search_service_instance is None:
        _search_service_instance = OptimizedSearchService()
    return _search_service_instance


def get_chat_service_instance():
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = OptimizedChatService(get_db_instance())
    return _chat_service_instance


# === LangGraph 节点函数 ===

"""输入预处理节点"""


def preprocess_input(state: OptimizedSessionState) -> OptimizedSessionState:
    start_time = datetime.now().timestamp()
    state.total_start_time = start_time

    # 基本信息设置
    state.user_input = state.user_input.strip()
    state.session_id = state.session_id or state.user_id
    state.processing_stage = "preprocessed"

    # 判断是否需要搜索
    search_service = get_search_service_instance()
    state.need_search = search_service.should_search(state.user_input)

    # 记录时间
    state.stage_timings["preprocess"] = datetime.now().timestamp() - start_time

    return state


"""危机检测节点"""


def detect_crisis(state: OptimizedSessionState) -> OptimizedSessionState:
    start_time = datetime.now().timestamp()

    crisis_detector = get_crisis_detector_instance()
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
        chat_service = get_chat_service_instance()
        chat_service.db.save_long_term_memory(
            state.user_id, f"[CRISIS-{severity.upper()}] {state.user_input} – {reason}"
        )

    state.stage_timings["crisis_detection"] = datetime.now().timestamp() - start_time
    return state


"""意图识别节点"""


def intent_analysis(state: OptimizedSessionState) -> OptimizedSessionState:
    start_time = datetime.now().timestamp()

    try:
        # 如果危机已检测到，跳过意图分析
        if state.crisis_detected:
            state.route_decision = "direct_chat"
            state.need_rag = False
            state.need_search = False
            state.stage_timings["intent_analysis"] = (
                datetime.now().timestamp() - start_time
            )
            return state

        # 获取聊天服务实例进行意图分析
        chat_service = get_chat_service_instance()

        if chat_service and chat_service.intent_router:
            # 构建对话上下文
            context = ""
            if state.history:
                recent_messages = state.history[-3:]  # 取最近3轮对话
                context = "\n".join(
                    [
                        f"用户: {msg.get('user', '')}\n咨询师: {msg.get('assistant', '')}"
                        for msg in recent_messages
                    ]
                )

            # 执行意图识别
            routing_decision = chat_service.intent_router.get_routing_decision(
                state.user_input, context
            )

            state.intent_result = routing_decision["intent"]
            state.route_decision = routing_decision["route"]

            # 设置路由标志
            if state.route_decision == "rag":
                state.need_rag = True
                state.need_search = False
            elif state.route_decision == "web_search":
                state.need_rag = False
                state.need_search = True
            else:
                state.need_rag = False
                state.need_search = False

            print(f"意图识别结果: 路由到 {state.route_decision}")

        else:
            # 如果RAG不可用，使用简单的关键词判断
            from rag.intent_router import SimpleIntentRouter

            simple_router = SimpleIntentRouter()

            state.need_rag = simple_router.should_use_rag(state.user_input)
            state.need_search = simple_router.should_use_web_search(state.user_input)

            if state.need_rag:
                state.route_decision = "rag"
            elif state.need_search:
                state.route_decision = "web_search"
            else:
                state.route_decision = "direct_chat"

    except Exception as e:
        print(f"意图识别失败: {e}")
        state.route_decision = "direct_chat"
        state.need_rag = False
        state.need_search = False

    state.stage_timings["intent_analysis"] = datetime.now().timestamp() - start_time
    return state


"""RAG检索节点"""


def rag_retrieval(state: OptimizedSessionState) -> OptimizedSessionState:
    start_time = datetime.now().timestamp()

    try:
        chat_service = get_chat_service_instance()

        if chat_service and chat_service.rag_service:
            # 直接使用RAG服务进行检索，显示详细的粗排和精排过程
            logger.info(f"开始RAG检索: {state.user_input[:50]}...")
            print(f"🔍 开始RAG检索，查询: {state.user_input}")

            # 执行详细的RAG搜索，获取粗排和精排结果
            retriever = chat_service.rag_service.retriever

            # 1. 粗排阶段：向量相似度搜索，获取更多候选
            print("\n📊 第一阶段：粗排 (向量相似度搜索)")
            vector_results = chat_service.rag_service.vector_store.search(
                state.user_input, top_k=6  # 获取更多候选用于展示粗排效果
            )

            if vector_results:
                print(f"   ✅ 粗排完成，获得 {len(vector_results)} 个候选文档")
                for i, result in enumerate(vector_results, 1):
                    print(
                        f"   [{i}] 相似度: {result.score:.4f} | 来源: {result.chunk.source_file}"
                    )
                    print(f"       内容预览: {result.chunk.content[:80]}...")
            else:
                print("   ❌ 粗排未找到相关文档")
                state.rag_context = ""
                state.has_rag_context = False
                return state

            # 2. 精排阶段：使用重排序模型
            print(f"\n🎯 第二阶段：精排 (重排序模型)")
            if retriever.rerank_enabled:
                print("   ⚡ 使用Qwen重排序模型进行精排...")
                reranked_results = retriever.search(
                    state.user_input,
                    top_k=3,
                    use_rerank=True,
                    rerank_top_k=len(vector_results),
                )

                if reranked_results:
                    print(
                        f"   ✅ 精排完成，最终选择 {len(reranked_results)} 个最相关文档"
                    )
                    for result in reranked_results:
                        rerank_str = (
                            f"重排序: {result.rerank_score:.4f}"
                            if result.rerank_score is not None
                            else "未重排序"
                        )
                        print(
                            f"   [TOP{result.final_rank}] 相似度: {result.similarity_score:.4f} | {rerank_str}"
                        )
                        print(f"           来源: {result.chunk.source_file}")
                        print(f"           内容: {result.chunk.content[:60]}...")
                else:
                    print("   ❌ 精排处理失败")
                    reranked_results = []
            else:
                print("   ⚠️ 重排序模型未启用，使用粗排结果")
                reranked_results = []
                for i, result in enumerate(vector_results[:3]):
                    from rag.core.rag_retriever import RerankedResult

                    reranked_results.append(
                        RerankedResult(
                            chunk=result.chunk,
                            similarity_score=result.score,
                            rerank_score=None,
                            final_rank=i + 1,
                        )
                    )

            # 3. 生成最终上下文
            if reranked_results:
                context_parts = []
                for i, result in enumerate(reranked_results, 1):
                    context_parts.append(f"[文档{i}] 来源: {result.chunk.source_file}")
                    context_parts.append(result.chunk.content)
                    context_parts.append("")  # 空行分隔

                context = "\n".join(context_parts)

                logger.info(f"RAG检索成功，获得 {len(context)} 字符的上下文")
                state.rag_context = context
                state.has_rag_context = True
                print(f"\n📋 上下文生成完成: {len(context)} 字符")

                # 4. 显示发送给模型的完整prompt
                print(f"\n💬 发送给模型的完整prompt:")
                print("=" * 80)

                # 构建完整的prompt（模拟实际发送给模型的内容）
                system_context = (
                    "你是一个专业的心理健康助手，基于提供的参考文档来回答用户问题。"
                )
                full_prompt = f"""系统角色: {system_context}

参考文档:
{context}

用户问题: {state.user_input}

请基于上述参考文档，为用户提供专业、准确的回答。如果参考文档中没有相关信息，请诚实说明。"""

                print(full_prompt)
                print("=" * 80)

            else:
                logger.warning("RAG检索未找到相关内容")
                state.rag_context = ""
                state.has_rag_context = False
                print("RAG检索未找到相关内容")
        else:
            print("RAG服务不可用")
            state.rag_context = ""
            state.has_rag_context = False

    except Exception as e:
        print(f"RAG检索失败: {e}")
        logger.error(f"RAG检索失败: {e}")
        state.rag_context = ""
        state.has_rag_context = False

    state.stage_timings["rag_retrieval"] = datetime.now().timestamp() - start_time
    return state


"""网络搜索检索节点"""


def web_search_retrieval(state: OptimizedSessionState) -> OptimizedSessionState:
    """网络搜索检索节点"""
    start_time = datetime.now().timestamp()

    try:
        chat_service = get_chat_service_instance()
        search_service = get_search_service_instance()

        print(f"🌐 进入网络搜索节点，查询: {state.user_input}")

        # 首先尝试使用全局搜索服务
        if search_service and search_service.api_key:
            print("✅ 使用全局搜索服务进行网络搜索")
            # 使用同步搜索
            search_results = search_service._sync_search(state.user_input)
            state.search_results = search_results
            print(f"🎯 网络搜索完成，结果长度: {len(search_results)} 字符")
        elif chat_service and chat_service.web_search_node:
            print("🔄 使用备用网络搜索节点")
            # 使用网络搜索节点
            state_dict = {
                "user_input": state.user_input,
                "need_web_search": True,
                "intent_result": {},
            }
            result_dict = chat_service.web_search_node(state_dict)
            state.search_results = result_dict.get("search_results", "")
            print(f"🎯 网络搜索完成，结果长度: {len(state.search_results or '')} 字符")
        else:
            print("❌ 网络搜索服务不可用: 未设置SERPAPI_KEY或搜索服务未初始化")
            state.search_results = "⚠️ [搜索功能未启用: 未设置 SERPAPI_KEY]"

    except Exception as e:
        print(f"❌ 网络搜索失败: {e}")
        state.search_results = f"搜索出错: {e}"

    state.stage_timings["web_search"] = datetime.now().timestamp() - start_time
    return state


"""上下文构建节点"""


def build_context(state: OptimizedSessionState) -> OptimizedSessionState:
    start_time = datetime.now().timestamp()

    # 批量获取用户数据
    chat_service = get_chat_service_instance()
    user_data = chat_service.batch_get_user_data(state.user_id)

    state.user_profile = user_data.get("profile", {})
    state.memory_context = chat_service.format_memory_context(
        user_data.get("memory", [])
    )

    state.processing_stage = "context_built"
    state.stage_timings["context_building"] = datetime.now().timestamp() - start_time

    return state


"""更新对话计划节点"""


def update_plan(state: OptimizedSessionState) -> OptimizedSessionState:
    start_time = datetime.now().timestamp()

    if state.skip_plan_update:
        state.stage_timings["plan_update"] = 0
        return state

    # 检测知己报告请求
    report_keywords = [
        "知己报告",
        "知己分析报告",
        "生成报告",
        "我的报告",
        "心理分析报告",
        "分析报告",
        "知己报告生成",
    ]

    user_input_lower = state.user_input.lower()
    is_report_request = any(keyword in user_input_lower for keyword in report_keywords)

    if is_report_request:
        print(f"🔍 检测到知己报告请求: {state.user_input}")
        # 直接标记需要生成分析报告
        state.need_analysis_report = True
        # 跳过常规的计划更新流程，直接进行报告生成
        state.processing_stage = "report_requested"
        print("✅ 已设置分析报告生成标志")
        state.stage_timings["plan_update"] = datetime.now().timestamp() - start_time
        return state

    retry_count = 2  # 添加重试机制

    for attempt in range(retry_count):
        try:
            # 获取或创建计划
            chat_service = get_chat_service_instance()
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

            print(f"🔄 计划更新 (尝试 {attempt + 1}/{retry_count})")

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

            print("✅ 计划更新成功")
            break  # 成功则退出重试循环

        except Exception as e:
            error_msg = f"计划更新失败 (尝试 {attempt + 1}/{retry_count}): {e}"
            print(f"❌ {error_msg}")

            if attempt == retry_count - 1:  # 最后一次尝试失败
                print("⚠️ 计划更新彻底失败，使用基础计划")
                state.plan = {
                    "session_id": state.session_id,
                    "current_state": {
                        "stage": "基础对话",
                        "last_updated": datetime.now().isoformat(),
                    },
                    "inquiry_status": {
                        "stage": "初始阶段",
                        "information_completeness": 0,
                        "collected_info": {},
                        "pattern_analyzed": False,
                    },
                }
            else:
                continue  # 重试

    state.processing_stage = "plan_updated"
    state.stage_timings["plan_update"] = datetime.now().timestamp() - start_time

    return state


"""引导性询问评估节点"""


def guided_inquiry_assessment(state: OptimizedSessionState) -> OptimizedSessionState:
    start_time = datetime.now().timestamp()

    # 获取聊天服务实例
    chat_service = get_chat_service_instance()

    # 判断是否需要进行引导性询问
    if (
        chat_service.enable_guided_inquiry
        and len(state.history) <= 10
        and not state.plan.get("inquiry_status", {}).get("pattern_analyzed", False)
    ):

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
                "pattern_analyzed": False,
            }

        state.plan["inquiry_status"]["information_completeness"] = inquiry_result.get(
            "information_completeness", 0
        )
        state.plan["inquiry_status"]["stage"] = inquiry_result.get(
            "current_stage", "初始阶段"
        )

        # 保存引导性询问结果
        chat_service.db.save_inquiry_result(state.session_id, inquiry_result)

        # 保存引导性询问历史记录
        chat_service.db.save_inquiry_history(state.session_id, inquiry_result)

        print(
            f"Information completeness: {inquiry_result.get('information_completeness', 0)}%"
        )

        # 判断是否需要进行模式分析
        should_analyze = chat_service.enable_pattern_analysis and (
            inquiry_result.get("information_completeness", 0) >= 80
            or len(state.history) >= 4
        )  # 4轮对话后强制分析

        if should_analyze and not state.plan["inquiry_status"]["pattern_analyzed"]:
            state.need_pattern_analysis = True

    elif not chat_service.enable_guided_inquiry:
        print("Guided inquiry is disabled by configuration.")

        # 即使引导性询问被禁用，仍然检查是否需要进行模式分析
        if (
            chat_service.enable_pattern_analysis
            and len(state.history) >= 4
            and not state.plan.get("inquiry_status", {}).get("pattern_analyzed", False)
        ):
            state.need_pattern_analysis = True

    state.processing_stage = "inquiry_assessed"
    state.stage_timings["guided_inquiry"] = datetime.now().timestamp() - start_time

    return state


"""用户模式分析节点"""


def pattern_analysis(state: OptimizedSessionState) -> OptimizedSessionState:
    start_time = datetime.now().timestamp()

    # 获取聊天服务实例
    chat_service = get_chat_service_instance()

    if state.need_pattern_analysis:
        print("Triggering behavior pattern analysis...")

        # 收集所有对话信息用于模式分析
        collected_info = {
            "session_id": state.session_id,
            "conversation_history": state.history
            + [{"user": state.user_input, "role": "user"}],
            "plan_context": state.plan.get("context", {}),
            "inquiry_stage": (
                state.inquiry_result.get("current_stage", "信息充分")
                if state.inquiry_result
                else "信息充分"
            ),
            "inquiry_result": state.inquiry_result,
        }

        pattern_analysis_result = chat_service._analyze_behavior_pattern(
            state.session_id, collected_info
        )

        if pattern_analysis_result:
            state.pattern_analysis = pattern_analysis_result

            # 更新计划状态
            if not state.plan.get("inquiry_status"):
                state.plan["inquiry_status"] = {
                    "stage": "初始阶段",
                    "information_completeness": 0,
                    "collected_info": {},
                    "pattern_analyzed": False,
                }

            state.plan["inquiry_status"]["pattern_analyzed"] = True
            state.plan["inquiry_status"][
                "pattern_analysis_completed_at"
            ] = datetime.now().isoformat()

            # 保存模式分析结果到数据库
            chat_service.db.save_pattern_analysis(
                state.session_id, pattern_analysis_result
            )

            # 保存更新后的会话计划
            chat_service.db.save_session_plan(state.session_id, state.plan)

            print("Behavior pattern analysis completed and saved.")

            # 检查是否需要生成分析报告
            # 当模式分析完成且信息完整度较高时，可以生成报告
            if (
                chat_service.analysis_service
                and state.inquiry_result
                and state.inquiry_result.get("information_completeness", 0) >= 80
            ):
                state.need_analysis_report = True
        else:
            print("Behavior pattern analysis failed.")

    state.processing_stage = "pattern_analyzed"
    state.stage_timings["pattern_analysis"] = datetime.now().timestamp() - start_time

    return state


def _generate_basic_report(state: OptimizedSessionState) -> str:
    """生成基础报告（当详细报告无法生成时使用）"""
    chat_service = get_chat_service_instance()

    # 尝试获取基础统计数据
    try:
        user_sessions = (
            chat_service.db.get_user_sessions(state.user_id) if chat_service.db else []
        )
        session_count = len(user_sessions)

        # 计算总消息数
        total_messages = 0
        for session in user_sessions:
            try:
                count = chat_service.db.get_user_message_count(session)
                total_messages += count
            except:
                continue

        # 尝试获取最近的事件
        recent_events = []
        if user_sessions:
            for session in user_sessions[-3:]:  # 最近3个会话
                try:
                    events = chat_service.db.get_events(session)
                    recent_events.extend(events[-2:])  # 每个会话最多2个事件
                except:
                    continue

        # 尝试获取情绪记录
        emotion_records = []
        try:
            emotion_records = chat_service.db.get_emotion_history(
                state.user_id, limit=10
            )
        except:
            pass

    except Exception as e:
        print(f"获取数据时出错: {e}")
        session_count = 0
        total_messages = 0
        recent_events = []
        emotion_records = []

    basic_report = "📊 知己报告 - 基础心理健康分析\n"
    basic_report += "=" * 50 + "\n\n"

    basic_report += "🔍 报告基本信息\n"
    basic_report += f"• 用户ID: {state.user_id}\n"
    basic_report += f"• 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    basic_report += f"• 会话数量: {session_count}个\n"
    basic_report += f"• 消息总数: {total_messages}条\n"
    basic_report += f"• 记录事件: {len(recent_events)}个\n"
    basic_report += f"• 情绪记录: {len(emotion_records)}条\n\n"

    # 数据状态评估
    basic_report += "📝 数据状态评估\n"
    if total_messages < 10:
        basic_report += "• 当前处于咨询初期阶段，数据积累较少\n"
        basic_report += "• 建议继续保持交流，以便获得更准确的分析\n"
    elif total_messages < 30:
        basic_report += "• 已建立了初步的对话基础\n"
        basic_report += "• 数据正在积累中，分析准确性将逐步提升\n"
    else:
        basic_report += "• 已积累了丰富的对话数据\n"
        basic_report += "• 具备了进行深度分析的基础条件\n"
    basic_report += "\n"

    # 简要分析
    if recent_events:
        basic_report += "🎯 近期事件概览\n"
        event_types = {}
        for event in recent_events[-5:]:  # 最近5个事件
            event_type = event.get("primaryType", "其他")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        if event_types:
            basic_report += "主要关注领域:\n"
            for event_type, count in sorted(
                event_types.items(), key=lambda x: x[1], reverse=True
            ):
                type_name_map = {
                    "emotional": "情绪管理",
                    "behavioral": "行为模式",
                    "cognitive": "认知思考",
                    "interpersonal": "人际关系",
                    "physiological": "身心健康",
                    "lifeEvent": "生活事件",
                }
                display_name = type_name_map.get(event_type, event_type)
                basic_report += f"• {display_name}: {count}次记录\n"
            basic_report += "\n"

    # 情绪状态简析
    if emotion_records:
        basic_report += "😊 情绪状态简析\n"
        try:
            recent_emotions = emotion_records[:5]  # 最近5条
            avg_score = sum(
                float(e.get("emotion_score", 0)) for e in recent_emotions
            ) / len(recent_emotions)

            if avg_score >= 7:
                emotion_desc = "整体情绪状态较为积极"
            elif avg_score >= 5:
                emotion_desc = "情绪状态相对平稳"
            else:
                emotion_desc = "可能需要关注情绪调节"

            basic_report += f"• 近期情绪评分: {avg_score:.1f}/10\n"
            basic_report += f"• 状态评估: {emotion_desc}\n\n"
        except:
            basic_report += "• 情绪数据正在积累中\n\n"

    # 个性化建议
    basic_report += "💡 当前建议\n"
    if total_messages < 10:
        basic_report += "• 继续保持开放的交流态度，分享更多具体的感受和想法\n"
        basic_report += "• 可以尝试描述具体的生活场景和情绪体验\n"
    else:
        basic_report += "• 定期进行自我反思，关注情绪和行为模式的变化\n"
        basic_report += "• 继续记录重要的生活事件和情绪状态\n"

    basic_report += "• 建立良好的作息习惯，保持身心健康\n"
    basic_report += "• 如有需要，寻求专业心理咨询师的支持\n\n"

    # 系统说明
    basic_report += "📋 报告说明\n"
    basic_report += "本报告基于当前可用的对话和行为数据生成。由于数据有限，\n"
    basic_report += "这是一份基础版分析报告。随着交流的深入和数据的积累，\n"
    basic_report += "系统将能够提供更详细和个性化的分析报告。\n\n"

    basic_report += "如需获得更全面的分析，请继续保持对话并记录相关信息。\n"
    basic_report += "您的隐私和数据安全始终受到严格保护。"

    return basic_report


"""生成分析报告节点"""


def generate_analysis_report(state: OptimizedSessionState) -> OptimizedSessionState:
    start_time = datetime.now().timestamp()

    # 获取聊天服务实例
    chat_service = get_chat_service_instance()

    if state.need_analysis_report:
        print("🔄 开始生成知己报告...")

        # 检查分析服务是否可用
        if (
            not hasattr(chat_service, "analysis_service")
            or not chat_service.analysis_service
        ):
            print("⚠️ 分析服务不可用，生成基础报告")
            state.response = _generate_basic_report(state)
            state.processing_stage = "analysis_report_generated"
            state.stage_timings["analysis_report"] = (
                datetime.now().timestamp() - start_time
            )
            return state

        try:
            print("📊 调用分析服务生成详细报告...")
            # 生成用户分析报告
            report = chat_service.analysis_service.generate_user_report(
                user_id=state.user_id,
                session_ids=None,  # 自动获取所有会话
                time_period=30,  # 最近30天
            )

            if "error" not in report:
                print("✅ 详细报告生成成功")
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
                report_response += (
                    f"• 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                report_response += f"• 分析时间范围: 最近30天\n"
                report_response += (
                    f"• 分析会话数: {metadata.get('sessions_analyzed', 0)}\n"
                )
                report_response += f"• 事件总数: {metadata.get('total_events', 0)}\n"
                report_response += (
                    f"• 情绪记录数: {metadata.get('emotion_records', 0)}\n\n"
                )

                # === 2. 执行摘要 ===
                summary = ai_analysis.get("summary", {})
                if summary:
                    report_response += "🎯 执行摘要\n"
                    report_response += (
                        f"• 整体状态: {summary.get('overallStatus', '需要更多数据')}\n"
                    )
                    report_response += (
                        f"• 风险等级: {summary.get('riskLevel', '未评估')}\n"
                    )
                    report_response += (
                        f"• 进步趋势: {summary.get('progressTrend', '待观察')}\n\n"
                    )

                    # 关键发现
                    key_findings = summary.get("keyFindings", [])
                    if key_findings:
                        report_response += "🔍 关键发现\n"
                        for i, finding in enumerate(key_findings[:5], 1):
                            report_response += f"{i}. {finding}\n"
                        report_response += "\n"

                # === 3. 建议部分 ===
                recommendations = ai_analysis.get("recommendations", {})
                if recommendations:
                    report_response += "💡 专业建议\n"

                    immediate = recommendations.get("immediate", [])
                    if immediate:
                        report_response += "立即建议:\n"
                        for rec in immediate[:3]:
                            report_response += f"• {rec}\n"
                        report_response += "\n"

                    short_term = recommendations.get("shortTerm", [])
                    if short_term:
                        report_response += "短期建议:\n"
                        for rec in short_term[:3]:
                            report_response += f"• {rec}\n"
                        report_response += "\n"

                # 数据统计部分
                data_summary = report.get("data_summary", {})
                event_stats = data_summary.get("event_statistics", {})
                if event_stats.get("total_events", 0) > 0:
                    report_response += "📈 数据分析概览\n"
                    most_common = event_stats.get("most_common_types", [])
                    if most_common:
                        report_response += "主要事件类型:\n"
                        for event_type, count in most_common[:3]:
                            report_response += f"• {event_type}: {count}次\n"
                        report_response += "\n"

                report_response += "📝 说明\n"
                report_response += "本报告基于您最近30天的对话数据生成，旨在帮助您更好地了解自己的心理状态和行为模式。\n"
                report_response += "如需更详细的分析或专业建议，建议继续保持定期交流。"

                # 将报告作为响应内容
                state.response = report_response
                print("✅ 详细知己报告已生成")
            else:
                print(f"⚠️ 详细报告生成失败: {report.get('error')}")
                # 生成基础的报告
                state.response = _generate_basic_report(state)
                print("✅ 已生成基础知己报告")

        except Exception as e:
            print(f"❌ 分析报告生成错误: {e}")
            # 生成基础的报告
            state.response = _generate_basic_report(state)
            print("✅ 已生成基础知己报告（备用方案）")

    state.processing_stage = "analysis_report_generated"
    state.stage_timings["analysis_report"] = datetime.now().timestamp() - start_time

    return state


"""生成AI响应节点"""


def generate_response(state: OptimizedSessionState) -> OptimizedSessionState:
    start_time = datetime.now().timestamp()

    try:
        # 格式化历史记录
        chat_service = get_chat_service_instance()
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

        # 添加RAG上下文
        if state.has_rag_context and state.rag_context:
            additional_context += f"\n\n专业知识参考：{state.rag_context}"

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


"""后处理和数据保存节点"""


def postprocess_and_save(state: OptimizedSessionState) -> OptimizedSessionState:
    start_time = datetime.now().timestamp()

    try:
        # 获取chat_service实例
        chat_service = get_chat_service_instance()

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
    return "intent_analysis"


def route_after_intent(state: OptimizedSessionState) -> str:
    """根据意图识别结果进行路由"""
    if state.route_decision == "rag":
        return "rag_retrieval"
    elif state.route_decision == "web_search":
        return "web_search"
    else:
        return "context_build"


def should_update_plan_after_context(state: OptimizedSessionState) -> str:
    """上下文构建后检查是否需要更新计划"""
    # 简单的启发式：如果是问候语或简单回复，跳过计划更新
    simple_inputs = {"你好", "谢谢", "好的", "嗯", "是的", "不是"}
    if state.user_input in simple_inputs:
        state.skip_plan_update = True
        return "generate_response"
    return "plan_update"


def continue_after_rag(state: OptimizedSessionState) -> str:
    """RAG检索后的路由"""
    return "context_build"


def continue_after_web_search(state: OptimizedSessionState) -> str:
    """网络搜索后的路由"""
    return "context_build"


def should_update_plan(state: OptimizedSessionState) -> str:
    """检查是否需要更新计划"""
    # 简单的启发式：如果是问候语或简单回复，跳过计划更新
    simple_inputs = {"你好", "谢谢", "好的", "嗯", "是的", "不是"}
    if state.user_input in simple_inputs:
        state.skip_plan_update = True
        return "generate_response"
    return "plan_update"


def route_after_plan_update(state: OptimizedSessionState) -> str:
    """计划更新后的路由决策"""
    print(
        f"🔍 路由决策检查: need_analysis_report={state.need_analysis_report}, processing_stage={state.processing_stage}"
    )

    # 如果检测到知己报告请求，直接跳转到报告生成
    if state.need_analysis_report:
        print("🔄 路由到分析报告生成节点")
        return "analysis_report_node"

    print("🔄 路由到引导性询问节点")
    return "guided_inquiry"


def route_after_guided_inquiry(state: OptimizedSessionState) -> str:
    """引导性询问后的路由决策"""
    if state.need_pattern_analysis:
        return "pattern_analysis_node"
    return "generate_response"


def route_after_pattern_analysis(state: OptimizedSessionState) -> str:
    """模式分析后的路由决策"""
    if state.need_analysis_report:
        return "analysis_report_node"
    return "generate_response"


def route_after_analysis_report(state: OptimizedSessionState) -> str:
    """分析报告生成后的路由决策"""
    # 分析报告已生成，直接跳到后处理保存，不需要再调用generate_response
    return "postprocess_save"


# === 构建 LangGraph ===

# 创建工作流
workflow = StateGraph(OptimizedSessionState)

# 添加节点
workflow.add_node("preprocess", preprocess_input)
workflow.add_node("crisis_check", detect_crisis)
workflow.add_node("intent_analysis", intent_analysis)
workflow.add_node("context_build", build_context)
workflow.add_node("rag_retrieval", rag_retrieval)
workflow.add_node("web_search", web_search_retrieval)
workflow.add_node("plan_update", update_plan)
workflow.add_node("guided_inquiry", guided_inquiry_assessment)
workflow.add_node("pattern_analysis_node", pattern_analysis)
workflow.add_node("analysis_report_node", generate_analysis_report)
workflow.add_node("generate_response", generate_response)
workflow.add_node("postprocess_save", postprocess_and_save)

# 设置入口点
workflow.set_entry_point("preprocess")

# 添加边和条件路由
workflow.add_edge("preprocess", "crisis_check")
workflow.add_conditional_edges(
    "crisis_check",
    should_skip_to_response,
    {"intent_analysis": "intent_analysis", "postprocess_save": "postprocess_save"},
)
workflow.add_conditional_edges(
    "intent_analysis",
    route_after_intent,
    {
        "rag_retrieval": "rag_retrieval",
        "web_search": "web_search",
        "context_build": "context_build",
    },
)
workflow.add_conditional_edges(
    "rag_retrieval",
    continue_after_rag,
    {"context_build": "context_build"},
)
workflow.add_conditional_edges(
    "web_search",
    continue_after_web_search,
    {"context_build": "context_build"},
)
workflow.add_conditional_edges(
    "context_build",
    should_update_plan,
    {"plan_update": "plan_update", "generate_response": "generate_response"},
)
workflow.add_conditional_edges(
    "plan_update",
    route_after_plan_update,
    {
        "guided_inquiry": "guided_inquiry",
        "analysis_report_node": "analysis_report_node",
    },
)
workflow.add_conditional_edges(
    "guided_inquiry",
    route_after_guided_inquiry,
    {
        "pattern_analysis_node": "pattern_analysis_node",
        "generate_response": "generate_response",
    },
)
workflow.add_conditional_edges(
    "pattern_analysis_node",
    route_after_pattern_analysis,
    {
        "analysis_report_node": "analysis_report_node",
        "generate_response": "generate_response",
    },
)
workflow.add_conditional_edges(
    "analysis_report_node",
    route_after_analysis_report,
    {"postprocess_save": "postprocess_save"},
)
workflow.add_edge("generate_response", "postprocess_save")
workflow.add_edge("postprocess_save", END)

# 编译工作流
optimized_chat_app = workflow.compile()

# === 系统初始化函数 ===


def initialize_system():
    """
    系统启动时初始化所有组件
    注意：这个函数现在主要用于测试和独立运行，正常启动时由start.py管理
    """
    print("🔧 正在初始化系统组件...")

    # 预先初始化所有服务实例，避免在对话过程中初始化
    print("   📊 初始化数据库服务...")
    get_db_instance()

    print("   🚨 初始化危机检测器...")
    get_crisis_detector_instance()

    print("   🔍 初始化搜索服务...")
    get_search_service_instance()

    print("   💬 初始化聊天服务...")
    get_chat_service_instance()

    print("✅ 系统组件初始化完成")


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
            "rag_context": final_state.get("rag_context"),
            "has_rag_context": final_state.get("has_rag_context", False),
            "intent_result": final_state.get("intent_result", {}),
            "route_decision": final_state.get("route_decision", "direct_chat"),
            # 新增字段
            "inquiry_result": final_state.get("inquiry_result"),
            "need_guided_inquiry": final_state.get("need_guided_inquiry", False),
            "need_pattern_analysis": final_state.get("need_pattern_analysis", False),
            "need_analysis_report": final_state.get("need_analysis_report", False),
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
            "rag_context": None,
            "has_rag_context": False,
            "intent_result": {},
            "route_decision": "direct_chat",
            "inquiry_result": None,
            "need_guided_inquiry": False,
            "need_pattern_analysis": False,
            "need_analysis_report": False,
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


# === 模块级别的初始化 ===
# 当模块被导入时，预先初始化基础组件，但不初始化RAG相关组件
# RAG组件由start.py统一管理
if __name__ != "__main__":
    # 只在模块被导入时初始化基础组件，不在直接运行时初始化（避免在测试时重复初始化）
    print("🔧 正在初始化基础对话组件...")

    # 只预先初始化基础服务实例，不包括聊天服务（避免RAG重复初始化）
    print("   📊 初始化数据库服务...")
    get_db_instance()

    print("   🚨 初始化危机检测器...")
    get_crisis_detector_instance()

    print("   🔍 初始化搜索服务...")
    get_search_service_instance()

    print("✅ 基础对话组件初始化完成")
