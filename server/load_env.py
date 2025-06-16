#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv


def load_environment():
    """加载环境变量"""
    # 尝试从.env文件加载环境变量
    env_file = os.path.join(os.path.dirname(__file__), ".env")

    if os.path.exists(env_file):
        load_dotenv(env_file)
        print("已加载环境变量配置文件：.env")
    else:
        print("警告：未找到.env文件。请创建该文件并设置必要的环境变量。")
        print("可以复制.env.example文件作为模板：cp .env .env")

    # 检查对话模型的必要环境变量
    if not os.environ.get("CHAT_API_KEY"):
        print("错误：未设置CHAT_API_KEY环境变量（对话模型）。请在.env文件中设置。")
        return False
        
    if not os.environ.get("CHAT_MODEL_NAME"):
        print("错误：未设置CHAT_MODEL_NAME环境变量（对话模型）。请在.env文件中设置。")
        return False
        
    if not os.environ.get("CHAT_BASE_URL"):
        print("错误：未设置CHAT_BASE_URL环境变量（对话模型）。请在.env文件中设置。")
        return False

    # 检查事件提取模型的必要环境变量
    if not os.environ.get("EVENT_API_KEY"):
        print("错误：未设置EVENT_API_KEY环境变量（事件提取模型）。请在.env文件中设置。")
        return False
        
    if not os.environ.get("EVENT_MODEL_NAME"):
        print("错误：未设置EVENT_MODEL_NAME环境变量（事件提取模型）。请在.env文件中设置。")
        return False
        
    if not os.environ.get("EVENT_BASE_URL"):
        print("错误：未设置EVENT_BASE_URL环境变量（事件提取模型）。请在.env文件中设置。")
        return False

    print(f"对话模型配置: {os.environ.get('CHAT_MODEL_NAME')} @ {os.environ.get('CHAT_BASE_URL')}")
    print(f"事件提取模型配置: {os.environ.get('EVENT_MODEL_NAME')} @ {os.environ.get('EVENT_BASE_URL')}")

    # 打印功能控制参数信息
    guided_inquiry_enabled = os.environ.get("ENABLE_GUIDED_INQUIRY", "true").lower() == "true"
    pattern_analysis_enabled = os.environ.get("ENABLE_PATTERN_ANALYSIS", "true").lower() == "true"
    
    print(f"引导性询问功能: {'启用' if guided_inquiry_enabled else '禁用'}")
    print(f"行为模式分析功能: {'启用' if pattern_analysis_enabled else '禁用'}")
    
    # 打印日志配置信息
    chat_logging_enabled = os.environ.get("ENABLE_CHAT_LOGGING", "true").lower() == "true"
    emotion_logging_enabled = os.environ.get("ENABLE_EMOTION_LOGGING", "true").lower() == "true"
    detailed_logging_enabled = os.environ.get("ENABLE_DETAILED_LOGGING", "true").lower() == "true"
    
    print(f"聊天日志记录: {'启用' if chat_logging_enabled else '禁用'}")
    print(f"情绪评分日志: {'启用' if emotion_logging_enabled else '禁用'}")
    print(f"详细日志信息: {'启用' if detailed_logging_enabled else '禁用'}")

    # 打印功能控制参数信息
    guided_inquiry_enabled = os.environ.get("ENABLE_GUIDED_INQUIRY", "true").lower() == "true"
    pattern_analysis_enabled = os.environ.get("ENABLE_PATTERN_ANALYSIS", "true").lower() == "true"
    
    print(f"引导性询问功能: {'启用' if guided_inquiry_enabled else '禁用'}")
    print(f"行为模式分析功能: {'启用' if pattern_analysis_enabled else '禁用'}")

    return True


if __name__ == "__main__":
    if load_environment():
        print("环境变量加载成功！")
    else:
        print("环境变量加载失败。请检查配置。")
        sys.exit(1)
