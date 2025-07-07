#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志配置管理脚本
用于快速切换日志功能的开启/关闭状态
"""

import os
import re
from pathlib import Path

def read_env_file():
    """读取.env文件内容"""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("❌ .env文件不存在")
        return None
    
    with open(env_file, 'r', encoding='utf-8') as f:
        return f.read()

def write_env_file(content):
    """写入.env文件内容"""
    env_file = Path(__file__).parent / ".env"
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)

def get_current_config():
    """获取当前日志配置"""
    content = read_env_file()
    if not content:
        return None
    
    config = {}
    for line in content.split('\n'):
        if line.startswith('ENABLE_CHAT_LOGGING='):
            config['chat'] = line.split('=')[1].lower() == 'true'
        elif line.startswith('ENABLE_EMOTION_LOGGING='):
            config['emotion'] = line.split('=')[1].lower() == 'true'
        elif line.startswith('ENABLE_DETAILED_LOGGING='):
            config['detailed'] = line.split('=')[1].lower() == 'true'
    
    return config

def update_config(chat_logging=None, emotion_logging=None, detailed_logging=None):
    """更新日志配置"""
    content = read_env_file()
    if not content:
        return False
    
    # 更新配置
    if chat_logging is not None:
        content = re.sub(
            r'ENABLE_CHAT_LOGGING=\w+',
            f'ENABLE_CHAT_LOGGING={str(chat_logging).lower()}',
            content
        )
    
    if emotion_logging is not None:
        content = re.sub(
            r'ENABLE_EMOTION_LOGGING=\w+',
            f'ENABLE_EMOTION_LOGGING={str(emotion_logging).lower()}',
            content
        )
    
    if detailed_logging is not None:
        content = re.sub(
            r'ENABLE_DETAILED_LOGGING=\w+',
            f'ENABLE_DETAILED_LOGGING={str(detailed_logging).lower()}',
            content
        )
    
    write_env_file(content)
    return True

def show_current_config():
    """显示当前配置"""
    config = get_current_config()
    if not config:
        return
    
    print("📝 当前日志配置:")
    print(f"   聊天日志: {'✅ 启用' if config.get('chat', False) else '❌ 禁用'}")
    print(f"   情绪日志: {'✅ 启用' if config.get('emotion', False) else '❌ 禁用'}")
    print(f"   详细日志: {'✅ 启用' if config.get('detailed', False) else '❌ 禁用'}")

def interactive_config():
    """交互式配置"""
    print("🔧 日志配置管理")
    print("=" * 40)
    
    show_current_config()
    print()
    
    print("选择操作:")
    print("1. 启用所有日志")
    print("2. 禁用所有日志")
    print("3. 只启用聊天日志")
    print("4. 只启用情绪日志")
    print("5. 自定义配置")
    print("6. 查看当前配置")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (0-6): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                update_config(True, True, True)
                print("✅ 已启用所有日志功能")
            elif choice == '2':
                update_config(False, False, False)
                print("✅ 已禁用所有日志功能")
            elif choice == '3':
                update_config(True, False, False)
                print("✅ 已启用聊天日志，禁用其他日志")
            elif choice == '4':
                update_config(False, True, False)
                print("✅ 已启用情绪日志，禁用其他日志")
            elif choice == '5':
                custom_config()
            elif choice == '6':
                show_current_config()
            else:
                print("❌ 无效选择，请重新输入")
                continue
            
            if choice in ['1', '2', '3', '4', '5']:
                print("\n更新后的配置:")
                show_current_config()
                print("\n⚠️  重启服务器后配置生效")
            
        except KeyboardInterrupt:
            print("\n👋 退出配置管理")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def custom_config():
    """自定义配置"""
    print("\n🎛️  自定义日志配置")
    
    try:
        chat = input("启用聊天日志? (y/n): ").lower().startswith('y')
        emotion = input("启用情绪日志? (y/n): ").lower().startswith('y')
        detailed = input("启用详细日志? (y/n): ").lower().startswith('y')
        
        update_config(chat, emotion, detailed)
        print("✅ 自定义配置已保存")
        
    except Exception as e:
        print(f"❌ 配置失败: {e}")

def quick_toggle(mode):
    """快速切换模式"""
    if mode == "all-on":
        update_config(True, True, True)
        print("✅ 已启用所有日志")
    elif mode == "all-off":
        update_config(False, False, False)
        print("✅ 已禁用所有日志")
    elif mode == "chat-only":
        update_config(True, False, False)
        print("✅ 仅启用聊天日志")
    elif mode == "emotion-only":
        update_config(False, True, False)
        print("✅ 仅启用情绪日志")
    else:
        print("❌ 无效模式")
        return False
    
    show_current_config()
    print("⚠️  重启服务器后配置生效")
    return True

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        # 命令行模式
        mode = sys.argv[1]
        if not quick_toggle(mode):
            print("用法: python config_logging.py [all-on|all-off|chat-only|emotion-only]")
    else:
        # 交互模式
        interactive_config()

"""
# 命令行快速切换
python config_logging.py all-on    # 启用所有日志
python config_logging.py all-off   # 禁用所有日志
python config_logging.py chat-only # 只启用聊天日志

# 直接运行进入交互模式
python config_logging.py
"""
if __name__ == "__main__":
    main()
