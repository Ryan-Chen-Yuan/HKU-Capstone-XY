# 环境变量配置说明

为了避免 Rate Limit 问题，我们将对话模型和事件提取模型分离，使用不同的 API Key 和模型。

## 环境变量配置

请在 `server/.env` 文件中配置以下环境变量：

```bash
# 对话模型配置（建议使用 DeepSeek）
CHAT_API_KEY=your_deepseek_api_key_here
CHAT_MODEL_NAME=deepseek-chat
CHAT_BASE_URL=https://api.sambanova.ai/v1

# 事件提取模型配置（建议使用 Qwen3-32B）
EVENT_API_KEY=your_qwen_api_key_here
EVENT_MODEL_NAME=Qwen/Qwen2.5-32B-Instruct
EVENT_BASE_URL=https://api.sambanova.ai/v1

# 服务器配置
HOST=0.0.0.0
PORT=5858
FLASK_ENV=development
```

## 模型分工

- **对话模型（DeepSeek）**: 负责用户对话回复和情绪分析
- **事件提取模型（Qwen3-32B）**: 负责从对话中提取关键事件

这样可以避免单个模型的 Rate Limit 问题，并且可以针对不同任务选择最适合的模型。 