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
        print("可以复制.env.example文件作为模板：cp .env.example .env")

    # 检查必要的环境变量
    if not os.environ.get("OPENAI_API_KEY"):
        print("错误：未设置OPENAI_API_KEY环境变量。请在.env文件中设置。")
        return False

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
