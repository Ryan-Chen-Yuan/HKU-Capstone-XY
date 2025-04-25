#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from openai import OpenAI
import re


class ChatService:
    """聊天服务，负责调用OpenAI API获取AI回复"""

    def __init__(self, model="Meta-Llama-3.1-8B-Instruct"):
        """初始化聊天服务

        Args:
            model: OpenAI模型名称
        """
        self.model = model
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("BASE_URL"),
        )
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self):
        """加载咨询师Prompt模板"""
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        os.makedirs(prompt_dir, exist_ok=True)

        prompt_file = os.path.join(prompt_dir, "counselor_prompt.txt")

        # 如果模板文件不存在，创建默认模板
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

        # 读取模板文件
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _format_history(self, history):
        """将历史记录格式化为OpenAI API需要的格式

        Args:
            history: 历史消息列表

        Returns:
            list: 格式化后的消息列表
        """
        formatted_messages = []

        # 系统提示
        formatted_messages.append({"role": "system", "content": self.prompt_template})

        # 历史消息
        for msg in history:
            if msg["role"] == "user":
                formatted_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "agent":
                formatted_messages.append(
                    {"role": "assistant", "content": msg["content"]}
                )

        return formatted_messages

    def _extract_emotion(self, content):
        """从AI回复中提取情绪标签

        Args:
            content: AI回复内容

        Returns:
            tuple: (清理后的内容, 情绪)
        """
        # 查找情绪标签
        emotion_match = re.search(
            r"#(happy|sad|angry|sleepy|neutral)\b", content, re.IGNORECASE
        )

        if emotion_match:
            emotion = emotion_match.group(1).lower()
            # 从内容中移除情绪标签
            clean_content = re.sub(
                r"\s*#(happy|sad|angry|sleepy|neutral)\b",
                "",
                content,
                flags=re.IGNORECASE,
            )
            return clean_content, emotion

        # 如果没有明确的情绪标签，尝试自动分析内容
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

        # 默认情绪
        return content, "neutral"

    def get_response(self, message, history=None):
        """获取AI回复

        Args:
            message: 用户消息
            history: 历史消息列表

        Returns:
            dict: 包含回复内容的字典
        """
        if history is None:
            history = []

        try:
            # 格式化历史记录
            messages = self._format_history(history)

            # 添加当前用户消息
            messages.append({"role": "user", "content": message})

            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )

            # 提取回复内容
            reply = response.choices[0].message.content.strip()

            # 提取情绪
            clean_content, emotion = self._extract_emotion(reply)

            return {"content": clean_content, "emotion": emotion}

        except Exception as e:
            print(f"Error getting AI response: {str(e)}")
            return {
                "content": f"抱歉，我现在无法回答。发生了错误: {str(e)}",
                "emotion": "sad",
            }
