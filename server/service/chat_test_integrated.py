#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
心理咨询对话系统核心逻辑实现（集成版）

该版本使用统一的Database类来管理所有数据，包括：
1. 会话状态管理
2. 用户画像存储
3. 长短期记忆管理
4. 情绪评分记录
5. 行为模式分析
6. 对话计划管理

优势：
- 统一的数据管理接口
- 线程安全的数据访问
- 更好的数据一致性
- 简化的错误处理
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
from dao.database import Database

# 加载环境变量
load_dotenv()

# 会话状态数据模型
class SessionState(BaseModel):
    user_input: str
    response: str | None = None
    user_id: str = "default_user"
    history: List[Dict[str, str]] = Field(default_factory=list)
    session_id: str | None = None
    user_profile: Dict[str, Any] = Field(default_factory=dict)
    crisis_detected: bool = False
    crisis_reason: str | None = None
    search_results: str | None = None
    plan: Dict[str, Any] = Field(default_factory=dict)
    pattern_analysis: Dict[str, Any] | None = None
    inquiry_result: Dict[str, Any] | None = None

# 危机检测类
class CrisisDetector:
    _KEYWORDS = {"自杀", "想死", "活不下去", "结束生命", "杀人", "伤害自己", "受不了", "绝望", "崩溃"}
    _THRESH = -0.3

    def check(self, text: str) -> Tuple[bool, str | None]:
        for kw in self._KEYWORDS:
            if kw in text:
                return True, f"检测到高危词: '{kw}'"
        polarity = SnowNLP(text).sentiments * 2 - 1
        if polarity <= self._THRESH:
            return True, f"情感极性过低 (polarity={polarity:.2f})"
        return False, None

# 集成版聊天服务核心类
class ChatService:
    def __init__(self, database: Database):
        self.db = database  # 使用统一的数据库实例
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
希望这些建议对你有所帮助！"
"""
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(default_prompt)
            return default_prompt

        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _load_planning_prompt(self):
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "planning_prompt.txt")
        if not os.path.exists(prompt_file):
            raise FileNotFoundError("Planning prompt file not found")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _load_guided_inquiry_prompt(self):
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "guided_inquiry_prompt.txt")
        if not os.path.exists(prompt_file):
            raise FileNotFoundError("Guided inquiry prompt file not found")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _load_pattern_analysis_prompt(self):
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "pattern_analysis_prompt.txt")
        if not os.path.exists(prompt_file):
            raise FileNotFoundError("Pattern analysis prompt file not found")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def save_memory(self, user_id: str, content: str, is_long_term: bool = False):
        """保存记忆到数据库"""
        if is_long_term:
            self.db.save_long_term_memory(user_id, content)
        # 短期记忆可以通过其他方式管理，或者扩展Database类支持

    def get_memory_context(self, user_id: str, k: int = 5) -> str:
        """获取记忆上下文"""
        long_term_memories = self.db.get_long_term_memory(user_id, k)
        return "\n".join(f"{m['time']}: {m['content']}" for m in long_term_memories)

    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """更新用户画像"""
        self.db.save_user_profile(user_id, profile_data)

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户画像"""
        return self.db.get_user_profile(user_id)

    def save_emotion_score(self, user_id: str, session_id: str, emotion_score: float, emotion_category: str = None):
        """保存情绪评分"""
        self.db.save_emotion_score(user_id, session_id, emotion_score, emotion_category)

    def _update_plan(self, session_id: str, message: str, history: List[Dict[str, str]]):
        """更新对话计划"""
        plan = self.db.get_session_plan(session_id)
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

            self.db.save_session_plan(session_id, updated_plan)
            return updated_plan
        except Exception as e:
            print(f"Error updating plan: {str(e)}")
            return plan

    def _analyze_behavior_pattern(self, session_id: str, collected_info: Dict[str, Any]):
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
            
            pattern_analysis = extract_json(reply)
            if pattern_analysis is None:
                return None

            pattern_analysis["analyzed_at"] = datetime.now().isoformat()
            pattern_analysis["session_id"] = session_id
            self.db.save_pattern_analysis(session_id, pattern_analysis)
            return pattern_analysis
        except Exception as e:
            print(f"Error analyzing behavior pattern: {str(e)}")
            return None

    def _format_history(self, history: List[Dict[str, str]]):
        """格式化对话历史"""
        formatted_messages = []
        formatted_messages.append({"role": "system", "content": self.prompt_template})

        for msg in history:
            if msg["role"] == "user":
                formatted_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "agent":
                formatted_messages.append({"role": "assistant", "content": msg["content"]})

        return formatted_messages

    def _extract_emotion(self, content: str):
        """提取情绪信息"""
        emotion_match = re.search(r"#(happy|sad|angry|sleepy|neutral)\b", content, re.IGNORECASE)

        if emotion_match:
            emotion = emotion_match.group(1).lower()
            clean_content = re.sub(r"\s*#(happy|sad|angry|sleepy|neutral)\b", "", content, flags=re.IGNORECASE)
            return clean_content, emotion

        content_lower = content.lower()

        if any(word in content_lower for word in ["开心", "高兴", "快乐", "很好", "很棒", "兴奋"]):
            return content, "happy"
        elif any(word in content_lower for word in ["悲伤", "难过", "伤心", "痛苦", "抑郁"]):
            return content, "sad"
        elif any(word in content_lower for word in ["生气", "愤怒", "恼火", "烦躁", "烦恼"]):
            return content, "angry"
        elif any(word in content_lower for word in ["累了", "疲惫", "困", "睡觉", "休息"]):
            return content, "sleepy"

        return content, "neutral"

    def get_response(self, message: str, history: List[Dict[str, str]] = None, session_id: str = None) -> Dict[str, Any]:
        """获取AI回复（集成版）"""
        try:
            user_id = "default_user"  # 可以根据需要动态设置
            
            # 调用chat函数获取完整响应
            result = chat(message, user_id=user_id, session_id=session_id, history=history or [])
            
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
db = Database()
crisis_detector = CrisisDetector()
chat_service = ChatService(db)

# 搜索功能
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SEARCH_TRIGGERS = [
    "什么是", "如何", "为什么", "怎么办", "最新", "现在", "今天", "新闻", "天气",
    "告诉我", "介绍", "说说", "讲讲", "了解", "关于", "活动", "事件", "情况"
]

def serp_search(query: str, k: int = 3) -> str:
    """网络搜索功能"""
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

def process_input(state: SessionState) -> SessionState:
    """处理用户输入（集成版）"""
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
        # 保存危机记录到长期记忆
        chat_service.save_memory(uid, f"[CRISIS] {raw} – {reason}", is_long_term=True)
        return state

    # 构建上下文
    profile = chat_service.get_user_profile(uid)
    mem_ctx = chat_service.get_memory_context(uid)
    search_out = serp_search(raw) if any(t in raw for t in SEARCH_TRIGGERS) else None
    state.search_results = search_out

    # 更新对话计划
    plan = chat_service._update_plan(session_id, raw, state.history)
    state.plan = plan

    # 格式化历史记录
    messages = chat_service._format_history(state.history)
    messages.append({"role": "user", "content": raw})

    # 准备系统提示的附加信息
    additional_context = f"\n\n当前对话计划：{json.dumps(plan, ensure_ascii=False)}"
    
    if search_out:
        additional_context += f"\n\n相关搜索信息：{search_out}"

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

    # 保存记忆（每3次对话保存一次到长期记忆）
    emotion_history = db.get_emotion_history(uid)
    is_long_term = (len(emotion_history) + 1) % 3 == 0
    chat_service.save_memory(uid, f"用户: {raw}\n咨询师: {reply}", is_long_term=is_long_term)

    # 更新用户画像和情绪评分
    emotion_score = SnowNLP(raw).sentiments * 2 - 1
    chat_service.update_user_profile(uid, {
        "last_interaction": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recent_emotion_score": emotion_score
    })
    chat_service.save_emotion_score(uid, session_id, emotion_score, emotion)
    
    state.user_profile = chat_service.get_user_profile(uid)

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
    """聊天接口函数（集成版）"""
    init_state = SessionState(
        user_input=user_input,
        user_id=user_id,
        session_id=session_id,
        history=history or []
    )
    result = chat_app.invoke(init_state)
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
    print("🩺 心理咨询对话系统 (集成版) (输入 '退出' 结束)")
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
