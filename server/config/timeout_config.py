#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
超时配置管理
统一管理系统中各种超时设置，便于调优和维护
"""

import os

class TimeoutConfig:
    """超时配置类"""
    
    # 网络搜索相关超时
    SEARCH_API_TIMEOUT = int(os.environ.get("SEARCH_API_TIMEOUT", "15"))  # SerpAPI超时
    SEARCH_RETRY_COUNT = int(os.environ.get("SEARCH_RETRY_COUNT", "2"))   # 搜索重试次数
    
    # LLM客户端超时
    CHAT_LLM_TIMEOUT = int(os.environ.get("CHAT_LLM_TIMEOUT", "60"))       # 主聊天LLM超时
    MOOD_LLM_TIMEOUT = int(os.environ.get("MOOD_LLM_TIMEOUT", "45"))       # 情绪分析LLM超时
    EVENT_LLM_TIMEOUT = int(os.environ.get("EVENT_LLM_TIMEOUT", "45"))     # 事件提取LLM超时
    ANALYSIS_LLM_TIMEOUT = int(os.environ.get("ANALYSIS_LLM_TIMEOUT", "120")) # 分析报告LLM超时
    
    # 前端请求超时
    FRONTEND_CHAT_TIMEOUT = int(os.environ.get("FRONTEND_CHAT_TIMEOUT", "120000"))      # 前端聊天请求超时(毫秒)
    FRONTEND_HISTORY_TIMEOUT = int(os.environ.get("FRONTEND_HISTORY_TIMEOUT", "30000")) # 前端历史记录请求超时(毫秒)
    
    # 计划更新重试
    PLAN_UPDATE_RETRY = int(os.environ.get("PLAN_UPDATE_RETRY", "2"))      # 计划更新重试次数
    
    # 数据库操作超时
    DB_OPERATION_TIMEOUT = int(os.environ.get("DB_OPERATION_TIMEOUT", "30"))  # 数据库操作超时
    
    @classmethod
    def get_config_summary(cls) -> str:
        """获取配置摘要"""
        return f"""
当前超时配置:
=================
🔍 网络搜索:
   - API超时: {cls.SEARCH_API_TIMEOUT}秒
   - 重试次数: {cls.SEARCH_RETRY_COUNT}次

🤖 LLM服务:
   - 聊天LLM: {cls.CHAT_LLM_TIMEOUT}秒
   - 情绪分析: {cls.MOOD_LLM_TIMEOUT}秒
   - 事件提取: {cls.EVENT_LLM_TIMEOUT}秒
   - 分析报告: {cls.ANALYSIS_LLM_TIMEOUT}秒

📱 前端请求:
   - 聊天请求: {cls.FRONTEND_CHAT_TIMEOUT/1000:.1f}秒
   - 历史记录: {cls.FRONTEND_HISTORY_TIMEOUT/1000:.1f}秒

🔄 系统机制:
   - 计划更新重试: {cls.PLAN_UPDATE_RETRY}次
   - 数据库操作: {cls.DB_OPERATION_TIMEOUT}秒
=================
"""
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置的合理性"""
        issues = []
        
        # 检查搜索超时是否合理
        if cls.SEARCH_API_TIMEOUT < 5:
            issues.append("⚠️ 搜索API超时时间过短，可能导致频繁超时")
        elif cls.SEARCH_API_TIMEOUT > 30:
            issues.append("⚠️ 搜索API超时时间过长，可能影响用户体验")
            
        # 检查LLM超时是否合理
        if cls.CHAT_LLM_TIMEOUT < 30:
            issues.append("⚠️ 聊天LLM超时时间过短，可能导致复杂回复超时")
        elif cls.ANALYSIS_LLM_TIMEOUT < 60:
            issues.append("⚠️ 分析报告LLM超时时间过短，报告生成可能失败")
            
        # 检查前端超时是否匹配后端
        if cls.FRONTEND_CHAT_TIMEOUT/1000 < cls.CHAT_LLM_TIMEOUT + 10:
            issues.append("⚠️ 前端聊天超时应该比后端LLM超时多10秒以上")
            
        if issues:
            print("配置验证发现问题:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("✅ 配置验证通过")
            return True

if __name__ == "__main__":
    print(TimeoutConfig.get_config_summary())
    TimeoutConfig.validate_config()
