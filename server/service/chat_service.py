#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from openai import OpenAI
import re

from utils.extract_json import extract_json


class ChatService:
    """聊天服务，负责调用OpenAI API获取AI回复"""

    def __init__(self):
        """初始化聊天服务

        Args:
            model: OpenAI模型名称
        """
        self.model = os.environ.get("MODEL_NAME")
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("BASE_URL"),
        )
        
        # 功能控制参数
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

    def _load_planning_prompt(self):
        """加载规划工具Prompt模板"""
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "planning_prompt.txt")

        if not os.path.exists(prompt_file):
            raise FileNotFoundError("Planning prompt file not found")

        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _load_guided_inquiry_prompt(self):
        """加载引导性询问Prompt模板"""
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "guided_inquiry_prompt.txt")

        if not os.path.exists(prompt_file):
            raise FileNotFoundError("Guided inquiry prompt file not found")

        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _load_pattern_analysis_prompt(self):
        """加载行为模式分析Prompt模板"""
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        prompt_file = os.path.join(prompt_dir, "pattern_analysis_prompt.txt")

        if not os.path.exists(prompt_file):
            raise FileNotFoundError("Pattern analysis prompt file not found")

        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _get_plan(self, session_id):
        """获取对话计划

        Args:
            session_id: 会话ID

        Returns:
            dict: 对话计划
        """
        plan_file = os.path.join(self.plans_dir, f"{session_id}.json")
        if os.path.exists(plan_file):
            with open(plan_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _save_plan(self, session_id, plan):
        """保存对话计划

        Args:
            session_id: 会话ID
            plan: 对话计划
        """
        plan_file = os.path.join(self.plans_dir, f"{session_id}.json")
        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)

    def _get_pattern(self, session_id):
        """获取行为模式分析

        Args:
            session_id: 会话ID

        Returns:
            dict: 行为模式分析
        """
        pattern_file = os.path.join(self.patterns_dir, f"{session_id}.json")
        if os.path.exists(pattern_file):
            with open(pattern_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _save_pattern(self, session_id, pattern):
        """保存行为模式分析

        Args:
            session_id: 会话ID
            pattern: 行为模式分析
        """
        pattern_file = os.path.join(self.patterns_dir, f"{session_id}.json")
        with open(pattern_file, "w", encoding="utf-8") as f:
            json.dump(pattern, f, ensure_ascii=False, indent=2)

    def _parse_inquiry_manually(self, text):
        """手动解析引导性询问结果的备用方法

        Args:
            text: AI返回的文本

        Returns:
            dict: 解析出的引导性询问结果
        """
        import re
        
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

    def _parse_pattern_manually(self, text):
        """手动解析行为模式分析结果的备用方法

        Args:
            text: AI返回的文本

        Returns:
            dict: 解析出的行为模式分析结果
        """
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

    def _assess_information_completeness(self, session_id, message, history):
        """评估信息完整性并生成引导性询问

        Args:
            session_id: 会话ID
            message: 当前用户消息
            history: 历史消息列表

        Returns:
            dict: 引导性询问结果
        """
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

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.3,
            )

            reply = response.choices[0].message.content.strip()
            # print(f"Inquiry assessment reply!!!: {reply}")
            
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

    def _analyze_behavior_pattern(self, session_id, collected_info):
        """分析行为模式

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

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1500,
                temperature=0.2,
            )

            reply = response.choices[0].message.content.strip()
            
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

            # 保存行为模式分析
            self._save_pattern(session_id, pattern_analysis)
            
            return pattern_analysis

        except Exception as e:
            print(f"Error analyzing behavior pattern: {str(e)}")
            return None

    def _update_plan(self, session_id, message, history):
        """更新对话计划

        Args:
            session_id: 会话ID
            message: 当前用户消息
            history: 历史消息列表

        Returns:
            dict: 更新后的对话计划
        """
        # 获取现有计划
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

        # 准备消息历史
        messages = [
            {"role": "system", "content": self.planning_prompt},
            {
                "role": "user",
                "content": f"Current plan: {json.dumps(plan, ensure_ascii=False)}\n\nCurrent message: {message}\n\nHistory: {json.dumps(history, ensure_ascii=False)}",
            },
        ]

        # print(f"messages: {messages}")

        # 调用OpenAI API更新计划
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )

        reply = response.choices[0].message.content.strip()
        # print(f"AI reply: {reply}")

        # 解析响应
        try:
            updated_plan = extract_json(reply)
            if updated_plan is None:
                print(f"Failed to extract JSON from reply: {reply}")
                # 如果JSON解析失败，保持原计划但更新时间戳
                plan["current_state"]["last_updated"] = datetime.now().isoformat()
                return plan

            # 保持inquiry_status信息
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

    def get_response(self, message, history=None, session_id=None):
        """获取AI回复

        Args:
            message: 用户消息
            history: 历史消息列表
            session_id: 会话ID（由app.py提供）

        Returns:
            dict: 包含回复内容的字典
        """
        if history is None:
            history = []

        try:
            # 更新对话计划
            plan = self._update_plan(session_id, message, history)

            # 检查是否需要进行引导性询问
            inquiry_result = None
            pattern_analysis = None
            
            # 只在功能启用且对话初期且信息不充分时进行引导性询问
            if (self.enable_guided_inquiry and 
                len(history) <= 10 and 
                not plan.get("inquiry_status", {}).get("pattern_analyzed", False)):
                
                inquiry_result = self._assess_information_completeness(session_id, message, history)
                
                # 更新计划中的询问状态
                plan["inquiry_status"]["information_completeness"] = inquiry_result.get("information_completeness", 0)
                plan["inquiry_status"]["stage"] = inquiry_result.get("current_stage", "初始阶段")
                
                print(f"Information completeness: {inquiry_result.get('information_completeness', 0)}%")
                
                # 如果信息充分度达到80%以上，或者对话轮次达到4轮，进行行为模式分析
                should_analyze = (
                    self.enable_pattern_analysis and
                    (inquiry_result.get("information_completeness", 0) >= 80 or 
                     len(history) >= 4)  # 测试模式：4轮对话后强制分析
                )
                
                if should_analyze and not plan["inquiry_status"]["pattern_analyzed"]:
                    print("Triggering behavior pattern analysis...")
                    # 收集所有对话信息用于模式分析
                    collected_info = {
                        "session_id": session_id,
                        "conversation_history": history + [{"role": "user", "content": message}],
                        "plan_context": plan.get("context", {}),
                        "inquiry_stage": inquiry_result.get("current_stage", "信息充分"),
                        "inquiry_result": inquiry_result
                    }
                    
                    pattern_analysis = self._analyze_behavior_pattern(session_id, collected_info)
                    if pattern_analysis:
                        plan["inquiry_status"]["pattern_analyzed"] = True
                        plan["inquiry_status"]["pattern_analysis_completed_at"] = datetime.now().isoformat()
                        print("Behavior pattern analysis completed and saved.")
                    else:
                        print("Behavior pattern analysis failed.")
            elif not self.enable_guided_inquiry:
                print("Guided inquiry is disabled by configuration.")
            
            # 如果模式分析功能被禁用但引导性询问功能启用，检查是否单独进行模式分析
            if (not self.enable_guided_inquiry and 
                self.enable_pattern_analysis and
                len(history) >= 4 and
                not plan.get("inquiry_status", {}).get("pattern_analyzed", False)):
                
                print("Triggering behavior pattern analysis (without guided inquiry)...")
                collected_info = {
                    "session_id": session_id,
                    "conversation_history": history + [{"role": "user", "content": message}],
                    "plan_context": plan.get("context", {}),
                    "inquiry_stage": "信息充分",
                    "inquiry_result": None
                }
                
                pattern_analysis = self._analyze_behavior_pattern(session_id, collected_info)
                if pattern_analysis:
                    plan["inquiry_status"]["pattern_analyzed"] = True
                    plan["inquiry_status"]["pattern_analysis_completed_at"] = datetime.now().isoformat()
                    print("Behavior pattern analysis completed and saved.")

            # 格式化历史记录
            messages = self._format_history(history)

            # 添加当前用户消息
            messages.append({"role": "user", "content": message})

            # 准备系统提示的附加信息
            additional_context = f"\n\n当前对话计划：{json.dumps(plan, ensure_ascii=False)}"
            
            # 如果有引导性询问结果，添加到上下文中
            if inquiry_result:
                additional_context += f"\n\n引导性询问评估：{json.dumps(inquiry_result, ensure_ascii=False)}"
                
                # 如果需要引导性询问，修改系统提示
                if inquiry_result.get("need_inquiry", False):
                    suggested_questions = inquiry_result.get("suggested_questions", [])
                    if suggested_questions:
                        additional_context += f"\n\n建议的引导性问题：{suggested_questions}"
                        additional_context += "\n\n请在给出共情回应后，适当地提出1-2个引导性问题来了解更多信息。"

            # 如果有行为模式分析，添加到上下文中
            if pattern_analysis:
                additional_context += f"\n\n行为模式分析已完成，关键洞察：{pattern_analysis.get('key_insights', [])}"
                additional_context += f"\n\n咨询建议：{pattern_analysis.get('consultation_recommendations', [])}"

            # 添加附加上下文到系统提示
            messages[0]["content"] += additional_context

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

            # 保存更新后的计划
            self._save_plan(session_id, plan)

            # 准备返回结果
            result = {
                "content": clean_content, 
                "emotion": emotion, 
                "plan": plan
            }
            
            # 如果有引导性询问结果，添加到返回结果中
            if inquiry_result:
                result["inquiry_result"] = inquiry_result
                
            # 如果有行为模式分析，添加到返回结果中
            if pattern_analysis:
                result["pattern_analysis"] = pattern_analysis

            return result

        except Exception as e:
            print(f"Error getting AI response: {str(e)}")
            return {
                "content": f"抱歉，我现在无法回答。发生了错误: {str(e)}",
                "emotion": "sad",
                "plan": None,
            }
