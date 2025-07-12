# 微信小程序聊天后端

这是微信小程序的聊天后端服务，使用Python和Flask实现，提供与OpenAI LLM模型的通信功能。

## 功能

- 实现微信小程序与AI助手的对话
- 处理聊天历史记录
- 生成情绪标签用于小怪物表情变化
- 持久化存储对话记录

## 快速开始

### 前提条件

- Python 3.11+
- OpenAI API 密钥

### 安装

1. 克隆仓库或进入已下载的项目目录

2. 安装依赖

```bash
cd server
pip install -r requirements.txt
```

3. 配置环境变量

复制环境变量示例文件并进行配置：

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，设置您的 OpenAI API 密钥和功能控制参数：


### 启动服务器

```bash
python start.py
```

服务器默认将在 http://localhost:5858 上运行。

## API 文档

### 发送消息并获取AI回复

**请求:**

```
POST /api/chat
```

**请求体:**

```json
{
  "user_id": "user123",
  "session_id": "session456", 
  "message": "你好，我今天感觉不太好",
  "timestamp": "2023-04-01T12:00:00Z",
  "history": [
    {
      "role": "user",
      "content": "你是谁？",
      "timestamp": "2023-04-01T11:58:00Z"
    },
    {
      "role": "agent",
      "content": "你好！我是知己咨询师，很高兴认识你！有什么我可以帮你的吗？",
      "timestamp": "2023-04-01T11:58:05Z"
    }
  ]
}
```

**响应:**

```json
{
  "message_id": "msg_12345",
  "content": "很遗憾听到你今天感觉不太好。你能告诉我是什么让你感到不舒服吗？或许我可以提供一些帮助。",
  "emotion": "sad",
  "timestamp": "2023-04-01T12:00:10Z",
  "session_id": "session456"
}
```

### 获取历史对话记录

**请求:**

```
GET /api/chat/history?user_id=user123&session_id=session456
```

**响应:**

```json
{
  "session_id": "session456",
  "history": [
    {
      "role": "user",
      "content": "你是谁？",
      "timestamp": "2023-04-01T11:58:00Z"
    },
    {
      "role": "agent",
      "content": "你好！我是知己咨询师，很高兴认识你！有什么我可以帮你的吗？",
      "timestamp": "2023-04-01T11:58:05Z"
    },
    {
      "role": "user",
      "content": "你好，我今天感觉不太好",
      "timestamp": "2023-04-01T12:00:00Z"
    },
    {
      "role": "agent",
      "content": "很遗憾听到你今天感觉不太好。你能告诉我是什么让你感到不舒服吗？或许我可以提供一些帮助。",
      "timestamp": "2023-04-01T12:00:10Z"
    }
  ],
  "count": 4
}
```

### 情绪分析

**请求:**

```
POST /api/mood
```

**请求体:**

```json
{
  "user_id": "user123",
  "session_id": "session456",
  "messages": ["我今天感觉不太好", "有点担心工作的事情"]
}
```

**响应:**

```json
{
  "message_id": "msg_c68a9920",
  "moodCategory": "忧郁",
  "moodIntensity": 5,
  "scene": "在思考工作相关的事情",
  "session_id": "session456",
  "thinking": "我有点担心工作的事情",
  "timestamp": "2025-07-06T03:20:25.903258"
}
```

## 自定义Prompt

咨询师的Prompt模板位于 `prompt/counselor_prompt.txt` 文件中，可以根据需要进行修改。

## 目前版本情绪相关流程

```
用户消息 → SnowNLP情绪评分 → 实时日志记录
         ↓
       LLM 情绪分析 → 详细情绪信息 → 影响AI回复策略
         ↓
       保存到数据库 → 用户画像更新 → 长期情绪跟踪
```

### 情绪分析说明

1. **情绪评分**: 使用SnowNLP对用户消息进行实时情绪评分（-1到1范围）
2. **情绪强度**: 通过OpenAI API分析得出情绪强度（0-10范围）
3. **情绪类别**: 具体的情绪分类（如：开心、悲伤、焦虑、忧郁等）
4. **内心独白**: AI推测的用户内心想法
5. **情绪场景**: 产生该情绪的具体场景描述

### 危机检测

系统会自动检测用户消息中的危机信号，包括：
- 高危关键词检测
- 情绪极性分析
- 当检测到危机时，会优先提供心理援助信息

## 数据存储

聊天记录将存储在 `data` 目录下：
- 会话记录：每个会话都有单独的JSON文件
- 用户画像：`user_profiles.json`
- 长期记忆：`long_term_memory.json`
- 情绪评分：`emotion_scores.json`
- 会话元数据：`sessions.json`

### 数据目录结构

```
data/
├── messages/           # 聊天消息记录
│   ├── session1.json
│   └── session2.json
├── plans/             # 对话计划
│   ├── session1.json
│   └── default_user.json
├── user_profiles.json  # 用户画像
├── long_term_memory.json  # 长期记忆
├── emotion_scores.json    # 情绪评分记录
└── sessions.json         # 会话元数据
```

## 开发

要启用开发模式，请将 `.env` 文件中的 `FLASK_ENV` 设置为 `development`。 