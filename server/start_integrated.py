#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
心理咨询对话系统启动脚本
使用集成版架构，统一管理所有数据和服务
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

def check_environment():
    """检查环境变量配置"""
    # 首先尝试加载环境变量
    try:
        from load_env import load_environment
        load_environment()
    except ImportError:
        print("⚠️ 无法加载环境变量模块，使用系统环境变量")
        from dotenv import load_dotenv
        load_dotenv()
    
    required_vars = [
        "OPENAI_API_KEY",
        "BASE_URL", 
        "MODEL_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请确保在.env文件中设置这些变量")
        return False
    
    print("✅ 环境变量检查通过")
    return True

def check_dependencies():
    """检查依赖包"""
    try:
        import flask
        import langchain_openai
        import langgraph
        import snownlp
        import pydantic
        print("✅ 依赖包检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_prompt_files():
    """检查提示文件"""
    prompt_dir = Path(__file__).parent / "prompt"
    required_files = [
        "counselor_prompt.txt",
        "planning_prompt.txt", 
        "guided_inquiry_prompt.txt",
        "pattern_analysis_prompt.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not (prompt_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ 缺少提示文件: {', '.join(missing_files)}")
        print("系统将使用默认提示模板")
    else:
        print("✅ 提示文件检查通过")
    
    return True

def initialize_data_directories():
    """初始化数据目录"""
    data_dir = Path(__file__).parent / "data"
    subdirs = ["messages", "patterns", "plans"]
    
    data_dir.mkdir(exist_ok=True)
    for subdir in subdirs:
        (data_dir / subdir).mkdir(exist_ok=True)
    
    print("✅ 数据目录初始化完成")

def start_server():
    """启动服务器"""
    print("🚀 启动心理咨询对话系统...")
    print("📊 使用集成版架构:")
    print("   - 统一数据库管理")
    print("   - 用户画像存储")
    print("   - 长短期记忆")
    print("   - 危机检测")
    print("   - 行为模式分析")
    print("   - 情绪评分")
    print("   - 智能日志记录")
    print()
    
    # 显示日志配置
    chat_logging = os.environ.get("ENABLE_CHAT_LOGGING", "true").lower() == "true"
    emotion_logging = os.environ.get("ENABLE_EMOTION_LOGGING", "true").lower() == "true"
    detailed_logging = os.environ.get("ENABLE_DETAILED_LOGGING", "true").lower() == "true"
    
    print("📝 日志配置:")
    print(f"   聊天日志: {'✅ 启用' if chat_logging else '❌ 禁用'}")
    print(f"   情绪日志: {'✅ 启用' if emotion_logging else '❌ 禁用'}")
    print(f"   详细日志: {'✅ 启用' if detailed_logging else '❌ 禁用'}")
    print()
    
    from app_test import app
    
    # 获取配置
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = os.environ.get("FLASK_ENV", "production") == "development"
    
    print(f"🌐 服务器地址: http://{HOST}:{PORT}")
    print(f"🔧 调试模式: {'开启' if DEBUG else '关闭'}")
    print()
    print("API端点:")
    print(f"  - POST http://{HOST}:{PORT}/api/chat - 聊天对话")
    print(f"  - GET  http://{HOST}:{PORT}/api/chat/history - 对话历史")
    print(f"  - POST http://{HOST}:{PORT}/api/mood - 情绪分析")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        app.run(host=HOST, port=PORT, debug=DEBUG)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")

def main():
    """主函数"""
    print("🩺 心理咨询对话系统 - 集成版")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        return
    
    if not check_dependencies():
        return
    
    check_prompt_files()
    initialize_data_directories()
    
    print("=" * 50)
    start_server()

if __name__ == "__main__":
    main()
