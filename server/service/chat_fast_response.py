#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
心理咨询对话系统 - 快速响应版本

专注于解决响应速度问题的简化版本：
1. 减少不必要的LLM调用
2. 优化数据库操作
3. 智能缓存
4. 异步处理非关键路径
"""

import os
import json
import sys
from pathlib import Path
import time
from typing import Dict, List, Tuple, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
import re
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

# 快速响应状态模型
class FastSessionState(BaseModel):
    user_input: str
    user_id: str = "default_user"
    session_id: str | None = None
    response: str | None = None
    history: List[Dict[str, str]] = Field(default_factory=list)
    crisis_detected: bool = False
    crisis_reason: str | None = None
    emotion: str = "neutral"
    skip_plan: bool = False
    skip_search: bool = False
    processing_time: float = 0.0

# 快速危机检测器（使用缓存）
class FastCrisisDetector:
    def __init__(self):
        self.high_risk_keywords = {"自杀", "想死", "活不下去", "结束生命"}
        self.cache = {}
        self.cache_lock = threading.Lock()
    
    def check(self, text: str) -> Tuple[bool, str]:
        with self.cache_lock:
            if text in self.cache:
                return self.cache[text]
        
        # 快速关键词检测
        for keyword in self.high_risk_keywords:
            if keyword in text:
                result = (True, f"检测到高危词: '{keyword}'")
                with self.cache_lock:
                    self.cache[text] = result
                return result
        
        result = (False, "")
        with self.cache_lock:
            self.cache[text] = result
        return result

# 快速聊天服务
class FastChatService:
    def __init__(self, database: Database):
        self.db = database
        self.client = ChatOpenAI(
            model=os.environ.get("MODEL_NAME", "deepseek-chat"),
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("BASE_URL", "https://api.deepseek.com/v1"),
            temperature=float(os.environ.get("TEMPERATURE", "0.7")),
            max_tokens=int(os.environ.get("MAX_TOKENS", "800")),  # 减少token数
            timeout=25,  # 减少超时时间
        )
        
        # 简化的提示词
        self.prompt = """你是一位专业的心理咨询师。请给出简洁、有用的回复，专注于：
1. 共情和理解
2. 实用建议
3. 适当的问题引导

保持回复简洁但有温度。"""
        
        # 线程池用于后台任务
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # 响应缓存
        self.response_cache = {}
        self.cache_lock = threading.Lock()
    
    def get_cached_response(self, user_input: str) -> Optional[str]:
        """获取缓存的响应"""
        with self.cache_lock:
            return self.response_cache.get(user_input)
    
    def cache_response(self, user_input: str, response: str):
        """缓存响应"""
        with self.cache_lock:
            if len(self.response_cache) > 100:  # 限制缓存大小
                # 移除最旧的缓存
                oldest_key = next(iter(self.response_cache))
                del self.response_cache[oldest_key]
            self.response_cache[user_input] = response
    
    def should_use_simple_response(self, user_input: str) -> Optional[str]:
        """判断是否可以使用简单的预设响应"""
        simple_responses = {
            "你好": "你好！我是心理咨询师，很高兴为您服务。有什么我可以帮助您的吗？",
            "谢谢": "不用谢，我很高兴能帮助到您。还有其他需要聊的吗？",
            "好的": "好的，我明白了。还有什么想分享的吗？",
            "嗯": "我在听，请继续说。",
            "是的": "好的，我理解。请继续。",
            "再见": "再见！记住，我随时都在这里。祝您一切顺利！"
        }
        
        user_input_clean = user_input.strip()
        return simple_responses.get(user_input_clean)
    
    def extract_emotion(self, content: str) -> str:
        """快速情绪提取"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["开心", "高兴", "快乐", "很好"]):
            return "happy"
        elif any(word in content_lower for word in ["悲伤", "难过", "抑郁", "痛苦"]):
            return "sad"
        elif any(word in content_lower for word in ["生气", "愤怒", "烦躁"]):
            return "angry"
        elif any(word in content_lower for word in ["累", "疲惫", "困"]):
            return "sleepy"
        
        return "neutral"
    
    def async_save_data(self, user_id: str, session_id: str, user_input: str, response: str, emotion: str):
        """异步保存数据"""
        def save_task():
            try:
                # 计算情绪评分
                emotion_score = SnowNLP(user_input).sentiments * 2 - 1
                
                # 保存情绪评分
                self.db.save_emotion_score(user_id, session_id, emotion_score, emotion)
                
                # 更新用户画像
                self.db.save_user_profile(user_id, {
                    "last_interaction": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "recent_emotion_score": emotion_score,
                    "recent_emotion": emotion
                })
                
                # 偶尔保存到长期记忆
                if emotion_score < -0.5 or "困扰" in user_input or "问题" in user_input:
                    self.db.save_long_term_memory(user_id, f"用户: {user_input}\n咨询师: {response}")
                
            except Exception as e:
                print(f"Background save error: {e}")
        
        # 提交到线程池
        self.executor.submit(save_task)

# 初始化服务
db = Database()
crisis_detector = FastCrisisDetector()
chat_service = FastChatService(db)

# === LangGraph 节点（简化版） ===

def fast_preprocess(state: FastSessionState) -> FastSessionState:
    """快速预处理"""
    start_time = time.time()
    
    state.user_input = state.user_input.strip()
    state.session_id = state.session_id or state.user_id
    
    # 检查是否可以使用简单响应
    simple_response = chat_service.should_use_simple_response(state.user_input)
    if simple_response:
        state.response = simple_response
        state.skip_plan = True
        state.skip_search = True
        return state
    
    # 检查缓存
    cached_response = chat_service.get_cached_response(state.user_input)
    if cached_response:
        state.response = cached_response
        state.skip_plan = True
        state.skip_search = True
        return state
    
    state.processing_time += time.time() - start_time
    return state

def fast_crisis_check(state: FastSessionState) -> FastSessionState:
    """快速危机检测"""
    start_time = time.time()
    
    if state.response:  # 如果已有响应，跳过
        return state
    
    crisis, reason = crisis_detector.check(state.user_input)
    if crisis:
        state.crisis_detected = True
        state.crisis_reason = reason
        state.response = (
            f"⚠️ 我注意到您可能遇到了严重的情绪困扰。\n"
            f"请立即联系专业心理援助热线 400-161-9995，或寻求专业帮助。\n"
            f"您的生命很宝贵，请不要独自承受。"
        )
        state.skip_plan = True
        state.skip_search = True
    
    state.processing_time += time.time() - start_time
    return state

def fast_generate_response(state: FastSessionState) -> FastSessionState:
    """快速生成响应"""
    start_time = time.time()
    
    if state.response:  # 如果已有响应，跳过
        return state
    
    try:
        # 构建简化的消息
        messages = [
            {"role": "system", "content": chat_service.prompt},
            {"role": "user", "content": state.user_input}
        ]
        
        # 添加最近的历史（最多2条）
        if state.history:
            recent_history = state.history[-2:]
            for msg in recent_history:
                if msg["role"] == "user":
                    messages.insert(-1, {"role": "user", "content": msg["content"]})
                elif msg["role"] == "agent":
                    messages.insert(-1, {"role": "assistant", "content": msg["content"]})
        
        # 调用LLM
        response = chat_service.client.invoke(messages)
        reply = response.content.strip() or "我理解您的感受，请继续分享。"
        
        state.response = reply
        state.emotion = chat_service.extract_emotion(state.user_input)
        
        # 缓存响应
        chat_service.cache_response(state.user_input, reply)
        
    except Exception as e:
        state.response = f"抱歉，系统暂时出现问题。让我们换个话题聊聊吧。"
        print(f"LLM Error: {e}")
    
    state.processing_time += time.time() - start_time
    return state

def fast_postprocess(state: FastSessionState) -> FastSessionState:
    """快速后处理"""
    start_time = time.time()
    
    # 更新历史记录
    state.history.append({"role": "user", "content": state.user_input})
    state.history.append({"role": "agent", "content": state.response})
    
    # 保持历史记录数量在合理范围
    if len(state.history) > 20:
        state.history = state.history[-20:]
    
    # 异步保存数据
    chat_service.async_save_data(
        state.user_id, 
        state.session_id, 
        state.user_input, 
        state.response, 
        state.emotion
    )
    
    state.processing_time += time.time() - start_time
    return state

# === 路由函数 ===

def should_skip_llm(state: FastSessionState) -> str:
    """检查是否应该跳过LLM调用"""
    if state.response:
        return "postprocess"
    return "generate"

# === 构建快速工作流 ===

fast_workflow = StateGraph(FastSessionState)

# 添加节点
fast_workflow.add_node("preprocess", fast_preprocess)
fast_workflow.add_node("crisis_check", fast_crisis_check)
fast_workflow.add_node("generate", fast_generate_response)
fast_workflow.add_node("postprocess", fast_postprocess)

# 设置入口点
fast_workflow.set_entry_point("preprocess")

# 添加边
fast_workflow.add_edge("preprocess", "crisis_check")
fast_workflow.add_conditional_edges(
    "crisis_check",
    should_skip_llm,
    {
        "generate": "generate",
        "postprocess": "postprocess"
    }
)
fast_workflow.add_edge("generate", "postprocess")
fast_workflow.add_edge("postprocess", END)

# 编译工作流
fast_chat_app = fast_workflow.compile()

# === 主要接口 ===

def fast_chat(
    user_input: str,
    user_id: str = "default_user",
    session_id: str | None = None,
    history: List[Dict[str, str]] | None = None,
    show_timing: bool = False
) -> Dict[str, Any]:
    """
    快速聊天接口
    
    专注于速度优化的聊天功能
    """
    
    overall_start = time.time()
    
    # 初始化状态
    init_state = FastSessionState(
        user_input=user_input,
        user_id=user_id,
        session_id=session_id,
        history=history or []
    )
    
    try:
        # 运行工作流
        result = fast_chat_app.invoke(init_state)
        
        total_time = time.time() - overall_start
        
        # 构建响应
        response_data = {
            "response": result.get("response"),
            "emotion": result.get("emotion", "neutral"),
            "history": result.get("history", []),
            "crisis_detected": result.get("crisis_detected", False),
            "crisis_reason": result.get("crisis_reason"),
            "total_time": total_time
        }
        
        if show_timing:
            response_data["processing_time"] = result.get("processing_time", 0)
            response_data["llm_time"] = total_time - result.get("processing_time", 0)
        
        return response_data
        
    except Exception as e:
        total_time = time.time() - overall_start
        print(f"Fast chat error: {e}")
        return {
            "response": f"抱歉，处理出现问题。让我们重新开始吧。",
            "emotion": "neutral",
            "history": history or [],
            "crisis_detected": False,
            "crisis_reason": None,
            "total_time": total_time
        }

# === 性能测试函数 ===

def benchmark_fast_chat():
    """性能基准测试"""
    test_messages = [
        "你好",
        "我今天心情不好",
        "什么是焦虑症",
        "我该怎么办",
        "谢谢你的建议",
        "我感觉很沮丧，不知道该如何是好",
        "最近工作压力很大",
        "我需要专业帮助吗",
        "好的，我明白了",
        "再见"
    ]
    
    print("🚀 快速聊天系统性能测试")
    print("=" * 50)
    
    times = []
    for i, msg in enumerate(test_messages):
        print(f"\n📝 测试 {i+1}: {msg}")
        
        start = time.time()
        result = fast_chat(msg, show_timing=True)
        end = time.time()
        
        actual_time = end - start
        times.append(actual_time)
        
        print(f"  ✅ 总耗时: {actual_time:.2f}s")
        print(f"  📊 处理时间: {result.get('processing_time', 0):.2f}s")
        print(f"  🤖 LLM时间: {result.get('llm_time', 0):.2f}s")
        print(f"  💬 响应: {result['response'][:50]}...")
    
    # 统计
    print(f"\n📈 总体统计:")
    print(f"  平均响应时间: {sum(times)/len(times):.2f}s")
    print(f"  最快响应: {min(times):.2f}s")
    print(f"  最慢响应: {max(times):.2f}s")
    print(f"  总测试时间: {sum(times):.2f}s")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "benchmark":
        benchmark_fast_chat()
    else:
        print("🚀 快速心理咨询系统 (输入 '退出' 结束)")
        print("💡 输入 'time' 可查看详细耗时信息")
        
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
            
            show_timing = user_input.lower() == "time"
            if show_timing:
                user_input = input("请输入测试消息: ").strip()
            
            result = fast_chat(user_input, history=history, show_timing=show_timing)
            
            print(f"咨询师: {result['response']}")
            
            if show_timing:
                print(f"⚡ 响应时间: {result['total_time']:.2f}s")
                if 'processing_time' in result:
                    print(f"   处理时间: {result['processing_time']:.2f}s")
                    print(f"   LLM时间: {result['llm_time']:.2f}s")
            
            history = result['history']
