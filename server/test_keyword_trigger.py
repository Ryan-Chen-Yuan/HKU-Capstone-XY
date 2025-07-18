#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试"知己报告"关键词触发功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from service.chat_langgraph_optimized import optimized_chat
from dao.database import Database
from datetime import datetime
import json

def create_sample_data():
    """创建一些示例数据来测试报告生成"""
    db = Database()
    user_id = "keyword_test_user"
    session_id = "keyword_test_session"
    
    # 创建一些示例对话
    messages = [
        {"role": "user", "content": "我最近感觉有些焦虑", "timestamp": datetime.now().isoformat()},
        {"role": "agent", "content": "我理解你的感受，能告诉我更多吗？", "timestamp": datetime.now().isoformat()},
        {"role": "user", "content": "工作压力比较大", "timestamp": datetime.now().isoformat()},
        {"role": "agent", "content": "工作压力确实会影响心理健康", "timestamp": datetime.now().isoformat()}
    ]
    
    for message in messages:
        db.save_message(session_id, user_id, message["role"], message["content"], message["timestamp"])
    
    # 创建一些示例事件
    events = [
        {
            "primaryType": "工作压力",
            "subType": "deadline",
            "description": "项目截止日期临近",
            "time": datetime.now().isoformat(),
            "severity": "medium"
        }
    ]
    
    db.save_events(session_id, events)
    
    # 创建一些示例情绪数据
    emotions = [
        {"emotion_category": "焦虑", "emotion_score": -0.5},
        {"emotion_category": "压力", "emotion_score": -0.6},
        {"emotion_category": "疲惫", "emotion_score": -0.4}
    ]
    
    for emotion in emotions:
        db.save_emotion_score(user_id, session_id, emotion["emotion_score"], emotion["emotion_category"])
    
    print(f"✅ 创建示例数据完成 - 用户: {user_id}, 会话: {session_id}")
    return user_id, session_id

def test_keyword_variations():
    """测试不同的关键词变体"""
    
    # 创建示例数据
    user_id, session_id = create_sample_data()
    
    # 测试不同的关键词触发方式
    test_cases = [
        # 直接关键词
        "知己报告",
        "生成报告", 
        "分析报告",
        "心理分析",
        "综合分析",
        "个人报告",
        "健康报告",
        "心理报告",
        "总结报告",
        "评估报告",
        
        # 组合表达
        "请生成知己报告",
        "我需要知己报告",
        "帮我生成知己报告",
        "可以给我一个知己报告吗",
        "我想要一份知己报告",
        "请帮我做一个知己报告",
        
        # 句子中包含关键词
        "我想看看我的知己报告",
        "能否提供一份心理分析报告",
        "我需要了解我的健康报告",
        "请为我生成一个综合分析",
        
        # 非触发词（对照组）
        "你好",
        "谢谢",
        "我想聊天",
        "今天天气怎么样"
    ]
    
    print("\n🔍 测试关键词触发功能...")
    print("=" * 60)
    
    results = []
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📝 测试 {i:2d}: '{test_input}'")
        
        try:
            # 使用相同的用户和会话来累积数据
            result = optimized_chat(
                user_input=test_input,
                user_id=user_id,
                session_id=session_id,
                enable_performance_monitoring=True
            )
            
            # 检查是否触发了分析报告
            triggered = bool(result.get("analysis_report"))
            response = result.get("response", "")
            
            # 检查响应是否包含报告内容
            has_report_content = "知己报告" in response and "全面心理健康分析报告" in response
            
            # 记录结果
            test_result = {
                "input": test_input,
                "triggered": triggered,
                "has_report_content": has_report_content,
                "response_length": len(response),
                "performance": result.get("performance", {}),
                "crisis_detected": result.get("crisis_detected", False)
            }
            
            results.append(test_result)
            
            # 显示结果
            status = "✅" if triggered else "❌"
            content_status = "✅" if has_report_content else "❌"
            
            print(f"   触发报告: {status}")
            print(f"   包含报告内容: {content_status}")
            print(f"   响应长度: {len(response)} 字符")
            
            if triggered:
                print(f"   📊 报告数据摘要:")
                if result.get("analysis_report"):
                    metadata = result["analysis_report"].get("metadata", {})
                    print(f"      - 数据完整度: {metadata.get('data_completeness', 0):.1f}%")
                    print(f"      - 分析可信度: {metadata.get('analysis_confidence', 0):.1f}%")
                    print(f"      - 分析的数据: {metadata.get('total_sessions', 0)}会话, {metadata.get('total_events', 0)}事件, {metadata.get('total_emotions', 0)}情绪")
                
                # 显示性能信息
                if "performance" in result:
                    perf = result["performance"]
                    print(f"      - 处理时间: {perf.get('total_time', 0):.2f}秒")
            
            # 显示响应前100字符
            if response:
                preview = response[:100].replace('\n', ' ')
                print(f"   响应预览: {preview}...")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {str(e)}")
            results.append({
                "input": test_input,
                "triggered": False,
                "error": str(e)
            })
    
    return results

def analyze_results(results):
    """分析测试结果"""
    print("\n" + "=" * 60)
    print("📊 测试结果分析")
    print("=" * 60)
    
    # 统计触发成功的关键词
    triggered_keywords = [r for r in results if r.get("triggered", False)]
    non_triggered = [r for r in results if not r.get("triggered", False)]
    
    print(f"\n✅ 成功触发报告的关键词数量: {len(triggered_keywords)}")
    print(f"❌ 未触发报告的输入数量: {len(non_triggered)}")
    print(f"📈 触发成功率: {len(triggered_keywords) / len(results) * 100:.1f}%")
    
    # 显示成功触发的关键词
    if triggered_keywords:
        print(f"\n🎯 成功触发的关键词:")
        for result in triggered_keywords:
            status = "✅" if result.get("has_report_content", False) else "⚠️"
            print(f"   {status} '{result['input']}'")
    
    # 显示未触发的输入（应该是非关键词）
    if non_triggered:
        print(f"\n🚫 未触发的输入:")
        for result in non_triggered:
            if "error" in result:
                print(f"   ❌ '{result['input']}' (错误: {result['error']})")
            else:
                print(f"   ✅ '{result['input']}' (正确未触发)")
    
    # 性能统计
    triggered_with_perf = [r for r in triggered_keywords if r.get("performance")]
    if triggered_with_perf:
        avg_time = sum(r["performance"].get("total_time", 0) for r in triggered_with_perf) / len(triggered_with_perf)
        print(f"\n⚡ 平均处理时间: {avg_time:.2f}秒")
    
    # 检查预期的行为
    print(f"\n🔍 预期行为检查:")
    
    # 应该触发的关键词
    expected_triggers = ["知己报告", "生成报告", "分析报告", "心理分析", "综合分析", "个人报告", "健康报告", "心理报告", "总结报告", "评估报告"]
    
    for keyword in expected_triggers:
        triggered_results = [r for r in results if keyword in r["input"] and r.get("triggered", False)]
        if triggered_results:
            print(f"   ✅ '{keyword}' 正确触发")
        else:
            print(f"   ❌ '{keyword}' 未能触发")
    
    # 不应该触发的输入
    non_trigger_inputs = ["你好", "谢谢", "我想聊天", "今天天气怎么样"]
    for input_text in non_trigger_inputs:
        non_triggered_results = [r for r in results if r["input"] == input_text and not r.get("triggered", False)]
        if non_triggered_results:
            print(f"   ✅ '{input_text}' 正确未触发")
        else:
            print(f"   ❌ '{input_text}' 意外触发")

def main():
    """主测试函数"""
    print("🚀 开始测试知己报告关键词触发功能")
    print("=" * 60)
    
    try:
        # 执行关键词测试
        results = test_keyword_variations()
        
        # 分析结果
        analyze_results(results)
        
        print(f"\n🎉 测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 