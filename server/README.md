# 微信小程序聊天后端

这是微信小程序的聊天后端服务，使用Python和Flask实现，提供与OpenAI LLM模型的通信功能。

## 功能

- 实现微信小程序与AI助手的对话
- 处理聊天历史记录
- 生成情绪标签用于小怪物表情变化
- 持久化存储对话记录

## 快速开始

### 前提条件

- Python 3.8+
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

然后编辑 `.env` 文件，设置您的 OpenAI API 密钥：

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 启动服务器

```bash
python app.py
```

服务器默认将在 http://localhost:5000 上运行。

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
  "messages": [
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
  ]
}
```

## 自定义Prompt

咨询师的Prompt模板位于 `prompt/counselor_prompt.txt` 文件中，可以根据需要进行修改。

## 数据存储

聊天记录将存储在 `data` 目录下。每个会话都有一个单独的JSON文件，会话元数据存储在 `sessions.json` 文件中。

## 开发

要启用开发模式，请将 `.env` 文件中的 `FLASK_ENV` 设置为 `development`。 