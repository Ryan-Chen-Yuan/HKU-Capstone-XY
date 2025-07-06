#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional
from openai import OpenAI
import statistics

class AnalysisReportService:
    """用户分析报告服务，基于行为模式和事件数据生成深度分析报告"""

    def __init__(self):
        """初始化分析报告服务"""
        self.model = os.environ.get("CHAT_MODEL_NAME")
        self.client = OpenAI(
            api_key=os.environ.get("CHAT_API_KEY"),
            base_url=os.environ.get("CHAT_BASE_URL"),
        )
        self.analysis_prompt = self._load_analysis_prompt()
        
    def _load_analysis_prompt(self) -> str:
        """加载分析报告生成的Prompt模板"""
        return """你是一位专业的心理健康数据分析师。基于用户的行为模式、事件历史和情绪数据，生成一份专业的心理健康分析报告。

请按照以下JSON格式生成报告：
{
    "summary": {
        "overallStatus": "整体心理健康状态评估",
        "keyFindings": ["主要发现1", "主要发现2", "主要发现3"],
        "riskLevel": "low/medium/high",
        "progressTrend": "improving/stable/declining"
    },
    "behaviorPatterns": {
        "dominantPatterns": ["主要行为模式1", "主要行为模式2"],
        "triggers": ["主要触发因素1", "主要触发因素2"],
        "copingStrategies": ["应对策略1", "应对策略2"],
        "patternEvolution": "行为模式变化趋势"
    },
    "eventAnalysis": {
        "frequentEventTypes": ["常见事件类型1", "常见事件类型2"],
        "impactfulEvents": ["高影响事件1", "高影响事件2"],
        "emotionalTriggers": ["情绪触发因素1", "情绪触发因素2"],
        "recoveryPatterns": "康复模式分析"
    },
    "emotionalProfile": {
        "dominantEmotions": ["主要情绪1", "主要情绪2"],
        "emotionalRange": "情绪波动范围描述",
        "stableEmotions": ["稳定情绪1", "稳定情绪2"],
        "volatileEmotions": ["波动情绪1", "波动情绪2"]
    },
    "recommendations": {
        "immediate": ["立即建议1", "立即建议2"],
        "shortTerm": ["短期建议1", "短期建议2"],
        "longTerm": ["长期建议1", "长期建议2"],
        "professionalReferral": "是否需要专业转介及原因"
    },
    "riskAssessment": {
        "currentRisks": ["当前风险1", "当前风险2"],
        "protectiveFactors": ["保护因素1", "保护因素2"],
        "warningSignals": ["警示信号1", "警示信号2"],
        "interventionPriority": "high/medium/low"
    }
}

请确保分析客观、专业，提供具体可行的建议。"""

    def generate_user_report(self, user_id: str, session_ids: List[str], time_period: int = 30) -> Dict[str, Any]:
        """生成用户综合分析报告
        
        Args:
            user_id: 用户ID
            session_ids: 会话ID列表
            time_period: 分析时间段（天数）
            
        Returns:
            Dict: 分析报告
        """
        try:
            # 收集用户数据
            user_data = self._collect_user_data(user_id, session_ids, time_period)
            
            # 生成数据统计
            statistics_data = self._generate_statistics(user_data)
            
            # 使用AI生成深度分析
            ai_analysis = self._generate_ai_analysis(user_data, statistics_data)
            
            # 整合报告
            report = {
                "user_id": user_id,
                "generated_at": datetime.now().isoformat(),
                "analysis_period": {
                    "days": time_period,
                    "start_date": (datetime.now() - timedelta(days=time_period)).isoformat(),
                    "end_date": datetime.now().isoformat()
                },
                "data_summary": statistics_data,
                "ai_analysis": ai_analysis,
                "metadata": {
                    "sessions_analyzed": len(session_ids),
                    "total_events": len(user_data.get("events", [])),
                    "total_patterns": len(user_data.get("patterns", [])),
                    "emotion_records": len(user_data.get("emotions", []))
                }
            }
            
            return report
            
        except Exception as e:
            print(f"Error generating user report: {str(e)}")
            return {"error": str(e)}

    def _collect_user_data(self, user_id: str, session_ids: List[str], time_period: int) -> Dict[str, Any]:
        """收集用户相关数据
        
        Args:
            user_id: 用户ID
            session_ids: 会话ID列表
            time_period: 时间段
            
        Returns:
            Dict: 用户数据集合
        """
        from dao.database import Database
        db = Database()
        
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        # 收集数据
        user_data = {
            "events": [],
            "patterns": [],
            "emotions": [],
            "user_profile": {},
            "long_term_memory": []
        }
        
        # 收集事件数据
        for session_id in session_ids:
            events = db.get_events(session_id)
            # 过滤时间范围内的事件
            filtered_events = [
                event for event in events 
                if datetime.fromisoformat(event.get("time", "1900-01-01")) >= cutoff_date
            ]
            user_data["events"].extend(filtered_events)
            
            # 收集行为模式数据
            pattern = db.get_pattern_analysis(session_id)
            if pattern:
                user_data["patterns"].append(pattern)
        
        # 收集情绪数据
        emotions = db.get_emotion_history(user_id, limit=50)
        user_data["emotions"] = [
            emotion for emotion in emotions 
            if datetime.fromisoformat(emotion.get("timestamp", "1900-01-01")) >= cutoff_date
        ]
        
        # 收集用户画像
        user_data["user_profile"] = db.get_user_profile(user_id)
        
        # 收集长期记忆
        user_data["long_term_memory"] = db.get_long_term_memory(user_id, limit=20)
        
        return user_data

    def _generate_statistics(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据统计信息
        
        Args:
            user_data: 用户数据
            
        Returns:
            Dict: 统计数据
        """
        stats = {
            "event_statistics": self._analyze_events(user_data["events"]),
            "pattern_statistics": self._analyze_patterns(user_data["patterns"]),
            "emotion_statistics": self._analyze_emotions(user_data["emotions"]),
            "engagement_statistics": self._analyze_engagement(user_data)
        }
        
        return stats

    def _analyze_events(self, events: List[Dict]) -> Dict[str, Any]:
        """分析事件数据
        
        Args:
            events: 事件列表
            
        Returns:
            Dict: 事件统计
        """
        if not events:
            return {"total_events": 0, "event_types": {}, "most_common_types": []}
        
        # 事件类型统计
        primary_types = [event.get("primaryType", "unknown") for event in events]
        sub_types = [event.get("subType", "unknown") for event in events]
        
        type_counter = Counter(primary_types)
        subtype_counter = Counter(sub_types)
        
        # 事件时间分布
        event_times = []
        for event in events:
            try:
                event_time = datetime.fromisoformat(event.get("time", ""))
                event_times.append(event_time)
            except:
                continue
        
        return {
            "total_events": len(events),
            "event_types": dict(type_counter),
            "event_subtypes": dict(subtype_counter),
            "most_common_types": type_counter.most_common(3),
            "most_common_subtypes": subtype_counter.most_common(5),
            "time_distribution": self._analyze_time_distribution(event_times),
            "event_status": Counter([event.get("status", "unknown") for event in events])
        }

    def _analyze_patterns(self, patterns: List[Dict]) -> Dict[str, Any]:
        """分析行为模式数据
        
        Args:
            patterns: 行为模式列表
            
        Returns:
            Dict: 模式统计
        """
        if not patterns:
            return {"total_patterns": 0, "common_patterns": [], "pattern_evolution": []}
        
        # 提取所有模式信息
        all_patterns = []
        triggers = []
        coping_strategies = []
        
        for pattern in patterns:
            if "behavioral_patterns" in pattern:
                bp = pattern["behavioral_patterns"]
                all_patterns.extend(bp.get("patterns", []))
                triggers.extend(bp.get("triggers", []))
                coping_strategies.extend(bp.get("coping_strategies", []))
        
        return {
            "total_patterns": len(patterns),
            "common_patterns": Counter(all_patterns).most_common(5),
            "common_triggers": Counter(triggers).most_common(5),
            "common_coping_strategies": Counter(coping_strategies).most_common(5),
            "pattern_evolution": self._analyze_pattern_evolution(patterns)
        }

    def _analyze_emotions(self, emotions: List[Dict]) -> Dict[str, Any]:
        """分析情绪数据
        
        Args:
            emotions: 情绪列表
            
        Returns:
            Dict: 情绪统计
        """
        if not emotions:
            return {"total_records": 0, "emotion_distribution": {}, "average_intensity": 0}
        
        # 情绪类别统计
        emotion_categories = [emotion.get("emotion_category", "unknown") for emotion in emotions]
        category_counter = Counter(emotion_categories)
        
        # 情绪强度统计
        intensities = []
        for emotion in emotions:
            try:
                intensity = float(emotion.get("emotion_score", 0))
                intensities.append(intensity)
            except:
                continue
        
        return {
            "total_records": len(emotions),
            "emotion_distribution": dict(category_counter),
            "most_common_emotions": category_counter.most_common(5),
            "average_intensity": statistics.mean(intensities) if intensities else 0,
            "intensity_range": {
                "min": min(intensities) if intensities else 0,
                "max": max(intensities) if intensities else 0,
                "median": statistics.median(intensities) if intensities else 0,
                "std_dev": statistics.stdev(intensities) if len(intensities) > 1 else 0
            },
            "emotion_trend": self._analyze_emotion_trend(emotions)
        }

    def _analyze_engagement(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户参与度
        
        Args:
            user_data: 用户数据
            
        Returns:
            Dict: 参与度统计
        """
        return {
            "total_sessions": len(user_data.get("patterns", [])),
            "total_events": len(user_data.get("events", [])),
            "total_emotions": len(user_data.get("emotions", [])),
            "memory_entries": len(user_data.get("long_term_memory", [])),
            "engagement_score": self._calculate_engagement_score(user_data)
        }

    def _analyze_time_distribution(self, event_times: List[datetime]) -> Dict[str, Any]:
        """分析事件时间分布
        
        Args:
            event_times: 事件时间列表
            
        Returns:
            Dict: 时间分布统计
        """
        if not event_times:
            return {"hourly_distribution": {}, "daily_distribution": {}, "weekly_distribution": {}}
        
        # 按小时分布
        hourly = Counter([dt.hour for dt in event_times])
        # 按星期分布
        weekly = Counter([dt.weekday() for dt in event_times])
        # 按日期分布
        daily = Counter([dt.date().isoformat() for dt in event_times])
        
        return {
            "hourly_distribution": dict(hourly),
            "weekly_distribution": dict(weekly),
            "daily_distribution": dict(daily)
        }

    def _analyze_pattern_evolution(self, patterns: List[Dict]) -> List[Dict]:
        """分析行为模式演变
        
        Args:
            patterns: 行为模式列表
            
        Returns:
            List: 模式演变趋势
        """
        if len(patterns) < 2:
            return []
        
        # 按时间排序
        sorted_patterns = sorted(patterns, key=lambda x: x.get("timestamp", ""))
        
        evolution = []
        for i in range(1, len(sorted_patterns)):
            prev_pattern = sorted_patterns[i-1]
            curr_pattern = sorted_patterns[i]
            
            evolution.append({
                "period": f"{prev_pattern.get('timestamp', '')} - {curr_pattern.get('timestamp', '')}",
                "changes": self._compare_patterns(prev_pattern, curr_pattern)
            })
        
        return evolution

    def _analyze_emotion_trend(self, emotions: List[Dict]) -> Dict[str, Any]:
        """分析情绪趋势
        
        Args:
            emotions: 情绪列表
            
        Returns:
            Dict: 情绪趋势
        """
        if not emotions:
            return {"trend": "stable", "recent_average": 0, "overall_direction": "neutral"}
        
        # 按时间排序
        sorted_emotions = sorted(emotions, key=lambda x: x.get("timestamp", ""))
        
        # 计算最近一周和总体平均值
        recent_week = [e for e in sorted_emotions if datetime.fromisoformat(e.get("timestamp", "")) >= datetime.now() - timedelta(days=7)]
        
        recent_scores = [float(e.get("emotion_score", 0)) for e in recent_week]
        overall_scores = [float(e.get("emotion_score", 0)) for e in sorted_emotions]
        
        recent_avg = statistics.mean(recent_scores) if recent_scores else 0
        overall_avg = statistics.mean(overall_scores) if overall_scores else 0
        
        # 判断趋势
        if recent_avg > overall_avg + 0.5:
            trend = "improving"
        elif recent_avg < overall_avg - 0.5:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "recent_average": recent_avg,
            "overall_average": overall_avg,
            "recent_period_days": 7,
            "score_difference": recent_avg - overall_avg
        }

    def _compare_patterns(self, prev_pattern: Dict, curr_pattern: Dict) -> List[str]:
        """比较两个行为模式的变化
        
        Args:
            prev_pattern: 前一个模式
            curr_pattern: 当前模式
            
        Returns:
            List: 变化描述
        """
        changes = []
        
        # 比较行为模式的主要字段
        if "behavioral_patterns" in prev_pattern and "behavioral_patterns" in curr_pattern:
            prev_bp = prev_pattern["behavioral_patterns"]
            curr_bp = curr_pattern["behavioral_patterns"]
            
            # 比较模式数量
            prev_count = len(prev_bp.get("patterns", []))
            curr_count = len(curr_bp.get("patterns", []))
            
            if curr_count > prev_count:
                changes.append(f"行为模式增加了{curr_count - prev_count}个")
            elif curr_count < prev_count:
                changes.append(f"行为模式减少了{prev_count - curr_count}个")
            
            # 比较应对策略
            prev_coping = set(prev_bp.get("coping_strategies", []))
            curr_coping = set(curr_bp.get("coping_strategies", []))
            
            new_coping = curr_coping - prev_coping
            lost_coping = prev_coping - curr_coping
            
            if new_coping:
                changes.append(f"新增应对策略: {', '.join(new_coping)}")
            if lost_coping:
                changes.append(f"减少应对策略: {', '.join(lost_coping)}")
        
        return changes

    def _calculate_engagement_score(self, user_data: Dict[str, Any]) -> float:
        """计算用户参与度评分
        
        Args:
            user_data: 用户数据
            
        Returns:
            float: 参与度评分 (0-10)
        """
        # 基于不同数据源的参与度权重
        weights = {
            "events": 0.3,
            "patterns": 0.25,
            "emotions": 0.2,
            "memory": 0.15,
            "profile": 0.1
        }
        
        scores = {
            "events": min(len(user_data.get("events", [])) / 10, 1.0),  # 最多10个事件得满分
            "patterns": min(len(user_data.get("patterns", [])) / 5, 1.0),  # 最多5个模式得满分
            "emotions": min(len(user_data.get("emotions", [])) / 20, 1.0),  # 最多20个情绪记录得满分
            "memory": min(len(user_data.get("long_term_memory", [])) / 10, 1.0),  # 最多10个记忆得满分
            "profile": 1.0 if user_data.get("user_profile") else 0.0  # 有用户画像得满分
        }
        
        engagement_score = sum(scores[key] * weights[key] for key in weights) * 10
        return round(engagement_score, 2)

    def _generate_ai_analysis(self, user_data: Dict[str, Any], statistics_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用AI生成深度分析
        
        Args:
            user_data: 用户数据
            statistics_data: 统计数据
            
        Returns:
            Dict: AI分析结果
        """
        try:
            # 准备分析数据
            analysis_input = {
                "user_data_summary": {
                    "total_events": len(user_data.get("events", [])),
                    "total_patterns": len(user_data.get("patterns", [])),
                    "total_emotions": len(user_data.get("emotions", [])),
                    "engagement_score": statistics_data.get("engagement_statistics", {}).get("engagement_score", 0)
                },
                "statistics": statistics_data
            }
            
            # 构建提示词
            prompt = f"""
            {self.analysis_prompt}
            
            用户数据分析：
            {json.dumps(analysis_input, ensure_ascii=False, indent=2)}
            
            请基于以上数据生成专业的心理健康分析报告。
            """
            
            # 调用AI生成分析
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            ai_analysis = json.loads(response.choices[0].message.content)
            return ai_analysis
            
        except Exception as e:
            print(f"Error in AI analysis: {str(e)}")
            return {
                "error": "AI分析生成失败",
                "fallback_analysis": self._generate_fallback_analysis(statistics_data)
            }

    def _generate_fallback_analysis(self, statistics_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成备用分析（当AI分析失败时使用）
        
        Args:
            statistics_data: 统计数据
            
        Returns:
            Dict: 备用分析结果
        """
        event_stats = statistics_data.get("event_statistics", {})
        emotion_stats = statistics_data.get("emotion_statistics", {})
        
        return {
            "summary": {
                "overallStatus": "需要进一步分析",
                "keyFindings": [
                    f"共记录了{event_stats.get('total_events', 0)}个事件",
                    f"情绪记录平均强度为{emotion_stats.get('average_intensity', 0):.1f}",
                    f"参与度评分为{statistics_data.get('engagement_statistics', {}).get('engagement_score', 0)}"
                ],
                "riskLevel": "unknown",
                "progressTrend": "需要更多数据"
            },
            "recommendations": {
                "immediate": ["继续记录情绪和事件", "保持定期交流"],
                "shortTerm": ["建立规律的自我反思习惯"],
                "longTerm": ["持续关注心理健康状况"]
            }
        }

    def export_report(self, report: Dict[str, Any], format_type: str = "json") -> str:
        """导出报告
        
        Args:
            report: 报告数据
            format_type: 导出格式 ("json", "text")
            
        Returns:
            str: 导出的报告内容
        """
        if format_type == "json":
            return json.dumps(report, ensure_ascii=False, indent=2)
        elif format_type == "text":
            return self._format_report_as_text(report)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def _format_report_as_text(self, report: Dict[str, Any]) -> str:
        """将报告格式化为文本
        
        Args:
            report: 报告数据
            
        Returns:
            str: 文本格式的报告
        """
        text_report = []
        text_report.append("=" * 50)
        text_report.append("用户心理健康分析报告")
        text_report.append("=" * 50)
        text_report.append(f"用户ID: {report.get('user_id', 'Unknown')}")
        text_report.append(f"生成时间: {report.get('generated_at', 'Unknown')}")
        text_report.append(f"分析周期: {report.get('analysis_period', {}).get('days', 'Unknown')}天")
        text_report.append("")
        
        # 数据摘要
        metadata = report.get("metadata", {})
        text_report.append("数据摘要:")
        text_report.append(f"- 分析会话数: {metadata.get('sessions_analyzed', 0)}")
        text_report.append(f"- 事件总数: {metadata.get('total_events', 0)}")
        text_report.append(f"- 行为模式数: {metadata.get('total_patterns', 0)}")
        text_report.append(f"- 情绪记录数: {metadata.get('emotion_records', 0)}")
        text_report.append("")
        
        # AI分析结果
        ai_analysis = report.get("ai_analysis", {})
        if "summary" in ai_analysis:
            summary = ai_analysis["summary"]
            text_report.append("整体评估:")
            text_report.append(f"- 健康状态: {summary.get('overallStatus', 'Unknown')}")
            text_report.append(f"- 风险等级: {summary.get('riskLevel', 'Unknown')}")
            text_report.append(f"- 进步趋势: {summary.get('progressTrend', 'Unknown')}")
            text_report.append("")
            
            key_findings = summary.get("keyFindings", [])
            if key_findings:
                text_report.append("主要发现:")
                for finding in key_findings:
                    text_report.append(f"- {finding}")
                text_report.append("")
        
        # 建议
        if "recommendations" in ai_analysis:
            recommendations = ai_analysis["recommendations"]
            text_report.append("建议:")
            
            immediate = recommendations.get("immediate", [])
            if immediate:
                text_report.append("立即建议:")
                for rec in immediate:
                    text_report.append(f"- {rec}")
            
            short_term = recommendations.get("shortTerm", [])
            if short_term:
                text_report.append("短期建议:")
                for rec in short_term:
                    text_report.append(f"- {rec}")
            
            long_term = recommendations.get("longTerm", [])
            if long_term:
                text_report.append("长期建议:")
                for rec in long_term:
                    text_report.append(f"- {rec}")
        
        text_report.append("")
        text_report.append("=" * 50)
        text_report.append("报告结束")
        text_report.append("=" * 50)
        
        return "\n".join(text_report) 