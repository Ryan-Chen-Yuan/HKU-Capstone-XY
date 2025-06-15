# Planning Tool 数据结构文档

## Plan 数据结构

```json
{
    "session_id": "string",  // 会话唯一标识符
    "user_intent": {         // 用户意图
        "type": "string",    // 意图类型：如"情绪支持"、"问题解决"、"关系咨询"等
        "description": "string",  // 意图详细描述
        "confidence": float,  // 意图识别的置信度 (0-1)
        "identified_at": "timestamp"  // 意图识别时间
    },
    "current_state": {       // 当前对话状态
        "stage": "string",   // 当前阶段：如"意图识别"、"问题探索"、"建议提供"等
        "progress": float,   // 整体进度 (0-1)
        "last_updated": "timestamp"  // 最后更新时间
    },
    "steps": [              // 对话步骤列表
        {
            "id": "string",  // 步骤ID
            "type": "string", // 步骤类型：如"询问"、"共情"、"建议"等
            "content": "string", // 步骤内容
            "status": "string",  // 状态：pending/completed/skipped
            "created_at": "timestamp", // 创建时间
            "completed_at": "timestamp" // 完成时间（如果已完成）
        }
    ],
    "context": {            // 上下文信息
        "key_points": ["string"], // 关键信息点
        "emotions": ["string"],   // 情绪变化
        "concerns": ["string"]    // 关注点
    }
}
```

## 数据结构说明

1. **session_id**: 用于唯一标识一个对话会话
2. **user_intent**: 记录用户的咨询意图
   - type: 意图的主要类型
   - description: 对意图的详细描述
   - confidence: 意图识别的置信度
   - identified_at: 意图被识别的时间戳

3. **current_state**: 记录当前对话的状态
   - stage: 当前所处的对话阶段
   - progress: 整体进度
   - last_updated: 最后更新时间

4. **steps**: 对话步骤列表
   - id: 步骤的唯一标识符
   - type: 步骤的类型
   - content: 步骤的具体内容
   - status: 步骤的完成状态
   - created_at: 步骤创建时间
   - completed_at: 步骤完成时间

5. **context**: 对话上下文信息
   - key_points: 对话中的关键信息点
   - emotions: 用户表达的情绪变化
   - concerns: 用户的主要关注点

## 使用说明

1. 每个新的对话会话都会创建一个新的plan
2. plan会随着对话的进行不断更新
3. 当用户意图不明确时，会添加询问意图的步骤
4. 每个步骤完成后，会更新plan的状态
5. 根据对话进展，可能会添加新的步骤 