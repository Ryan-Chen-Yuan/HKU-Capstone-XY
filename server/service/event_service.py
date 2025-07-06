#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from openai import OpenAI
from typing import List, Dict, Any
import time

class EventService:
    """事件提取服务，负责从对话中提取关键事件"""

    def __init__(self):
        """初始化事件提取服务"""
        self.model = os.environ.get("EVENT_MODEL_NAME")
        self.client = OpenAI(
            api_key=os.environ.get("EVENT_API_KEY"),
            base_url=os.environ.get("EVENT_BASE_URL"),
        )
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """加载事件提取Prompt模板"""
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        os.makedirs(prompt_dir, exist_ok=True)

        prompt_file = os.path.join(prompt_dir, "event_extraction_prompt.txt")

        # 如果模板文件不存在，创建默认模板
        if not os.path.exists(prompt_file):
            default_prompt = """你是一个专业的事件提取助手。你的任务是从心理咨询用户对话中提取关键事件。

请严格按照以下JSON格式提取事件，不要添加任何其他内容：
{
    "events": [
        {
            "primaryType": "emotional/cognitive/interpersonal/behavioral/physiological/lifeEvent",
            "subType": "emotionalLow/positiveThinking/conflict/avoidance/sleepIssues/transition等",
            "title": "事件标题",
            "content": "事件详细描述",
            "dialogContent": "原始对话内容",
            "status": "pending",
            "tagColor": "#颜色代码"
        }
    ]
}

事件类型参考：
1. emotional - 情绪类事件 (如: emotionalLow-情绪低落, emotionalHigh-情绪高涨)
2. cognitive - 认知类事件 (如: positiveThinking-积极思考, negativeThinking-消极思考)
3. interpersonal - 人际关系事件 (如: conflict-冲突, support-支持)
4. behavioral - 行为类事件 (如: avoidance-回避行为, proactive-积极行为)
5. physiological - 生理类事件 (如: sleepIssues-睡眠问题, appetite-食欲变化)
6. lifeEvent - 生活事件 (如: transition-生活转变, challenge-挑战)

注意事项：
1. 只提取真实发生的事件，不要推测或假设
2. 确保事件描述清晰具体
3. 每个事件必须包含primaryType和subType
4. 根据事件类型选择合适的标签颜色：
   - emotional: #4192FF
   - cognitive: #9C27B0
   - interpersonal: #4CAF50
   - behavioral: #FF9800
   - physiological: #F44336
   - lifeEvent: #FFC107
5. 必须返回有效的JSON格式，不要添加任何其他说明文字
"""
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(default_prompt)

            return default_prompt

        # 读取模板文件
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def extract_events(self, conversation: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """从对话中提取事件

        Args:
            conversation: 对话历史列表，每个元素包含 role 和 content

        Returns:
            List[Dict]: 提取的事件列表
        """
        try:
            # 格式化对话历史
            formatted_conversation = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation
            ])

            # 提取原始对话内容（用户部分）
            user_messages = [msg['content'] for msg in conversation if msg['role'] == 'user']
            dialog_content = "\n".join(user_messages)

            # 准备系统提示
            messages = [
                {"role": "system", "content": self.prompt_template},
                {"role": "user", "content": f"请从以下对话中提取事件：\n\n{formatted_conversation}"}
            ]

            # 调用OpenAI API，强制要求返回JSON对象
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.1,  # 使用较低的温度以获得更确定性的结果
                response_format={"type": "json_object"}, #使用response_format规定json输出
            )

            # 直接获取 JSON 对象
            events_data = response.choices[0].message.content
            if isinstance(events_data, str):
                events_data = json.loads(events_data)
            print(f"LLM Response(JSON): {events_data}")  # 添加日志

            # 处理事件数据，添加必要的字段
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            events = events_data.get("events", [])
            
            for i, event in enumerate(events):
                # 生成唯一ID，使用时间戳、索引和标题哈希确保唯一性
                timestamp = int(time.time() * 1000)
                title_hash = abs(hash(event.get('title', ''))) % 10000
                event["id"] = f"evt_{timestamp}_{i}_{title_hash}"
                
                # 设置时间
                event["time"] = current_time
                event["createTime"] = current_time
                event["updateTime"] = current_time
                
                # 确保dialogContent存在
                if not event.get("dialogContent"):
                    event["dialogContent"] = dialog_content
                    
                # 确保状态字段存在
                if not event.get("status"):
                    event["status"] = "pending"
                    
                # 确保标签颜色存在
                if not event.get("tagColor"):
                    # 根据primaryType设置默认颜色
                    tag_colors = {
                        "emotional": "#4192FF",
                        "cognitive": "#9C27B0",
                        "interpersonal": "#4CAF50",
                        "behavioral": "#FF9800",
                        "physiological": "#F44336",
                        "lifeEvent": "#FFC107"
                    }
                    event["tagColor"] = tag_colors.get(event.get("primaryType", ""), "#848484")

            return events

        except Exception as e:
            print(f"Error extracting events: {str(e)}")
            print(f"Full error details: {type(e).__name__}: {str(e)}")  # 添加更详细的错误信息
            return []

    def get_events_by_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """获取指定对话的事件列表

        Args:
            conversation_id: 对话ID

        Returns:
            List[Dict]: 事件列表
        """
        # TODO: 从数据库获取对话内容并提取事件
        # 这部分需要与数据库层集成
        pass 