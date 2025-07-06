#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
心理咨询对话系统核心逻辑实现

该文件实现了一个基于AI的心理咨询对话服务，包含以下核心功能：
1. 会话状态管理 - 跟踪用户输入、历史对话、危机检测状态等
2. 用户画像存储 - 持久化保存用户相关信息
3. 记忆管理 - 维护长短期对话记忆
4. 危机检测 - 通过关键词匹配和情感分析识别潜在自杀风险
5. 聊天服务 - 处理对话逻辑、调用LLM模型生成回复
6. 行为模式分析 - 分析用户行为模式并提供咨询建议
7. 引导式询问 - 评估信息完整性并生成追问问题

技术栈：
- Python 3.8+
- LangChain - LLM交互和工作流管理
- Pydantic - 数据模型验证
- SnowNLP - 中文情感分析
- LangGraph - 对话流程管理
"""
import os
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from datetime import datetime
from typing import Dict, List, Tuple, Any
import re
import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from snownlp import SnowNLP

from utils.extract_json import extract_json

# 加载环境变量
load_dotenv()

# 会话状态数据模型
class SessionState(BaseModel):
    """
    跟踪单次对话会话中的所有状态信息，包括用户输入、历史对话、
    危机检测结果、搜索结果等关键数据
    """
    user_input: str  # 用户输入的文本内容
    response: str | None = None  # 系统生成的回复内容
    user_id: str = "default_user"  # 用户唯一标识符，默认为"default_user"
    history: List[Dict[str, str]] = Field(default_factory=list)  # 对话历史记录，包含用户和系统的消息
    session_id: str | None = None  # 会话ID，用于标识不同的对话会话
    user_profile: Dict[str, Any] = Field(default_factory=dict)  # 用户画像数据，包含用户相关信息
    crisis_detected: bool = False  # 是否检测到危机情况
    crisis_reason: str | None = None  # 危机检测的原因说明
    search_results: str | None = None  # 搜索结果内容
    plan: Dict[str, Any] = Field(default_factory=dict)  # 对话计划，包含当前阶段和进度等信息
    pattern_analysis: Dict[str, Any] | None = None  # 行为模式分析结果
    inquiry_result: Dict[str, Any] | None = None  # 引导性询问评估结果

# 用户画像存储管理类
class UserProfileStore:
    """
    负责持久化存储和管理用户画像数据，包括最后交互时间、情绪评分等
    数据存储在JSON文件中，支持用户画像的获取和更新操作
    """
    _PATH = os.path.join(os.path.dirname(__file__), "../data/user_profiles.json")
   # 初始化用户画像存储系统
    def __init__(self):
        self._profiles: Dict[str, Dict[str, Any]] = {}
        os.makedirs(os.path.dirname(self._PATH), exist_ok=True)
        if os.path.exists(self._PATH):
            # 尝试从JSON文件加载已有用户画像
            try:
                with open(self._PATH, "r", encoding="utf-8") as fp:
                    self._profiles = json.load(fp)
            except Exception:
                self._profiles = {}
    # 获取指定用户的画像数据
    def get(self, uid: str) -> Dict[str, Any]:
        return self._profiles.get(uid, {})
    # 更新或插入用户画像数据
    def upsert(self, uid: str, data: Dict[str, Any]):
        self._profiles.setdefault(uid, {}).update(data)
        try:
            with open(self._PATH, "w", encoding="utf-8") as fp:
                json.dump(self._profiles, fp, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存用户画像失败: {e}")

# 对话记忆存储管理类
class MemoryStore:
    """
    维护用户的长短期对话记忆，长期记忆持久化存储在JSON文件中，
    短期记忆保存在内存中并限制长度。提供记忆上下文构建功能。
    """
    _PATH = os.path.join(os.path.dirname(__file__), "../data/long_term_memory.json")

    def __init__(self):
        # 长期记忆
        self._long: Dict[str, List[Dict[str, str]]] = {}
        # 短期记忆
        self._short: Dict[str, List[Dict[str, str]]] = {}
        os.makedirs(os.path.dirname(self._PATH), exist_ok=True)
        if os.path.exists(self._PATH):
            try:
                with open(self._PATH, "r", encoding="utf-8") as fp:
                    self._long = json.load(fp)
            except Exception:
                self._long = {}

    # 为内容添加时间戳
    @staticmethod
    def _stamp(content: str) -> Dict[str, str]:
        return {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "content": content}

    # 构建上下文字符串，组合最近k条长期记忆与全部短期记忆
    def context(self, uid: str, k: int = 5) -> str:
        ctx = self._long.get(uid, [])[-k:] + self._short.get(uid, [])
        return "\n".join(f"{c['time']}: {c['content']}" for c in ctx)

    # 添加内容到记忆系统
    def add(self, uid: str, content: str, *, long_term: bool = False):
        # 长期记忆
        if long_term:
            self._long.setdefault(uid, []).append(self._stamp(content))
            try:
                with open(self._PATH, "w", encoding="utf-8") as fp:
                    json.dump(self._long, fp, indent=2, ensure_ascii=False)
            except Exception:
                pass
        # 短期记忆
        else:
            self._short.setdefault(uid, []).append(self._stamp(content))
            if len(self._short[uid]) > 20:
                self._short[uid].pop(0)

# 危机检测类
class CrisisDetector:
    """
    通过关键词匹配和情感分析识别用户潜在的自杀或自伤风险。
    使用SnowNLP进行情感极性分析，结合高危关键词列表进行危机判断。
    """
    _KEYWORDS = {"自杀", "想死", "活不下去", "结束生命", "杀人", "伤害自己", "受不了", "绝望", "崩溃"}
    _THRESH = -0.8  # 调整阈值，避免过度敏感

    def check(self, text: str) -> Tuple[bool, str | None]:
        # 先检查关键词
        for kw in self._KEYWORDS:
            if kw in text:
                return True, f"检测到高危词: '{kw}'"
        
        # 只有在包含情绪相关词汇时才进行情感分析
        emotion_indicators = ["感到", "觉得", "很", "非常", "特别", "心情", "情绪", "难受", "痛苦", "无助"]
        if any(indicator in text for indicator in emotion_indicators):
            polarity = SnowNLP(text).sentiments * 2 - 1
            if polarity <= self._THRESH:
                return True, f"情感极性过低 (polarity={polarity:.2f})"
        
        return False, None

# 聊天服务核心类
class ChatService:
    """
    实现心理咨询对话的核心逻辑，包括：
    - 加载和管理各类提示模板
    - 调用LLM模型生成回复
    - 评估信息完整性并生成引导性问题
    - 分析用户行为模式
    - 管理对话计划和上下文
    """
    def __init__(self):
        self.model = os.environ.get("MODEL_NAME", "deepseek-chat")
        self.client = ChatOpenAI(
            model=self.model,
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("BASE_URL", "https://api.deepseek.com/v1"),
            temperature=float(os.environ.get("TEMPERATURE", "0.7")),
            max_tokens=int(os.environ.get("MAX_TOKENS", "1000")),
            timeout=40,
        )
        
        self.enable_guided_inquiry = os.environ.get("ENABLE_GUIDED_INQUIRY", "true").lower() == "true"
        self.enable_pattern_analysis = os.environ.get("ENABLE_PATTERN_ANALYSIS", "true").lower() == "true"
        
        self.prompt_template = self._load_prompt_template()
        self.planning_prompt = self._load_planning_prompt()
        self.guided_inquiry_prompt = self._load_guided_inquiry_prompt()
        self.pattern_analysis_prompt = self._load_pattern_analysis_prompt()
        
        self.plans_dir = os.path.join(os.path.dirname(__file__), "../data/plans")
        self.patterns_dir = os.path.join(os.path.dirname(__file__), "../data/patterns")
        os.makedirs(self.plans_dir, exist_ok=True)
        os.makedirs(self.patterns_dir, exist_ok=True)

    # 加载心理咨询师提示模板
    def _load_prompt_template(self):
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
            希望这些建议对你有所帮助！
            """
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(default_prompt)
            return default_prompt

        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    # 加载对话计划提示模板
    def _load_planning_prompt(self):
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "planning_prompt.txt")
        if not os.path.exists(prompt_file):
            raise FileNotFoundError("Planning prompt file not found")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    # 加载引导性询问提示模板
    def _load_guided_inquiry_prompt(self):
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "guided_inquiry_prompt.txt")
        if not os.path.exists(prompt_file):
            raise FileNotFoundError("Guided inquiry prompt file not found")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    # 加载行为模式分析提示模板
    def _load_pattern_analysis_prompt(self):
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "pattern_analysis_prompt.txt")
        if not os.path.exists(prompt_file):
            raise FileNotFoundError("Pattern analysis prompt file not found")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    # 获取会话计划
    def _get_plan(self, session_id):
        plan_file = os.path.join(self.plans_dir, f"{session_id}.json")
        if os.path.exists(plan_file):
            with open(plan_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    # 保存会话计划
    def _save_plan(self, session_id, plan):
        plan_file = os.path.join(self.plans_dir, f"{session_id}.json")
        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)

    # 获取行为模式分析结果
    def _get_pattern(self, session_id):
        pattern_file = os.path.join(self.patterns_dir, f"{session_id}.json")
        if os.path.exists(pattern_file):
            with open(pattern_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    # 保存行为模式分析结果
    def _save_pattern(self, session_id, pattern):
        pattern_file = os.path.join(self.patterns_dir, f"{session_id}.json")
        with open(pattern_file, "w", encoding="utf-8") as f:
            json.dump(pattern, f, ensure_ascii=False, indent=2)

    # 手动解析引导性询问结果
    def _parse_inquiry_manually(self, text):
        try:
            result = {
                "need_inquiry": True,
                "current_stage": "基础情况了解",
                "missing_info": [],
                "suggested_questions": [],
                "information_completeness": 50,
                "reason": "手动解析结果"
            }
            
            completeness_match = re.search(r'信息完整[度性]?[：:]\s*(\d+)%?', text)
            if completeness_match:
                result["information_completeness"] = int(completeness_match.group(1))
            
            stage_match = re.search(r'当前阶段[：:]\s*([^\n]+)', text)
            if stage_match:
                result["current_stage"] = stage_match.group(1).strip()
            
            questions = re.findall(r'[12]\.?\s*([^？?]*[？?])', text)
            if questions:
                result["suggested_questions"] = [q.strip() for q in questions[:2]]
            
            if result["information_completeness"] >= 80:
                result["need_inquiry"] = False
                result["current_stage"] = "信息充分"
            
            return result
        except Exception as e:
            print(f"Manual parsing failed: {e}")
            return None

    # 手动解析行为模式分析结果
    def _parse_pattern_manually(self, text):
        try:
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

    # 评估信息完整性
    def _assess_information_completeness(self, session_id, message, history):
        """
        Args:
            session_id: 会话ID
            message: 当前用户消息
            history: 历史消息列表

        Returns:
            dict: 引导性询问结果
        """
        try:
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
            
            inquiry_result = extract_json(reply)
            if inquiry_result is None:
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

    # 分析用户行为模式
    def _analyze_behavior_pattern(self, session_id, collected_info):
        """
        Args:
            session_id: 会话ID
            collected_info: 收集到的完整信息

        Returns:
            dict: 行为模式分析结果
        """
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
            
            pattern_analysis = extract_json(reply)
            if pattern_analysis is None:
                pattern_analysis = self._parse_pattern_manually(reply)
                if pattern_analysis is None:
                    return None

            pattern_analysis["analyzed_at"] = datetime.now().isoformat()
            pattern_analysis["session_id"] = session_id
            self._save_pattern(session_id, pattern_analysis)
            return pattern_analysis
        except Exception as e:
            print(f"Error analyzing behavior pattern: {str(e)}")
            return None

    # 更新对话计划
    def _update_plan(self, session_id, message, history):
        """
        Args:
            session_id: 会话ID
            message: 当前用户消息
            history: 历史消息列表

        Returns:
            dict: 更新后的对话计划
        """
        plan = self._get_plan(session_id)
        if not plan:
            plan = {
                "session_id": session_id,
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
                    "pattern_analyzed": False
                }
            }

        messages = [
            {"role": "system", "content": self.planning_prompt},
            {
                "role": "user",
                "content": f"Current plan: {json.dumps(plan, ensure_ascii=False)}\n\nCurrent message: {message}\n\nHistory: {json.dumps(history, ensure_ascii=False)}",
            },
        ]

        response = self.client.invoke(messages)
        reply = response.content.strip()

        try:
            updated_plan = extract_json(reply)
            if updated_plan is None:
                plan["current_state"]["last_updated"] = datetime.now().isoformat()
                return plan

            if "inquiry_status" not in updated_plan:
                updated_plan["inquiry_status"] = plan.get("inquiry_status", {
                    "stage": "初始阶段",
                    "information_completeness": 0,
                    "collected_info": {},
                    "pattern_analyzed": False
                })

            self._save_plan(session_id, updated_plan)
            return updated_plan
        except Exception as e:
            print(f"Error updating plan: {str(e)}")
            return plan

    # 格式化对话历史
    def _format_history(self, history):
        """将历史记录格式化为OpenAI API需要的格式
        Args:
            history: 历史消息列表

        Returns:
            list: 格式化后的消息列表
        """
        formatted_messages = []
        formatted_messages.append({"role": "system", "content": self.prompt_template})

        for msg in history:
            if msg["role"] == "user":
                formatted_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "agent":
                formatted_messages.append(
                    {"role": "assistant", "content": msg["content"]}
                )

        return formatted_messages

    # 提取用户情绪
    def _extract_emotion(self, content):
        """
        Args:
            content: AI回复内容

        Returns:
            tuple: (清理后的内容, 情绪)
        """
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

        content_lower = content.lower()

        if any(
            word in content_lower
            for word in ["开心", "高兴", "快乐", "很好", "很棒", "兴奋"]
        ):
            return content, "happy"
        elif any(
            word in content_lower for word in ["悲伤", "难过", "伤心", "痛苦", "抑郁"]
        ):
            return content, "sad"
        elif any(
            word in content_lower for word in ["生气", "愤怒", "恼火", "烦躁", "烦恼"]
        ):
            return content, "angry"
        elif any(
            word in content_lower for word in ["累了", "疲惫", "困", "睡觉", "休息"]
        ):
            return content, "sleepy"

        return content, "neutral"

    # 为控制器层提供的接口方法
    def get_response(self, message: str, history: List[Dict[str, str]] = None, session_id: str = None) -> Dict[str, Any]:
        """
        为控制器层提供的统一接口方法，调用chat函数并返回格式化的响应
        
        Args:
            message: 用户输入消息
            history: 对话历史记录
            session_id: 会话ID
            
        Returns:
            dict: 包含content和emotion的响应字典
        """
        try:
            # 调用chat函数获取完整响应
            result = chat(message, session_id=session_id, history=history or [])
            
            # 提取并格式化响应内容
            response_content = result.get("response", "抱歉，暂时无法回答。")
            
            # 提取情绪信息
            clean_content, emotion = self._extract_emotion(response_content)
            
            return {
                "content": clean_content,
                "emotion": emotion,
                "crisis_detected": result.get("crisis_detected", False),
                "crisis_reason": result.get("crisis_reason"),
                "search_results": result.get("search_results"),
                "pattern_analysis": result.get("pattern_analysis")
            }
            
        except Exception as e:
            print(f"Error in get_response: {str(e)}")
            return {
                "content": f"对话处理出错: {str(e)}",
                "emotion": "neutral",
                "crisis_detected": False
            }

# 初始化服务和存储
profile_store = UserProfileStore()
memory_store = MemoryStore()
crisis_detector = CrisisDetector()
chat_service = ChatService()

# 搜索功能
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SEARCH_TRIGGERS = ["什么是", "如何", "为什么", "怎么办", "最新", "现在", "今天", "新闻", "天气"]

# 使用SERPAPI进行网络搜索
def serp_search(query: str, k: int = 3) -> str:
    """
    当用户输入包含特定触发词（如"什么是"、"如何"等）时调用，
    获取相关搜索结果并格式化返回。需要SERPAPI_KEY环境变量。

    参数:
        query: 搜索查询字符串
        k: 返回结果数量，默认为3

    返回:
        格式化的搜索结果字符串，或错误信息
    """
    if not SERPAPI_KEY:
        return "⚠️ [搜索功能未启用: 未设置 SERPAPI_KEY]"
    try:
        r = requests.get(
            "https://serpapi.com/search",
            params={"q": query, "api_key": SERPAPI_KEY, "hl": "zh-cn"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        snippets: List[str] = []
        for item in data.get("organic_results", [])[:k]:
            snippets.append(
                f"标题: {item.get('title','').strip()}\n摘要: {item.get('snippet','').strip()}\n链接: {item.get('link','').strip()}"
            )
        return "\n\n".join(snippets) if snippets else "未找到相关搜索结果"
    except Exception as e:
        return f"搜索出错: {e}"

# LangGraph节点函数
def process_input(state: SessionState) -> SessionState:
    """LangGraph节点函数 - 处理用户输入

    实现对话流程的核心处理逻辑，包括：
    1. 危机检测
    2. 构建对话上下文
    3. 更新对话计划
    4. 评估信息完整性
    5. 分析行为模式
    6. 调用LLM生成回复
    7. 更新记忆和用户画像

    参数:
        state: 当前会话状态对象

    返回:
        更新后的会话状态对象
    """
    uid, raw = state.user_id, state.user_input.strip()
    session_id = state.session_id or uid
    state.session_id = session_id

    # 危机检测
    crisis, reason = crisis_detector.check(raw)
    if crisis:
        state.response = (
            f"⚠️ 检测到潜在情绪危机: {reason}\n\n"
            "请立即联系专业人士或拨打心理援助热线 400-161-9995。\n"
            "您并不孤单，我们关心您。"
        )
        state.crisis_detected = True
        state.crisis_reason = reason
        memory_store.add(uid, f"[CRISIS] {raw} – {reason}", long_term=True)
        return state

    # 构建上下文
    profile = profile_store.get(uid)
    mem_ctx = memory_store.context(uid)
    search_out = serp_search(raw) if any(t in raw for t in SEARCH_TRIGGERS) else None
    state.search_results = search_out

    # 更新对话计划
    plan = chat_service._update_plan(session_id, raw, state.history)
    state.plan = plan

    # 评估信息完整性
    inquiry_result = None
    if (chat_service.enable_guided_inquiry and 
        len(state.history) <= 10 and 
        not plan.get("inquiry_status", {}).get("pattern_analyzed", False)):
        inquiry_result = chat_service._assess_information_completeness(session_id, raw, state.history)
        state.inquiry_result = inquiry_result
        
        if inquiry_result:
            plan["inquiry_status"]["information_completeness"] = inquiry_result.get("information_completeness", 0)
            plan["inquiry_status"]["stage"] = inquiry_result.get("current_stage", "初始阶段")
            chat_service._save_plan(session_id, plan)
            state.plan = plan

    # 行为模式分析
    pattern_analysis = None
    should_analyze = (
        chat_service.enable_pattern_analysis and
        (inquiry_result and inquiry_result.get("information_completeness", 0) >= 80 or 
         len(state.history) >= 4)
    )
    
    if should_analyze and not plan.get("inquiry_status", {}).get("pattern_analyzed", False):
        collected_info = {
            "session_id": session_id,
            "conversation_history": state.history + [{"role": "user", "content": raw}],
            "plan_context": plan.get("context", {}),
            "inquiry_stage": inquiry_result.get("current_stage", "信息充分") if inquiry_result else "信息充分",
            "inquiry_result": inquiry_result
        }
        
        pattern_analysis = chat_service._analyze_behavior_pattern(session_id, collected_info)
        if pattern_analysis:
            plan["inquiry_status"]["pattern_analyzed"] = True
            plan["inquiry_status"]["pattern_analysis_completed_at"] = datetime.now().isoformat()
            chat_service._save_plan(session_id, plan)
            state.plan = plan
            state.pattern_analysis = pattern_analysis

    # 格式化历史记录
    messages = chat_service._format_history(state.history)
    messages.append({"role": "user", "content": raw})

    # 准备系统提示的附加信息
    additional_context = f"\n\n当前对话计划：{json.dumps(plan, ensure_ascii=False)}"
    
    if inquiry_result:
        additional_context += f"\n\n引导性询问评估：{json.dumps(inquiry_result, ensure_ascii=False)}"
        if inquiry_result.get("need_inquiry", False):
            suggested_questions = inquiry_result.get("suggested_questions", [])
            if suggested_questions:
                additional_context += f"\n\n建议的引导性问题：{suggested_questions}"
                additional_context += "\n\n请在给出共情回应后，适当地提出1-2个引导性问题来了解更多信息。"

    if pattern_analysis:
        additional_context += f"\n\n行为模式分析已完成，关键洞察：{pattern_analysis.get('key_insights', [])}"
        additional_context += f"\n\n咨询建议：{pattern_analysis.get('consultation_recommendations', [])}"

    if search_out:
        additional_context += f"\n\n[重要] 用户询问了需要搜索的信息，以下是相关搜索结果，请在回复中先简要提供用户所需的信息，然后再进行心理咨询引导：\n相关搜索信息：{search_out}"

    messages[0]["content"] += additional_context

    # 调用LLM
    try:
        ai_msg = chat_service.client.invoke(messages)
        reply = ai_msg.content.strip() or "抱歉，暂时无法回答。"
    except Exception as e:
        reply = f"对话处理出错: {e}"

    # 提取情绪
    clean_content, emotion = chat_service._extract_emotion(reply)
    state.response = clean_content

    # 更新记忆
    total = len(memory_store._short.get(uid, [])) + len(memory_store._long.get(uid, []))
    long_flag = ((total + 1) % 3 == 0)
    memory_store.add(uid, f"用户: {raw}\n咨询师: {reply}", long_term=long_flag)

    # 更新用户画像
    emotion_score = SnowNLP(raw).sentiments * 2 - 1
    profile_store.upsert(uid, {"last_interaction": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "recent_emotion_score": emotion_score})
    state.user_profile = profile_store.get(uid)

    # 更新历史记录
    state.history.append({"role": "user", "content": raw})
    state.history.append({"role": "agent", "content": clean_content})

    return state

# 构建LangGraph
workflow = StateGraph(SessionState)
workflow.add_node("process_input", process_input)
workflow.set_entry_point("process_input")
workflow.add_edge("process_input", END)

# 编译应用
chat_app = workflow.compile()

def chat(user_input: str, user_id: str = "default_user", session_id: str | None = None, history: List[Dict[str, str]] | None = None) -> Dict[str, Any]:
    """聊天接口函数

    对外提供的聊天接口，初始化会话状态并调用LangGraph应用处理输入。

    参数:
        user_input: 用户输入文本
        user_id: 用户唯一标识，默认为"default_user"
        session_id: 会话ID，可选
        history: 历史对话列表，可选

    返回:
        包含回复、历史记录等信息的字典
    """
    init_state = SessionState(
        user_input=user_input,
        user_id=user_id,
        session_id=session_id,
        history=history or []
    )
    result = chat_app.invoke(init_state)
    # LangGraph返回的是字典，包含所有节点的最终状态
    final_state = result if isinstance(result, dict) else result
    
    return {
        "response": final_state.get("response"),
        "history": final_state.get("history", []),
        "crisis_detected": final_state.get("crisis_detected", False),
        "crisis_reason": final_state.get("crisis_reason"),
        "search_results": final_state.get("search_results"),
        "pattern_analysis": final_state.get("pattern_analysis")
    }

if __name__ == "__main__":
    print("🩺 心理咨询对话系统 (输入 '退出' 结束)")
    history = []
    while True:
        try:
            u_in = input("您: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见！")
            break
        if u_in.lower() in {"退出", "quit", "q"}:
            print("👋 再见！祝您一切顺利。")
            break
        result = chat(u_in, history=history)
        print(f"咨询师: {result['response']}")
        history = result['history']