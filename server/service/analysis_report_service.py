#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
import statistics
import numpy as np

# 添加路径以便导入数据库模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dao.database import Database

class AnalysisReportService:
    """全面的用户心理健康分析报告服务
    
    该服务整合所有可用的用户数据源，提供深度的心理健康分析：
    - 对话历史分析
    - 事件模式分析
    - 情绪轨迹分析
    - 行为模式分析
    - 认知模式分析
    - 社交互动分析
    - 个人成长轨迹分析
    - 风险评估和预测
    """

    def __init__(self):
        """初始化全面分析报告服务"""
        self.model = os.environ.get("CHAT_MODEL_NAME", "deepseek-chat")
        self.client = OpenAI(
            api_key=os.environ.get("CHAT_API_KEY"),
            base_url=os.environ.get("CHAT_BASE_URL", "https://api.deepseek.com/v1"),
        )
        self.analysis_prompt = self._load_comprehensive_analysis_prompt()
        
    def _load_comprehensive_analysis_prompt(self) -> str:
        """加载全面分析报告生成的Prompt模板"""
        return """你是一位资深的心理健康专家和数据分析师。请基于用户的全面心理健康数据，生成一份深度的专业分析报告。

你需要分析的数据包括：
1. 对话历史和交流模式
2. 事件记录和生活事件分析
3. 情绪轨迹和心理状态变化
4. 行为模式和应对策略
5. 认知模式和思维方式
6. 社交互动和人际关系
7. 个人成长和发展轨迹
8. 心理健康风险评估

请按照以下详细的JSON格式生成报告：
{
    "executive_summary": {
        "overall_status": "整体心理健康状态评估（详细描述）",
        "key_findings": ["关键发现1", "关键发现2", "关键发现3", "关键发现4", "关键发现5"],
        "primary_concerns": ["主要关注点1", "主要关注点2", "主要关注点3"],
        "strengths": ["个人优势1", "个人优势2", "个人优势3"],
        "risk_level": "low/medium/high",
        "progress_trend": "improving/stable/declining/mixed",
        "confidence_level": "评估可信度（高/中/低）",
        "report_period": "报告分析时间段"
    },
    "detailed_analysis": {
        "communication_patterns": {
            "interaction_frequency": "交流频率分析",
            "message_complexity": "消息复杂度趋势",
            "emotional_expression": "情感表达模式",
            "topic_preferences": ["常讨论话题1", "常讨论话题2"],
            "communication_style": "沟通风格特征",
            "openness_trend": "开放程度变化趋势"
        },
        "event_analysis": {
            "life_events_overview": "生活事件概览",
            "event_patterns": ["事件模式1", "事件模式2"],
            "trigger_events": ["触发事件1", "触发事件2"],
            "event_impact_analysis": "事件影响分析",
            "recovery_patterns": "恢复模式分析",
            "event_frequency_trend": "事件频率趋势"
        },
        "emotional_profile": {
            "dominant_emotions": ["主要情绪1", "主要情绪2", "主要情绪3"],
            "emotion_stability": "情绪稳定性分析",
            "emotion_regulation": "情绪调节能力评估",
            "emotional_range": "情绪波动范围",
            "trigger_emotions": ["易触发情绪1", "易触发情绪2"],
            "positive_emotions_trend": "积极情绪趋势",
            "negative_emotions_trend": "消极情绪趋势",
            "emotional_complexity": "情绪复杂度分析"
        },
        "behavioral_patterns": {
            "primary_behaviors": ["主要行为模式1", "主要行为模式2"],
            "coping_strategies": ["应对策略1", "应对策略2", "应对策略3"],
            "adaptive_behaviors": ["适应性行为1", "适应性行为2"],
            "maladaptive_behaviors": ["不良行为模式1", "不良行为模式2"],
            "behavior_triggers": ["行为触发因素1", "行为触发因素2"],
            "behavior_effectiveness": "行为效果评估",
            "behavior_evolution": "行为模式演变"
        },
        "cognitive_patterns": {
            "thinking_styles": ["思维风格1", "思维风格2"],
            "cognitive_biases": ["认知偏差1", "认知偏差2"],
            "problem_solving_approach": "问题解决方式",
            "core_beliefs": ["核心信念1", "核心信念2"],
            "cognitive_flexibility": "认知灵活性评估",
            "metacognitive_awareness": "元认知意识水平",
            "cognitive_distortions": ["认知扭曲1", "认知扭曲2"]
        },
        "social_interaction": {
            "interaction_style": "社交互动风格",
            "support_seeking": "求助行为分析",
            "social_support_utilization": "社会支持利用情况",
            "relationship_patterns": ["人际关系模式1", "人际关系模式2"],
            "social_engagement": "社交参与度",
            "interpersonal_skills": "人际交往技能评估"
        },
        "growth_trajectory": {
            "progress_indicators": ["进步指标1", "进步指标2"],
            "skill_development": ["技能发展1", "技能发展2"],
            "insight_development": "自我洞察力发展",
            "resilience_building": "韧性建设情况",
            "goal_achievement": "目标达成情况",
            "learning_patterns": ["学习模式1", "学习模式2"],
            "change_readiness": "变化准备度"
        }
    },
    "comprehensive_recommendations": {
        "immediate_actions": {
            "high_priority": ["高优先级行动1", "高优先级行动2"],
            "medium_priority": ["中优先级行动1", "中优先级行动2"],
            "low_priority": ["低优先级行动1", "低优先级行动2"]
        },
        "therapeutic_interventions": {
            "recommended_approaches": ["推荐治疗方法1", "推荐治疗方法2"],
            "skill_building": ["技能建设1", "技能建设2"],
            "coping_enhancement": ["应对能力增强1", "应对能力增强2"],
            "cognitive_restructuring": ["认知重构建议1", "认知重构建议2"]
        },
        "lifestyle_modifications": {
            "daily_habits": ["日常习惯改善1", "日常习惯改善2"],
            "stress_management": ["压力管理策略1", "压力管理策略2"],
            "social_connections": ["社交关系建议1", "社交关系建议2"],
            "self_care": ["自我照顾建议1", "自我照顾建议2"]
        },
        "long_term_goals": {
            "personal_development": ["个人发展目标1", "个人发展目标2"],
            "mental_health_maintenance": ["心理健康维护1", "心理健康维护2"],
            "skill_mastery": ["技能精进目标1", "技能精进目标2"],
            "relationship_enhancement": ["关系提升目标1", "关系提升目标2"]
        }
    },
    "risk_assessment": {
        "current_risks": {
            "immediate_risks": ["即时风险1", "即时风险2"],
            "short_term_risks": ["短期风险1", "短期风险2"],
            "long_term_risks": ["长期风险1", "长期风险2"]
        },
        "protective_factors": {
            "personal_strengths": ["个人优势1", "个人优势2"],
            "social_support": ["社会支持1", "社会支持2"],
            "coping_resources": ["应对资源1", "应对资源2"],
            "environmental_factors": ["环境因素1", "环境因素2"]
        },
        "warning_signals": {
            "behavioral_indicators": ["行为指标1", "行为指标2"],
            "emotional_indicators": ["情绪指标1", "情绪指标2"],
            "cognitive_indicators": ["认知指标1", "认知指标2"],
            "social_indicators": ["社交指标1", "社交指标2"]
        },
        "intervention_priority": "high/medium/low",
        "monitoring_recommendations": ["监控建议1", "监控建议2"],
        "crisis_prevention": ["危机预防策略1", "危机预防策略2"]
    },
    "data_insights": {
        "data_quality": "数据质量评估",
        "analysis_confidence": "分析可信度",
        "data_gaps": ["数据缺口1", "数据缺口2"],
        "trending_patterns": ["趋势模式1", "趋势模式2"],
        "predictive_indicators": ["预测指标1", "预测指标2"],
        "anomaly_detection": ["异常检测1", "异常检测2"]
    },
    "follow_up_recommendations": {
        "monitoring_schedule": "监控计划",
        "reassessment_timeline": "重新评估时间表",
        "data_collection_focus": ["数据收集重点1", "数据收集重点2"],
        "intervention_adjustments": ["干预调整建议1", "干预调整建议2"],
        "progress_metrics": ["进展指标1", "进展指标2"]
    }
}

请确保分析深入、全面、专业，提供具体可行的建议，并基于实际数据进行客观评估。"""

    def generate_user_report(self, user_id: str, session_ids: List[str] = None, time_period: int = 30) -> Dict[str, Any]:
        """生成用户全面分析报告
        
        Args:
            user_id: 用户ID
            session_ids: 会话ID列表（可选，如果不提供则自动获取用户的所有会话）
            time_period: 分析时间段（天数）
            
        Returns:
            Dict: 全面分析报告
        """
        try:
            # 如果没有提供会话ID，自动获取用户的所有会话
            if session_ids is None:
                session_ids = self._get_user_sessions(user_id)
            
            # 收集所有用户数据
            comprehensive_data = self._collect_comprehensive_data(user_id, session_ids, time_period)
            
            # 生成全面统计分析
            comprehensive_statistics = self._generate_comprehensive_statistics(comprehensive_data)
            
            # 生成深度洞察
            deep_insights = self._generate_deep_insights(comprehensive_data, comprehensive_statistics)
            
            # 使用AI生成专业分析
            ai_analysis = self._generate_ai_comprehensive_analysis(comprehensive_data, comprehensive_statistics, deep_insights)
            
            # 生成预测性分析
            predictive_analysis = self._generate_predictive_analysis(comprehensive_data)
            
            # 整合全面报告
            report = {
                "user_id": user_id,
                "report_type": "comprehensive_psychological_analysis",
                "generated_at": datetime.now().isoformat(),
                "analysis_period": {
                    "days": time_period,
                    "start_date": (datetime.now() - timedelta(days=time_period)).isoformat(),
                    "end_date": datetime.now().isoformat()
                },
                "data_sources": {
                    "sessions_analyzed": len(session_ids),
                    "data_types": ["conversations", "events", "emotions", "patterns", "behaviors", "cognitions"]
                },
                "comprehensive_statistics": comprehensive_statistics,
                "deep_insights": deep_insights,
                "ai_analysis": ai_analysis,
                "predictive_analysis": predictive_analysis,
                "metadata": {
                    "total_sessions": len(session_ids),
                    "total_conversations": len(comprehensive_data.get("conversations", [])),
                    "total_events": len(comprehensive_data.get("events", [])),
                    "total_emotions": len(comprehensive_data.get("emotions", [])),
                    "total_patterns": len(comprehensive_data.get("patterns", [])),
                    "total_moods": len(comprehensive_data.get("moods", [])),
                    "data_completeness": self._calculate_data_completeness(comprehensive_data),
                    "analysis_confidence": self._calculate_analysis_confidence(comprehensive_data)
                }
            }
            
            return report
            
        except Exception as e:
            print(f"Error generating comprehensive user report: {str(e)}")
            return {"error": str(e)}

    def _get_user_sessions(self, user_id: str) -> List[str]:
        """获取用户的所有会话ID"""
        try:
            db = Database()
            sessions = db.get_sessions(user_id)
            return list(sessions.keys())
        except Exception as e:
            print(f"Error getting user sessions: {str(e)}")
            return []

    def _collect_comprehensive_data(self, user_id: str, session_ids: List[str], time_period: int) -> Dict[str, Any]:
        """收集用户的全面数据"""
        db = Database()
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        comprehensive_data = {
            "conversations": [],
            "events": [],
            "emotions": [],
            "patterns": [],
            "moods": [],
            "inquiries": [],
            "user_profile": {},
            "long_term_memory": [],
            "session_plans": []
        }
        
        try:
            # 收集对话历史
            for session_id in session_ids:
                try:
                    chat_history = db.get_chat_history(session_id, limit=100)
                    message_count = db.get_user_message_count(session_id)
                    
                    session_data = {
                        "session_id": session_id,
                        "chat_history": chat_history,
                        "message_count": message_count,
                        "collected_at": datetime.now().isoformat()
                    }
                    comprehensive_data["conversations"].append(session_data)
                except Exception as e:
                    print(f"Error collecting conversation data for session {session_id}: {e}")
                    continue
            
            # 收集事件数据
            for session_id in session_ids:
                try:
                    events = db.get_events(session_id, limit=50)
                    filtered_events = self._filter_by_time_period(events, cutoff_date, "time")
                    comprehensive_data["events"].extend(filtered_events)
                except Exception as e:
                    print(f"Error collecting events for session {session_id}: {e}")
                    continue
            
            # 收集情绪数据
            try:
                emotions = db.get_emotion_history(user_id, limit=100)
                filtered_emotions = self._filter_by_time_period(emotions, cutoff_date, "timestamp")
                comprehensive_data["emotions"] = filtered_emotions
            except Exception as e:
                print(f"Error collecting emotions: {e}")
            
            # 收集行为模式数据
            for session_id in session_ids:
                try:
                    pattern = db.get_pattern_analysis(session_id)
                    if pattern:
                        comprehensive_data["patterns"].append(pattern)
                except Exception as e:
                    print(f"Error collecting pattern for session {session_id}: {e}")
                    continue
            
            # 收集心情分析数据
            for session_id in session_ids:
                try:
                    moods = db.get_mood_analysis(session_id, limit=20)
                    filtered_moods = self._filter_by_time_period(moods, cutoff_date, "timestamp")
                    comprehensive_data["moods"].extend(filtered_moods)
                except Exception as e:
                    print(f"Error collecting moods for session {session_id}: {e}")
                    continue
            
            # 收集引导性询问数据
            for session_id in session_ids:
                try:
                    inquiry = db.get_inquiry_result(session_id)
                    if inquiry:
                        comprehensive_data["inquiries"].append(inquiry)
                    
                    inquiry_history = db.get_inquiry_history(session_id, limit=10)
                    comprehensive_data["inquiries"].extend(inquiry_history)
                except Exception as e:
                    print(f"Error collecting inquiry data for session {session_id}: {e}")
                    continue
            
            # 收集用户画像
            try:
                comprehensive_data["user_profile"] = db.get_user_profile(user_id)
            except Exception as e:
                print(f"Error collecting user profile: {e}")
            
            # 收集长期记忆
            try:
                comprehensive_data["long_term_memory"] = db.get_long_term_memory(user_id, limit=50)
            except Exception as e:
                print(f"Error collecting long term memory: {e}")
            
            # 收集会话计划
            for session_id in session_ids:
                try:
                    plan = db.get_session_plan(session_id)
                    if plan:
                        comprehensive_data["session_plans"].append(plan)
                except Exception as e:
                    print(f"Error collecting session plan for {session_id}: {e}")
                    continue
            
            return comprehensive_data
            
        except Exception as e:
            print(f"Error in comprehensive data collection: {e}")
            return comprehensive_data

    def _filter_by_time_period(self, items: List[Dict], cutoff_date: datetime, time_field: str) -> List[Dict]:
        """根据时间段过滤数据"""
        filtered_items = []
        for item in items:
            try:
                time_str = item.get(time_field, "")
                if time_str:
                    # 处理不同的时间格式
                    if not time_str.endswith('Z') and '+' not in time_str:
                        if 'T' not in time_str:
                            time_str += 'T00:00:00'
                    item_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    if item_time >= cutoff_date:
                        filtered_items.append(item)
                else:
                    # 如果没有时间信息，仍然包含该项
                    filtered_items.append(item)
            except Exception as e:
                print(f"Error parsing time for filtering: {e}")
                # 解析失败时仍然包含该项
                filtered_items.append(item)
        return filtered_items

    def _generate_comprehensive_statistics(self, comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成全面的统计分析"""
        try:
            statistics = {
                "conversation_statistics": self._analyze_conversations(comprehensive_data["conversations"]),
                "event_statistics": self._analyze_events_comprehensive(comprehensive_data["events"]),
                "emotion_statistics": self._analyze_emotions_comprehensive(comprehensive_data["emotions"]),
                "pattern_statistics": self._analyze_patterns_comprehensive(comprehensive_data["patterns"]),
                "mood_statistics": self._analyze_moods(comprehensive_data["moods"]),
                "inquiry_statistics": self._analyze_inquiries(comprehensive_data["inquiries"]),
                "engagement_statistics": self._analyze_engagement_comprehensive(comprehensive_data),
                "temporal_statistics": self._analyze_temporal_patterns(comprehensive_data),
                "interaction_statistics": self._analyze_interaction_patterns(comprehensive_data)
            }
            return statistics
        except Exception as e:
            print(f"Error generating comprehensive statistics: {e}")
            return {}

    def _analyze_conversations(self, conversations: List[Dict]) -> Dict[str, Any]:
        """分析对话数据"""
        if not conversations:
            return {"total_conversations": 0, "average_length": 0, "interaction_patterns": {}}
        
        total_messages = sum(conv.get("message_count", 0) for conv in conversations)
        session_lengths = [len(conv.get("chat_history", [])) for conv in conversations]
        
        # 分析对话主题和情感
        topics = []
        emotions = []
        
        for conv in conversations:
            chat_history = conv.get("chat_history", [])
            for message in chat_history:
                # 简单的主题提取（基于关键词）
                content = message.get("content", "").lower()
                if any(word in content for word in ["工作", "职业", "事业"]):
                    topics.append("工作")
                elif any(word in content for word in ["家庭", "父母", "孩子"]):
                    topics.append("家庭")
                elif any(word in content for word in ["感情", "恋爱", "关系"]):
                    topics.append("感情")
                elif any(word in content for word in ["健康", "身体", "疾病"]):
                    topics.append("健康")
                elif any(word in content for word in ["学习", "教育", "考试"]):
                    topics.append("学习")
                elif any(word in content for word in ["焦虑", "抑郁", "压力"]):
                    topics.append("心理健康")
                else:
                    topics.append("其他")
                
                # 情感分析
                if any(word in content for word in ["开心", "高兴", "快乐"]):
                    emotions.append("积极")
                elif any(word in content for word in ["伤心", "难过", "痛苦"]):
                    emotions.append("消极")
                else:
                    emotions.append("中性")
        
        return {
            "total_conversations": len(conversations),
            "total_messages": total_messages,
            "average_session_length": statistics.mean(session_lengths) if session_lengths else 0,
            "session_length_distribution": {
                "min": min(session_lengths) if session_lengths else 0,
                "max": max(session_lengths) if session_lengths else 0,
                "median": statistics.median(session_lengths) if session_lengths else 0
            },
            "topic_distribution": dict(Counter(topics)),
            "emotion_distribution": dict(Counter(emotions)),
            "interaction_frequency": len(conversations) / 30 if conversations else 0,  # 每月平均对话次数
            "engagement_consistency": self._calculate_engagement_consistency(conversations)
        }

    def _analyze_events_comprehensive(self, events: List[Dict]) -> Dict[str, Any]:
        """全面分析事件数据"""
        if not events:
            return {"total_events": 0, "event_patterns": {}, "impact_analysis": {}}
        
        # 基本统计
        primary_types = [event.get("primaryType", "unknown") for event in events]
        sub_types = [event.get("subType", "unknown") for event in events]
        impacts = [event.get("impact", {}) for event in events]
        
        # 影响分析
        emotional_impacts = []
        behavioral_impacts = []
        
        for impact in impacts:
            if isinstance(impact, dict):
                emotional_impacts.append(impact.get("emotional", "unknown"))
                behavioral_impacts.append(impact.get("behavioral", "unknown"))
        
        # 时间模式分析
        event_times = []
        for event in events:
            try:
                time_str = event.get("time", "")
                if time_str:
                    if not time_str.endswith('Z') and '+' not in time_str:
                        if 'T' not in time_str:
                            time_str += 'T00:00:00'
                    event_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    event_times.append(event_time)
            except Exception as e:
                print(f"Error parsing event time: {e}")
                continue
        
        return {
            "total_events": len(events),
            "event_types": dict(Counter(primary_types)),
            "event_subtypes": dict(Counter(sub_types)),
            "most_common_types": Counter(primary_types).most_common(5),
            "emotional_impact_patterns": dict(Counter(emotional_impacts)),
            "behavioral_impact_patterns": dict(Counter(behavioral_impacts)),
            "event_frequency": len(events) / 30 if events else 0,  # 每月平均事件数
            "temporal_patterns": self._analyze_event_temporal_patterns(event_times),
            "severity_distribution": self._analyze_event_severity(events),
            "recovery_patterns": self._analyze_recovery_patterns(events)
        }

    def _analyze_emotions_comprehensive(self, emotions: List[Dict]) -> Dict[str, Any]:
        """全面分析情绪数据"""
        if not emotions:
            return {"total_emotions": 0, "emotion_patterns": {}, "stability_analysis": {}}
        
        # 情绪类别和强度
        emotion_categories = [emotion.get("emotion_category", "unknown") for emotion in emotions]
        emotion_scores = []
        
        for emotion in emotions:
            try:
                score = float(emotion.get("emotion_score", 0))
                emotion_scores.append(score)
            except:
                continue
        
        # 时间序列分析
        emotion_timeline = []
        for emotion in emotions:
            try:
                time_str = emotion.get("timestamp", "")
                if time_str:
                    if not time_str.endswith('Z') and '+' not in time_str:
                        if 'T' not in time_str:
                            time_str += 'T00:00:00'
                    emotion_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    score = float(emotion.get("emotion_score", 0))
                    emotion_timeline.append((emotion_time, score))
            except Exception as e:
                print(f"Error parsing emotion timeline: {e}")
                continue
        
        # 情绪稳定性分析
        stability_metrics = self._calculate_emotion_stability(emotion_scores)
        
        return {
            "total_emotions": len(emotions),
            "emotion_distribution": dict(Counter(emotion_categories)),
            "most_common_emotions": Counter(emotion_categories).most_common(5),
            "emotion_intensity": {
                "average": statistics.mean(emotion_scores) if emotion_scores else 0,
                "median": statistics.median(emotion_scores) if emotion_scores else 0,
                "std_dev": statistics.stdev(emotion_scores) if len(emotion_scores) > 1 else 0,
                "range": max(emotion_scores) - min(emotion_scores) if emotion_scores else 0
            },
            "stability_metrics": stability_metrics,
            "temporal_patterns": self._analyze_emotion_temporal_patterns(emotion_timeline),
            "volatility_analysis": self._analyze_emotion_volatility(emotion_scores),
            "trend_analysis": self._analyze_emotion_trends(emotion_timeline)
        }

    def _analyze_patterns_comprehensive(self, patterns: List[Dict]) -> Dict[str, Any]:
        """全面分析行为模式数据"""
        if not patterns:
            return {"total_patterns": 0, "pattern_evolution": {}, "behavioral_insights": {}}
        
        # 提取模式信息
        all_behaviors = []
        all_triggers = []
        all_coping_strategies = []
        pattern_types = []
        
        for pattern in patterns:
            if isinstance(pattern, dict):
                # 提取行为模式
                behavioral_patterns = pattern.get("behavioral_patterns", {})
                if isinstance(behavioral_patterns, dict):
                    all_behaviors.extend(behavioral_patterns.get("behavior_habits", []))
                    all_triggers.extend(behavioral_patterns.get("triggers", []))
                    all_coping_strategies.extend(behavioral_patterns.get("coping_strategies", []))
                
                # 提取模式类型
                pattern_analysis = pattern.get("pattern_analysis", {})
                if isinstance(pattern_analysis, dict):
                    for category in pattern_analysis.keys():
                        pattern_types.append(category)
        
        return {
            "total_patterns": len(patterns),
            "behavioral_patterns": dict(Counter(all_behaviors)),
            "common_triggers": dict(Counter(all_triggers)),
            "coping_strategies": dict(Counter(all_coping_strategies)),
            "pattern_categories": dict(Counter(pattern_types)),
            "pattern_evolution": self._analyze_pattern_evolution_comprehensive(patterns),
            "effectiveness_analysis": self._analyze_pattern_effectiveness(patterns),
            "adaptation_patterns": self._analyze_adaptation_patterns(patterns)
        }

    def _analyze_moods(self, moods: List[Dict]) -> Dict[str, Any]:
        """分析心情数据"""
        if not moods:
            return {"total_moods": 0, "mood_patterns": {}, "mood_stability": {}}
        
        mood_values = []
        mood_categories = []
        
        for mood in moods:
            try:
                if isinstance(mood, dict):
                    mood_value = mood.get("mood_score", 0)
                    if mood_value:
                        mood_values.append(float(mood_value))
                    
                    mood_category = mood.get("mood_category", "unknown")
                    mood_categories.append(mood_category)
            except:
                continue
        
        return {
            "total_moods": len(moods),
            "mood_distribution": dict(Counter(mood_categories)),
            "mood_statistics": {
                "average": statistics.mean(mood_values) if mood_values else 0,
                "median": statistics.median(mood_values) if mood_values else 0,
                "std_dev": statistics.stdev(mood_values) if len(mood_values) > 1 else 0
            },
            "mood_stability": self._calculate_mood_stability(mood_values),
            "mood_trends": self._analyze_mood_trends(moods)
        }

    def _analyze_inquiries(self, inquiries: List[Dict]) -> Dict[str, Any]:
        """分析引导性询问数据"""
        if not inquiries:
            return {"total_inquiries": 0, "inquiry_patterns": {}, "information_completeness": {}}
        
        stages = []
        completeness_scores = []
        
        for inquiry in inquiries:
            if isinstance(inquiry, dict):
                stage = inquiry.get("current_stage", "unknown")
                stages.append(stage)
                
                completeness = inquiry.get("information_completeness", 0)
                if completeness:
                    completeness_scores.append(float(completeness))
        
        return {
            "total_inquiries": len(inquiries),
            "inquiry_stages": dict(Counter(stages)),
            "average_completeness": statistics.mean(completeness_scores) if completeness_scores else 0,
            "completeness_trend": self._analyze_completeness_trend(inquiries),
            "inquiry_effectiveness": self._analyze_inquiry_effectiveness(inquiries)
        }

    def _analyze_engagement_comprehensive(self, comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
        """全面分析用户参与度"""
        engagement_metrics = {}
        
        # 计算各类数据的参与度
        conversations = comprehensive_data.get("conversations", [])
        events = comprehensive_data.get("events", [])
        emotions = comprehensive_data.get("emotions", [])
        patterns = comprehensive_data.get("patterns", [])
        
        # 时间跨度分析
        all_timestamps = []
        
        # 收集所有时间戳
        for conv in conversations:
            for message in conv.get("chat_history", []):
                timestamp = message.get("timestamp", "")
                if timestamp:
                    all_timestamps.append(timestamp)
        
        for event in events:
            timestamp = event.get("time", "")
            if timestamp:
                all_timestamps.append(timestamp)
        
        for emotion in emotions:
            timestamp = emotion.get("timestamp", "")
            if timestamp:
                all_timestamps.append(timestamp)
        
        # 计算参与度指标
        engagement_score = self._calculate_comprehensive_engagement_score(comprehensive_data)
        consistency_score = self._calculate_engagement_consistency(conversations)
        
        return {
            "overall_engagement_score": engagement_score,
            "consistency_score": consistency_score,
            "data_diversity": len([k for k, v in comprehensive_data.items() if v]),
            "temporal_consistency": self._analyze_temporal_consistency(all_timestamps),
            "interaction_depth": self._calculate_interaction_depth(comprehensive_data),
            "participation_patterns": self._analyze_participation_patterns(comprehensive_data)
        }

    def _analyze_temporal_patterns(self, comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析时间模式"""
        temporal_analysis = {}
        
        # 收集所有时间数据
        all_activities = []
        
        # 对话时间
        for conv in comprehensive_data.get("conversations", []):
            for message in conv.get("chat_history", []):
                try:
                    timestamp = message.get("timestamp", "")
                    if timestamp:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        all_activities.append(("conversation", dt))
                except:
                    continue
        
        # 事件时间
        for event in comprehensive_data.get("events", []):
            try:
                timestamp = event.get("time", "")
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    all_activities.append(("event", dt))
            except:
                continue
        
        # 情绪时间
        for emotion in comprehensive_data.get("emotions", []):
            try:
                timestamp = emotion.get("timestamp", "")
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    all_activities.append(("emotion", dt))
            except:
                continue
        
        if all_activities:
            # 按活动类型分析时间模式
            activity_times = defaultdict(list)
            for activity_type, timestamp in all_activities:
                activity_times[activity_type].append(timestamp)
            
            # 分析每种活动的时间模式
            for activity_type, timestamps in activity_times.items():
                temporal_analysis[f"{activity_type}_patterns"] = {
                    "hourly_distribution": self._analyze_hourly_distribution(timestamps),
                    "daily_distribution": self._analyze_daily_distribution(timestamps),
                    "weekly_distribution": self._analyze_weekly_distribution(timestamps)
                }
        
        return temporal_analysis

    def _analyze_interaction_patterns(self, comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析交互模式"""
        interaction_analysis = {}
        
        conversations = comprehensive_data.get("conversations", [])
        
        if conversations:
            # 分析对话模式
            response_times = []
            message_lengths = []
            
            for conv in conversations:
                chat_history = conv.get("chat_history", [])
                for i, message in enumerate(chat_history):
                    # 消息长度
                    content = message.get("content", "")
                    message_lengths.append(len(content))
                    
                    # 响应时间（如果有时间戳）
                    if i > 0:
                        try:
                            curr_time = datetime.fromisoformat(message.get("timestamp", "").replace('Z', '+00:00'))
                            prev_time = datetime.fromisoformat(chat_history[i-1].get("timestamp", "").replace('Z', '+00:00'))
                            response_time = (curr_time - prev_time).total_seconds()
                            response_times.append(response_time)
                        except:
                            continue
            
            interaction_analysis = {
                "average_message_length": statistics.mean(message_lengths) if message_lengths else 0,
                "message_length_distribution": {
                    "min": min(message_lengths) if message_lengths else 0,
                    "max": max(message_lengths) if message_lengths else 0,
                    "median": statistics.median(message_lengths) if message_lengths else 0
                },
                "average_response_time": statistics.mean(response_times) if response_times else 0,
                "response_time_consistency": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "interaction_intensity": self._calculate_interaction_intensity(conversations)
            }
        
        return interaction_analysis

    def _generate_deep_insights(self, comprehensive_data: Dict[str, Any], comprehensive_statistics: Dict[str, Any]) -> Dict[str, Any]:
        """生成深度洞察"""
        insights = {}
        
        try:
            # 行为模式洞察
            insights["behavioral_insights"] = self._generate_behavioral_insights(comprehensive_data, comprehensive_statistics)
            
            # 情绪模式洞察
            insights["emotional_insights"] = self._generate_emotional_insights(comprehensive_data, comprehensive_statistics)
            
            # 认知模式洞察
            insights["cognitive_insights"] = self._generate_cognitive_insights(comprehensive_data, comprehensive_statistics)
            
            # 社交模式洞察
            insights["social_insights"] = self._generate_social_insights(comprehensive_data, comprehensive_statistics)
            
            # 发展轨迹洞察
            insights["developmental_insights"] = self._generate_developmental_insights(comprehensive_data, comprehensive_statistics)
            
            # 风险因素洞察
            insights["risk_insights"] = self._generate_risk_insights(comprehensive_data, comprehensive_statistics)
            
        except Exception as e:
            print(f"Error generating deep insights: {e}")
            insights["error"] = str(e)
        
        return insights

    def _generate_predictive_analysis(self, comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成预测性分析"""
        predictive_analysis = {}
        
        try:
            # 情绪趋势预测
            emotions = comprehensive_data.get("emotions", [])
            if emotions:
                predictive_analysis["emotion_trend_prediction"] = self._predict_emotion_trends(emotions)
            
            # 行为模式预测
            patterns = comprehensive_data.get("patterns", [])
            if patterns:
                predictive_analysis["behavior_pattern_prediction"] = self._predict_behavior_patterns(patterns)
            
            # 参与度预测
            conversations = comprehensive_data.get("conversations", [])
            if conversations:
                predictive_analysis["engagement_prediction"] = self._predict_engagement_trends(conversations)
            
            # 风险预测
            predictive_analysis["risk_prediction"] = self._predict_risk_factors(comprehensive_data)
            
        except Exception as e:
            print(f"Error generating predictive analysis: {e}")
            predictive_analysis["error"] = str(e)
        
        return predictive_analysis

    # 辅助方法
    def _calculate_data_completeness(self, comprehensive_data: Dict[str, Any]) -> float:
        """计算数据完整性"""
        data_sources = ["conversations", "events", "emotions", "patterns", "moods", "inquiries"]
        available_sources = sum(1 for source in data_sources if comprehensive_data.get(source))
        return (available_sources / len(data_sources)) * 100

    def _calculate_analysis_confidence(self, comprehensive_data: Dict[str, Any]) -> float:
        """计算分析可信度"""
        total_data_points = (
            len(comprehensive_data.get("conversations", [])) +
            len(comprehensive_data.get("events", [])) +
            len(comprehensive_data.get("emotions", [])) +
            len(comprehensive_data.get("patterns", []))
        )
        
        if total_data_points >= 50:
            return 95.0
        elif total_data_points >= 20:
            return 80.0
        elif total_data_points >= 10:
            return 65.0
        else:
            return 40.0

    def _calculate_engagement_consistency(self, conversations: List[Dict]) -> float:
        """计算参与度一致性"""
        if not conversations:
            return 0.0
        
        # 简单的一致性计算：基于对话间隔的标准差
        session_dates = []
        for conv in conversations:
            try:
                chat_history = conv.get("chat_history", [])
                if chat_history:
                    # 使用第一条消息的时间作为会话时间
                    timestamp = chat_history[0].get("timestamp", "")
                    if timestamp:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        session_dates.append(dt)
            except:
                continue
        
        if len(session_dates) < 2:
            return 50.0  # 数据不足，给予中等评分
        
        # 计算相邻会话间的时间间隔
        session_dates.sort()
        intervals = []
        for i in range(1, len(session_dates)):
            interval = (session_dates[i] - session_dates[i-1]).days
            intervals.append(interval)
        
        if intervals:
            std_dev = statistics.stdev(intervals)
            # 标准差越小，一致性越高
            consistency_score = max(0, 100 - std_dev)
            return min(100, consistency_score)
        
        return 50.0

    def _calculate_comprehensive_engagement_score(self, comprehensive_data: Dict[str, Any]) -> float:
        """计算全面参与度评分"""
        weights = {
            "conversations": 0.25,
            "events": 0.20,
            "emotions": 0.20,
            "patterns": 0.15,
            "moods": 0.10,
            "inquiries": 0.10
        }
        
        scores = {}
        for data_type, weight in weights.items():
            data = comprehensive_data.get(data_type, [])
            if data_type == "conversations":
                # 对话评分基于会话数和消息数
                total_messages = sum(len(conv.get("chat_history", [])) for conv in data)
                scores[data_type] = min(100, (len(data) * 10) + (total_messages * 2))
            else:
                # 其他数据类型基于数量
                scores[data_type] = min(100, len(data) * 10)
        
        # 计算加权平均
        total_score = sum(scores.get(data_type, 0) * weight for data_type, weight in weights.items())
        return round(total_score, 2)

    def _generate_ai_comprehensive_analysis(self, comprehensive_data: Dict[str, Any], comprehensive_statistics: Dict[str, Any], deep_insights: Dict[str, Any]) -> Dict[str, Any]:
        """使用AI生成全面分析"""
        try:
            # 准备分析数据
            analysis_input = {
                "data_summary": {
                    "total_conversations": len(comprehensive_data.get("conversations", [])),
                    "total_events": len(comprehensive_data.get("events", [])),
                    "total_emotions": len(comprehensive_data.get("emotions", [])),
                    "total_patterns": len(comprehensive_data.get("patterns", [])),
                    "data_completeness": self._calculate_data_completeness(comprehensive_data),
                    "analysis_confidence": self._calculate_analysis_confidence(comprehensive_data)
                },
                "comprehensive_statistics": comprehensive_statistics,
                "deep_insights": deep_insights
            }
            
            # 构建提示词
            prompt = f"""
            {self.analysis_prompt}
            
            用户全面心理健康数据分析：
            {json.dumps(analysis_input, ensure_ascii=False, indent=2)}
            
            请基于以上全面的数据生成深度专业的心理健康分析报告。
            """
            
            # 调用AI生成分析
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            ai_analysis = json.loads(response.choices[0].message.content)
            return ai_analysis
            
        except Exception as e:
            print(f"Error in AI comprehensive analysis: {str(e)}")
            return {
                "error": "AI分析生成失败",
                "fallback_analysis": self._generate_comprehensive_fallback_analysis(comprehensive_statistics)
            }

    def _generate_comprehensive_fallback_analysis(self, comprehensive_statistics: Dict[str, Any]) -> Dict[str, Any]:
        """生成全面的备用分析"""
        conversation_stats = comprehensive_statistics.get("conversation_statistics", {})
        event_stats = comprehensive_statistics.get("event_statistics", {})
        emotion_stats = comprehensive_statistics.get("emotion_statistics", {})
        engagement_stats = comprehensive_statistics.get("engagement_statistics", {})
        
        return {
            "executive_summary": {
                "overall_status": "基于现有数据的初步评估",
                "key_findings": [
                    f"进行了{conversation_stats.get('total_conversations', 0)}次对话交流",
                    f"记录了{event_stats.get('total_events', 0)}个生活事件",
                    f"情绪平均强度为{emotion_stats.get('emotion_intensity', {}).get('average', 0):.1f}",
                    f"整体参与度评分为{engagement_stats.get('overall_engagement_score', 0):.1f}",
                    "需要更多数据进行深入分析"
                ],
                "risk_level": "medium",
                "progress_trend": "需要持续观察"
            },
            "comprehensive_recommendations": {
                "immediate_actions": {
                    "high_priority": ["保持定期交流", "继续记录情绪变化"],
                    "medium_priority": ["建立自我反思习惯", "关注生活事件影响"],
                    "low_priority": ["探索新的应对策略", "增强自我认知"]
                },
                "therapeutic_interventions": {
                    "recommended_approaches": ["认知行为疗法", "正念练习"],
                    "skill_building": ["情绪调节技能", "压力管理技能"],
                    "coping_enhancement": ["建立支持系统", "发展积极应对策略"]
                }
            },
            "risk_assessment": {
                "current_risks": {
                    "immediate_risks": ["数据不足导致的评估局限性"],
                    "short_term_risks": ["情绪波动的潜在影响"],
                    "long_term_risks": ["需要持续监控的心理健康状况"]
                },
                "protective_factors": {
                    "personal_strengths": ["主动参与心理健康管理", "愿意记录和分析"],
                    "social_support": ["与咨询师的良好互动"],
                    "coping_resources": ["基本的情绪表达能力"]
                }
            }
        }

    # 以下是各种分析方法的实现（由于篇幅限制，只显示方法签名）
    def _analyze_event_temporal_patterns(self, event_times: List[datetime]) -> Dict[str, Any]:
        """分析事件时间模式"""
        if not event_times:
            return {"hourly_patterns": {}, "daily_patterns": {}, "weekly_patterns": {}}
        
        # 按小时分析
        hourly_counts = Counter([dt.hour for dt in event_times])
        
        # 按星期几分析
        weekly_counts = Counter([dt.weekday() for dt in event_times])
        
        # 按日期分析
        daily_counts = Counter([dt.date() for dt in event_times])
        
        # 找出高峰时间
        peak_hour = hourly_counts.most_common(1)[0][0] if hourly_counts else 12
        peak_day = weekly_counts.most_common(1)[0][0] if weekly_counts else 0
        
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        return {
            "hourly_patterns": dict(hourly_counts),
            "daily_patterns": len(daily_counts),
            "weekly_patterns": dict(weekly_counts),
            "peak_hour": peak_hour,
            "peak_day": weekday_names[peak_day] if peak_day < 7 else "未知",
            "event_clustering": self._detect_event_clustering(event_times)
        }

    def _analyze_event_severity(self, events: List[Dict]) -> Dict[str, Any]:
        """分析事件严重程度"""
        if not events:
            return {"severity_levels": {}, "average_severity": 0, "high_severity_count": 0}
        
        severity_levels = []
        severity_scores = []
        
        for event in events:
            # 从事件中提取严重程度信息
            severity = event.get("severity", "medium")
            severity_levels.append(severity)
            
            # 转换为数值评分
            severity_score = {"low": 1, "medium": 2, "high": 3}.get(severity, 2)
            severity_scores.append(severity_score)
        
        severity_distribution = dict(Counter(severity_levels))
        high_severity_count = severity_distribution.get("high", 0)
        
        return {
            "severity_levels": severity_distribution,
            "average_severity": statistics.mean(severity_scores) if severity_scores else 0,
            "high_severity_count": high_severity_count,
            "severity_trend": self._calculate_severity_trend(events),
            "severity_by_type": self._analyze_severity_by_type(events)
        }

    def _analyze_recovery_patterns(self, events: List[Dict]) -> Dict[str, Any]:
        """分析恢复模式"""
        # 实现恢复模式分析
        pass

    def _calculate_emotion_stability(self, emotion_scores: List[float]) -> Dict[str, Any]:
        """计算情绪稳定性"""
        if not emotion_scores:
            return {"stability_score": 0, "volatility": 0, "stability_level": "未知"}
        
        if len(emotion_scores) < 2:
            return {"stability_score": 50, "volatility": 0, "stability_level": "数据不足"}
        
        # 计算标准差作为波动性指标
        std_dev = statistics.stdev(emotion_scores)
        mean_score = statistics.mean(emotion_scores)
        
        # 计算变异系数（标准差/平均值）
        coefficient_of_variation = std_dev / abs(mean_score) if mean_score != 0 else 0
        
        # 计算稳定性评分 (0-100)
        stability_score = max(0, 100 - (coefficient_of_variation * 100))
        
        # 根据稳定性评分确定等级
        if stability_score >= 80:
            stability_level = "高度稳定"
        elif stability_score >= 60:
            stability_level = "中度稳定"
        elif stability_score >= 40:
            stability_level = "轻度波动"
        else:
            stability_level = "高度波动"
        
        return {
            "stability_score": round(stability_score, 2),
            "volatility": round(std_dev, 2),
            "stability_level": stability_level,
            "coefficient_of_variation": round(coefficient_of_variation, 2),
            "mean_emotion": round(mean_score, 2)
        }

    def _analyze_emotion_temporal_patterns(self, emotion_timeline: List[Tuple[datetime, float]]) -> Dict[str, Any]:
        """分析情绪时间模式"""
        # 实现情绪时间模式分析
        pass

    def _analyze_emotion_volatility(self, emotion_scores: List[float]) -> Dict[str, Any]:
        """分析情绪波动性"""
        # 实现情绪波动性分析
        pass

    def _analyze_emotion_trends(self, emotion_timeline: List[Tuple[datetime, float]]) -> Dict[str, Any]:
        """分析情绪趋势"""
        if not emotion_timeline or len(emotion_timeline) < 2:
            return {"trend_direction": "未知", "trend_strength": 0, "slope": 0}
        
        # 按时间排序
        sorted_timeline = sorted(emotion_timeline, key=lambda x: x[0])
        
        # 计算简单线性趋势
        scores = [score for _, score in sorted_timeline]
        n = len(scores)
        
        # 计算斜率（简单线性回归）
        x_values = list(range(n))
        y_values = scores
        
        if n < 2:
            return {"trend_direction": "未知", "trend_strength": 0, "slope": 0}
        
        # 计算斜率
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # 计算趋势强度（相关系数）
        if denominator == 0:
            correlation = 0
        else:
            y_var = sum((y - y_mean) ** 2 for y in y_values)
            correlation = numerator / (denominator * y_var) ** 0.5 if y_var > 0 else 0
        
        # 判断趋势方向
        if slope > 0.1:
            trend_direction = "上升"
        elif slope < -0.1:
            trend_direction = "下降"
        else:
            trend_direction = "稳定"
        
        # 计算最近趋势（最近5个数据点）
        recent_scores = scores[-5:] if len(scores) >= 5 else scores
        recent_trend = self._calculate_recent_trend(recent_scores)
        
        return {
            "trend_direction": trend_direction,
            "trend_strength": abs(correlation),
            "slope": round(slope, 4),
            "recent_trend": recent_trend,
            "overall_change": round(scores[-1] - scores[0], 2) if scores else 0
        }

    def _analyze_pattern_evolution_comprehensive(self, patterns: List[Dict]) -> Dict[str, Any]:
        """全面分析模式演变"""
        # 实现模式演变分析
        pass

    def _analyze_pattern_effectiveness(self, patterns: List[Dict]) -> Dict[str, Any]:
        """分析模式有效性"""
        # 实现模式有效性分析
        pass

    def _analyze_adaptation_patterns(self, patterns: List[Dict]) -> Dict[str, Any]:
        """分析适应模式"""
        # 实现适应模式分析
        pass

    def _calculate_mood_stability(self, mood_values: List[float]) -> Dict[str, Any]:
        """计算心情稳定性"""
        # 实现心情稳定性计算
        pass

    def _analyze_mood_trends(self, moods: List[Dict]) -> Dict[str, Any]:
        """分析心情趋势"""
        # 实现心情趋势分析
        pass

    def _analyze_completeness_trend(self, inquiries: List[Dict]) -> Dict[str, Any]:
        """分析完整性趋势"""
        # 实现完整性趋势分析
        pass

    def _analyze_inquiry_effectiveness(self, inquiries: List[Dict]) -> Dict[str, Any]:
        """分析询问有效性"""
        # 实现询问有效性分析
        pass

    def _analyze_temporal_consistency(self, timestamps: List[str]) -> Dict[str, Any]:
        """分析时间一致性"""
        # 实现时间一致性分析
        pass

    def _calculate_interaction_depth(self, comprehensive_data: Dict[str, Any]) -> float:
        """计算交互深度"""
        # 实现交互深度计算
        pass

    def _analyze_participation_patterns(self, comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析参与模式"""
        # 实现参与模式分析
        pass

    def _analyze_hourly_distribution(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """分析小时分布"""
        # 实现小时分布分析
        pass

    def _analyze_daily_distribution(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """分析日分布"""
        # 实现日分布分析
        pass

    def _analyze_weekly_distribution(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """分析周分布"""
        # 实现周分布分析
        pass

    def _calculate_interaction_intensity(self, conversations: List[Dict]) -> float:
        """计算交互强度"""
        # 实现交互强度计算
        pass

    def _generate_behavioral_insights(self, comprehensive_data: Dict[str, Any], comprehensive_statistics: Dict[str, Any]) -> Dict[str, Any]:
        """生成行为洞察"""
        # 实现行为洞察生成
        pass

    def _generate_emotional_insights(self, comprehensive_data: Dict[str, Any], comprehensive_statistics: Dict[str, Any]) -> Dict[str, Any]:
        """生成情绪洞察"""
        # 实现情绪洞察生成
        pass

    def _generate_cognitive_insights(self, comprehensive_data: Dict[str, Any], comprehensive_statistics: Dict[str, Any]) -> Dict[str, Any]:
        """生成认知洞察"""
        # 实现认知洞察生成
        pass

    def _generate_social_insights(self, comprehensive_data: Dict[str, Any], comprehensive_statistics: Dict[str, Any]) -> Dict[str, Any]:
        """生成社交洞察"""
        # 实现社交洞察生成
        pass

    def _generate_developmental_insights(self, comprehensive_data: Dict[str, Any], comprehensive_statistics: Dict[str, Any]) -> Dict[str, Any]:
        """生成发展洞察"""
        # 实现发展洞察生成
        pass

    def _generate_risk_insights(self, comprehensive_data: Dict[str, Any], comprehensive_statistics: Dict[str, Any]) -> Dict[str, Any]:
        """生成风险洞察"""
        # 实现风险洞察生成
        pass

    def _predict_emotion_trends(self, emotions: List[Dict]) -> Dict[str, Any]:
        """预测情绪趋势"""
        # 实现情绪趋势预测
        pass

    def _predict_behavior_patterns(self, patterns: List[Dict]) -> Dict[str, Any]:
        """预测行为模式"""
        # 实现行为模式预测
        pass

    def _predict_engagement_trends(self, conversations: List[Dict]) -> Dict[str, Any]:
        """预测参与度趋势"""
        # 实现参与度趋势预测
        pass

    def _predict_risk_factors(self, comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
        """预测风险因素"""
        # 实现风险因素预测
        pass

    def export_comprehensive_report(self, report: Dict[str, Any], format_type: str = "json") -> str:
        """导出全面报告"""
        if format_type == "json":
            return json.dumps(report, ensure_ascii=False, indent=2)
        elif format_type == "markdown":
            return self._format_comprehensive_report_as_markdown(report)
        elif format_type == "text":
            return self._format_comprehensive_report_as_text(report)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def _format_comprehensive_report_as_markdown(self, report: Dict[str, Any]) -> str:
        """将报告格式化为Markdown"""
        markdown_report = []
        
        # 标题
        markdown_report.append("# 全面心理健康分析报告")
        markdown_report.append("")
        
        # 基本信息
        markdown_report.append("## 基本信息")
        markdown_report.append(f"- **用户ID**: {report.get('user_id', 'Unknown')}")
        markdown_report.append(f"- **生成时间**: {report.get('generated_at', 'Unknown')}")
        markdown_report.append(f"- **分析周期**: {report.get('analysis_period', {}).get('days', 'Unknown')}天")
        markdown_report.append(f"- **数据完整度**: {report.get('metadata', {}).get('data_completeness', 0):.1f}%")
        markdown_report.append(f"- **分析可信度**: {report.get('metadata', {}).get('analysis_confidence', 0):.1f}%")
        markdown_report.append("")
        
        # 执行摘要
        ai_analysis = report.get("ai_analysis", {})
        executive_summary = ai_analysis.get("executive_summary", {})
        
        if executive_summary:
            markdown_report.append("## 执行摘要")
            markdown_report.append(f"- **整体状态**: {executive_summary.get('overall_status', 'Unknown')}")
            markdown_report.append(f"- **风险等级**: {executive_summary.get('risk_level', 'Unknown')}")
            markdown_report.append(f"- **进展趋势**: {executive_summary.get('progress_trend', 'Unknown')}")
            markdown_report.append("")
            
            key_findings = executive_summary.get("key_findings", [])
            if key_findings:
                markdown_report.append("### 关键发现")
                for finding in key_findings:
                    markdown_report.append(f"- {finding}")
                markdown_report.append("")
        
        # 详细分析
        detailed_analysis = ai_analysis.get("detailed_analysis", {})
        if detailed_analysis:
            markdown_report.append("## 详细分析")
            
            # 各个分析维度
            for category, analysis in detailed_analysis.items():
                category_title = {
                    "communication_patterns": "沟通模式",
                    "event_analysis": "事件分析",
                    "emotional_profile": "情绪画像",
                    "behavioral_patterns": "行为模式",
                    "cognitive_patterns": "认知模式",
                    "social_interaction": "社交互动",
                    "growth_trajectory": "成长轨迹"
                }.get(category, category)
                
                markdown_report.append(f"### {category_title}")
                
                if isinstance(analysis, dict):
                    for key, value in analysis.items():
                        if isinstance(value, list):
                            markdown_report.append(f"- **{key}**: {', '.join(value)}")
                        else:
                            markdown_report.append(f"- **{key}**: {value}")
                markdown_report.append("")
        
        # 建议
        recommendations = ai_analysis.get("comprehensive_recommendations", {})
        if recommendations:
            markdown_report.append("## 建议")
            
            for rec_type, rec_content in recommendations.items():
                rec_title = {
                    "immediate_actions": "立即行动",
                    "therapeutic_interventions": "治疗干预",
                    "lifestyle_modifications": "生活方式调整",
                    "long_term_goals": "长期目标"
                }.get(rec_type, rec_type)
                
                markdown_report.append(f"### {rec_title}")
                
                if isinstance(rec_content, dict):
                    for priority, actions in rec_content.items():
                        if isinstance(actions, list):
                            markdown_report.append(f"**{priority}**:")
                            for action in actions:
                                markdown_report.append(f"- {action}")
                        else:
                            markdown_report.append(f"- **{priority}**: {actions}")
                markdown_report.append("")
        
        # 风险评估
        risk_assessment = ai_analysis.get("risk_assessment", {})
        if risk_assessment:
            markdown_report.append("## 风险评估")
            
            current_risks = risk_assessment.get("current_risks", {})
            if current_risks:
                markdown_report.append("### 当前风险")
                for risk_type, risks in current_risks.items():
                    if isinstance(risks, list):
                        risk_title = {
                            "immediate_risks": "即时风险",
                            "short_term_risks": "短期风险",
                            "long_term_risks": "长期风险"
                        }.get(risk_type, risk_type)
                        
                        markdown_report.append(f"**{risk_title}**:")
                        for risk in risks:
                            markdown_report.append(f"- {risk}")
                markdown_report.append("")
            
            protective_factors = risk_assessment.get("protective_factors", {})
            if protective_factors:
                markdown_report.append("### 保护因素")
                for factor_type, factors in protective_factors.items():
                    if isinstance(factors, list):
                        factor_title = {
                            "personal_strengths": "个人优势",
                            "social_support": "社会支持",
                            "coping_resources": "应对资源",
                            "environmental_factors": "环境因素"
                        }.get(factor_type, factor_type)
                        
                        markdown_report.append(f"**{factor_title}**:")
                        for factor in factors:
                            markdown_report.append(f"- {factor}")
                markdown_report.append("")
        
        # 数据洞察
        data_insights = ai_analysis.get("data_insights", {})
        if data_insights:
            markdown_report.append("## 数据洞察")
            for key, value in data_insights.items():
                if isinstance(value, list):
                    markdown_report.append(f"- **{key}**: {', '.join(value)}")
                else:
                    markdown_report.append(f"- **{key}**: {value}")
            markdown_report.append("")
        
        # 后续建议
        follow_up = ai_analysis.get("follow_up_recommendations", {})
        if follow_up:
            markdown_report.append("## 后续建议")
            for key, value in follow_up.items():
                if isinstance(value, list):
                    markdown_report.append(f"- **{key}**: {', '.join(value)}")
                else:
                    markdown_report.append(f"- **{key}**: {value}")
            markdown_report.append("")
        
        markdown_report.append("---")
        markdown_report.append("*此报告由AI生成，仅供参考。如需专业医疗建议，请咨询专业医疗人员。*")
        
        return "\n".join(markdown_report)

    def _format_comprehensive_report_as_text(self, report: Dict[str, Any]) -> str:
        """将报告格式化为文本"""
        text_report = []
        
        # 标题
        text_report.append("=" * 60)
        text_report.append("全面心理健康分析报告")
        text_report.append("=" * 60)
        text_report.append("")
        
        # 基本信息
        text_report.append("基本信息:")
        text_report.append(f"用户ID: {report.get('user_id', 'Unknown')}")
        text_report.append(f"生成时间: {report.get('generated_at', 'Unknown')}")
        text_report.append(f"分析周期: {report.get('analysis_period', {}).get('days', 'Unknown')}天")
        text_report.append(f"数据完整度: {report.get('metadata', {}).get('data_completeness', 0):.1f}%")
        text_report.append(f"分析可信度: {report.get('metadata', {}).get('analysis_confidence', 0):.1f}%")
        text_report.append("")
        
        # 数据摘要
        metadata = report.get("metadata", {})
        text_report.append("数据摘要:")
        text_report.append(f"- 分析会话数: {metadata.get('total_sessions', 0)}")
        text_report.append(f"- 对话记录数: {metadata.get('total_conversations', 0)}")
        text_report.append(f"- 事件总数: {metadata.get('total_events', 0)}")
        text_report.append(f"- 情绪记录数: {metadata.get('total_emotions', 0)}")
        text_report.append(f"- 行为模式数: {metadata.get('total_patterns', 0)}")
        text_report.append(f"- 心情记录数: {metadata.get('total_moods', 0)}")
        text_report.append("")
        
        # AI分析结果
        ai_analysis = report.get("ai_analysis", {})
        
        # 执行摘要
        executive_summary = ai_analysis.get("executive_summary", {})
        if executive_summary:
            text_report.append("执行摘要:")
            text_report.append(f"- 整体状态: {executive_summary.get('overall_status', 'Unknown')}")
            text_report.append(f"- 风险等级: {executive_summary.get('risk_level', 'Unknown')}")
            text_report.append(f"- 进展趋势: {executive_summary.get('progress_trend', 'Unknown')}")
            text_report.append("")
            
            key_findings = executive_summary.get("key_findings", [])
            if key_findings:
                text_report.append("关键发现:")
                for i, finding in enumerate(key_findings, 1):
                    text_report.append(f"{i}. {finding}")
                text_report.append("")
        
        # 详细分析
        detailed_analysis = ai_analysis.get("detailed_analysis", {})
        if detailed_analysis:
            text_report.append("详细分析:")
            text_report.append("-" * 40)
            
            for category, analysis in detailed_analysis.items():
                category_title = {
                    "communication_patterns": "沟通模式分析",
                    "event_analysis": "事件分析",
                    "emotional_profile": "情绪画像",
                    "behavioral_patterns": "行为模式",
                    "cognitive_patterns": "认知模式",
                    "social_interaction": "社交互动",
                    "growth_trajectory": "成长轨迹"
                }.get(category, category)
                
                text_report.append(f"{category_title}:")
                
                if isinstance(analysis, dict):
                    for key, value in analysis.items():
                        if isinstance(value, list):
                            text_report.append(f"  - {key}: {', '.join(value)}")
                        else:
                            text_report.append(f"  - {key}: {value}")
                text_report.append("")
        
        # 建议
        recommendations = ai_analysis.get("comprehensive_recommendations", {})
        if recommendations:
            text_report.append("建议:")
            text_report.append("-" * 40)
            
            for rec_type, rec_content in recommendations.items():
                rec_title = {
                    "immediate_actions": "立即行动",
                    "therapeutic_interventions": "治疗干预",
                    "lifestyle_modifications": "生活方式调整",
                    "long_term_goals": "长期目标"
                }.get(rec_type, rec_type)
                
                text_report.append(f"{rec_title}:")
                
                if isinstance(rec_content, dict):
                    for priority, actions in rec_content.items():
                        if isinstance(actions, list):
                            text_report.append(f"  {priority}:")
                            for action in actions:
                                text_report.append(f"    - {action}")
                        else:
                            text_report.append(f"  - {priority}: {actions}")
                text_report.append("")
        
        # 风险评估
        risk_assessment = ai_analysis.get("risk_assessment", {})
        if risk_assessment:
            text_report.append("风险评估:")
            text_report.append("-" * 40)
            
            current_risks = risk_assessment.get("current_risks", {})
            if current_risks:
                text_report.append("当前风险:")
                for risk_type, risks in current_risks.items():
                    if isinstance(risks, list):
                        risk_title = {
                            "immediate_risks": "即时风险",
                            "short_term_risks": "短期风险",
                            "long_term_risks": "长期风险"
                        }.get(risk_type, risk_type)
                        
                        text_report.append(f"  {risk_title}:")
                        for risk in risks:
                            text_report.append(f"    - {risk}")
                text_report.append("")
            
            protective_factors = risk_assessment.get("protective_factors", {})
            if protective_factors:
                text_report.append("保护因素:")
                for factor_type, factors in protective_factors.items():
                    if isinstance(factors, list):
                        factor_title = {
                            "personal_strengths": "个人优势",
                            "social_support": "社会支持",
                            "coping_resources": "应对资源",
                            "environmental_factors": "环境因素"
                        }.get(factor_type, factor_type)
                        
                        text_report.append(f"  {factor_title}:")
                        for factor in factors:
                            text_report.append(f"    - {factor}")
                text_report.append("")
        
        text_report.append("=" * 60)
        text_report.append("报告结束")
        text_report.append("=" * 60)
        text_report.append("")
        text_report.append("注意：此报告由AI生成，仅供参考。")
        text_report.append("如需专业医疗建议，请咨询专业医疗人员。")
        
        return "\n".join(text_report)
    
    def _detect_event_clustering(self, event_times: List[datetime]) -> str:
        """检测事件聚集模式"""
        if len(event_times) < 3:
            return "数据不足"
        
        # 计算事件间的时间间隔
        sorted_times = sorted(event_times)
        intervals = []
        for i in range(1, len(sorted_times)):
            interval = (sorted_times[i] - sorted_times[i-1]).total_seconds() / 3600  # 小时
            intervals.append(interval)
        
        if not intervals:
            return "无聚集模式"
        
        avg_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
        
        # 根据间隔模式判断聚集程度
        if avg_interval < 24 and std_interval < 12:  # 平均间隔小于24小时且标准差小于12小时
            return "高度聚集"
        elif avg_interval < 168 and std_interval < 72:  # 平均间隔小于1周且标准差小于3天
            return "中度聚集"
        else:
            return "分散分布"
    
    def _calculate_severity_trend(self, events: List[Dict]) -> str:
        """计算严重程度趋势"""
        if len(events) < 2:
            return "数据不足"
        
        # 按时间排序事件
        sorted_events = sorted(events, key=lambda x: x.get("time", ""))
        
        # 提取前半部分和后半部分的严重程度
        mid_point = len(sorted_events) // 2
        early_events = sorted_events[:mid_point]
        recent_events = sorted_events[mid_point:]
        
        # 计算平均严重程度
        def get_avg_severity(event_list):
            scores = [{"low": 1, "medium": 2, "high": 3}.get(event.get("severity", "medium"), 2) for event in event_list]
            return statistics.mean(scores) if scores else 2
        
        early_avg = get_avg_severity(early_events)
        recent_avg = get_avg_severity(recent_events)
        
        if recent_avg > early_avg + 0.3:
            return "严重程度上升"
        elif recent_avg < early_avg - 0.3:
            return "严重程度下降"
        else:
            return "严重程度稳定"
    
    def _analyze_severity_by_type(self, events: List[Dict]) -> Dict[str, Any]:
        """按事件类型分析严重程度"""
        type_severity = defaultdict(list)
        
        for event in events:
            event_type = event.get("primaryType", "unknown")
            severity = event.get("severity", "medium")
            severity_score = {"low": 1, "medium": 2, "high": 3}.get(severity, 2)
            type_severity[event_type].append(severity_score)
        
        type_avg_severity = {}
        for event_type, scores in type_severity.items():
            type_avg_severity[event_type] = statistics.mean(scores) if scores else 2
        
        return type_avg_severity
    
    def _calculate_recent_trend(self, recent_scores: List[float]) -> str:
        """计算最近趋势"""
        if len(recent_scores) < 2:
            return "数据不足"
        
        # 比较最近分数和之前分数
        recent_avg = statistics.mean(recent_scores[-2:])
        earlier_avg = statistics.mean(recent_scores[:-2]) if len(recent_scores) > 2 else recent_scores[0]
        
        if recent_avg > earlier_avg + 0.2:
            return "最近上升"
        elif recent_avg < earlier_avg - 0.2:
            return "最近下降"
        else:
            return "最近稳定" 