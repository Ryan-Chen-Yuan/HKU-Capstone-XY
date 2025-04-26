# 聊天API文档

## 概述

本API提供微信小程序与后端AI服务的通信接口，实现用户与AI助手的对话功能。

## 基本信息

- 基础URL: `http://your-server-domain/api`
- 数据格式: JSON
- 认证方式: 通过`user_id`字段验证用户身份

## 接口列表

### 1. 发送消息并获取AI回复

**请求**

```
POST /chat
```

**请求参数**

| 参数名 | 类型 | 必填 | 描述 |
|------|------|------|------|
| user_id | String | 是 | 用户唯一标识符 |
| session_id | String | 否 | 会话ID，用于跟踪对话上下文。若不提供则创建新会话 |
| message | String | 是 | 用户发送的消息内容 |
| timestamp | String | 否 | 消息发送的时间戳，ISO 8601格式。若不提供则使用服务器时间 |
| history | Array | 否 | 对话历史记录，用于提供上下文。若不提供或session_id已存在，则使用服务器保存的历史记录 |

**响应**

```json
{
  "message_id": "msg_123456",
  "content": "AI助手的回复内容",
  "timestamp": "2023-04-01T12:00:00Z",
  "emotion": "happy"
}
```

**错误响应**

```json
{
  "error_code": 400,
  "error_message": "无效的请求参数"
}
```

### 2. 获取历史对话记录

**请求**

```
GET /chat/history?user_id=123&session_id=abc
```

**请求参数**

| 参数名 | 类型 | 必填 | 描述 |
|------|------|------|------|
| user_id | String | 是 | 用户唯一标识符 |
| session_id | String | 是 | 会话ID |

**响应**

```json
{
  "session_id": "abc",
  "messages": [
    {
      "role": "user",
      "content": "你好",
      "timestamp": "2023-04-01T12:00:00Z"
    },
    {
      "role": "agent",
      "content": "你好！我是AI助手，有什么可以帮助你的吗？",
      "timestamp": "2023-04-01T12:00:01Z"
    }
  ]
}
```

## 状态码

| 状态码 | 描述 |
|------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 注意事项

1. 所有请求和响应的Content-Type应为`application/json`
2. 对话历史记录会在服务器端保存一段时间，但客户端应当自行维护完整的对话历史
3. 为提高响应速度，建议在请求中包含必要的历史消息以提供上下文 