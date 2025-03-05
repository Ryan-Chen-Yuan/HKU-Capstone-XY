# Detailed Proposal Draft

---

## 1. Background

### 1.1 心理咨询市场

- **供需失衡**：中国心理咨询师缺口大，单次咨询费用普遍在500-1000元区间，形成高门槛服务。
- **地域限制**：专业资源集中在一线城市集中，二三线城市用户获取服务困难。
- **认知滞后**：潜在需求者因"病耻感"回避线下咨询。

### 1.2 竞品报告

- **情智星球**：<https://www.sohu.com/a/830612921_122042791>
- **AI心语**：<https://news.qq.com/rain/a/20241106A09XWS00>

### 1.3 AI's scope

#### Pros

1. **颠覆性的成本结构**：以DeepSeek模型价格为例，每百万Token仅需几块钱，远低于人类心理咨询师价格。且不受地点、时间安排等限制。
2. **实时情绪响应**：7x24在线提供情感支持和安慰，帮助青少年表达和理解自己的情绪。
3. **信息和资源提供**：提供关于心理健康、应对策略等方面的信息。

#### Cons

1. **深层次的情感问题**：如创伤处理、深层次的自我认同问题等，需要专业心理咨询师的介入。
2. **紧急情况**：如自杀倾向、严重的心理危机等，需要即时的专业干预。
3. **法律和医学问题**：如家庭暴力、严重精神疾病等，需要专业的法律和医学介入。
4. **用户认同问题**：LLM的回复有时较为空泛，无法实现人与人之间的情感链接，用户可能主观上不愿与AI交流心理问题。

### 法律和伦理风险

1. **创伤处理的次生风险**：对PTSD来访者的暴露疗法需要精确把握情绪唤醒度。LLM无法通过生理指标（心率、呼吸频率等）实时调节干预强度，可能导致二次创伤。2023年加拿大某AI咨询平台因此被集体诉讼。
2. **道德判断的算法困境**：面对自杀倾向等危机情况，人类咨询师需要在保密原则与生命权保护间进行价值权衡。LLM的决策受训练数据分布主导，可能产生统计学正确但伦理失当的应对，如过度强调隐私保护而延误危机干预。
3. **责任归属的模糊性**：当AI建议引发不良后果时，责任链条涉及算法开发者、数据提供方、部署机构等多个主体，形成"责任稀释效应"。2021年意大利ChatGPT禁令事件已暴露出此类法律真空。

## Scope

### 不做咨询师

### 不做模型优化

### 不做TTS(Text to Speech)

### 做倾听者

AI倾听情绪输出，给予情绪肯定。

### 做内容社区

由用户发帖驱动的日常case、心理学习资源、咨询经历分享。

匿名树洞 + AI情感共鸣 ： 用户可以分享自己的心理困扰、日常情绪或成长故事，LLM 自动生成鼓励性回复或建议（比如“你最近感觉焦虑，试试深呼吸或写日记吧”）。
示例：发布“职场压力”故事的用户，会收到AI整理的相关CBT技巧，并进入“打工人互助小组”聊天室。

### 做评测工具：心理量表。

## Object & Metric

针对心理咨询AI Agent的功能设计，以下是各模块可量化的指标及设计目标建议：

---

### **一、倾听者模块：情绪陪伴与肯定**

1. **情绪识别准确率**  
   - 目标：≥90%的情绪标签精准匹配（基于NLP情感分析）  
   - 指标：与专业心理咨询师标注结果的一致性对比  
   - 参考依据：情智星球的"情绪识别准确性"维度

2. **对话满意度评分**  
   - 目标：用户主观评分≥4.5/5分  
   - 测量：每次对话后嵌入轻量级问卷（如1-2题）  

---

### **二、推荐者模块：资源精准匹配**

1. **推荐准确率**  
   - 目标：≥85%的资源推荐符合用户当前心理状态  
   - 算法依据：结合用户画像（如MBTI/Big5）与动态情绪数据  

2. **资源采纳率**  
   - 目标：推荐资源的点击率≥70%，咨询师匹配点击率≥60%  
   - 优化方向：基于用户行为数据的协同过滤算法迭代  

3. **群体匹配有效性**  
   - 目标：用户加入群体后30天留存率≥50%  
   - 评估：通过群体互动频率与情绪改善指标交叉验证  

---

### **三、评测工具模块：科学评估体系**

1. **心理测评一致性**  
   - 目标：与专业量表结果相关性≥0.85  
   - 对标案例：情智星球六维指数与经典量表的融合设计

2. **评测完成率**  
   - 目标：用户首次测评完成率≥80%，月度复测率≥40%  
   - 优化策略：游戏化引导（如进度条、成就徽章）  
   - 参考机制：情智星球无感对话式测评设计

---

### **四、扩展性指标**

1. **系统响应时效**  
   - 目标：情绪危机识别到干预建议生成≤3秒

2. **用户留存周期**  
   - 目标：30天留存率≥40%，反映产品粘性

3. **政策、伦理合规**  
   - 目标：隐私政策覆盖率100%，数据脱敏率100%  
   - 参考标准：HIPAA/GDPR合规框架

---

## 3. Design(包括工作量评估)

### 3.1 AI 对话

#### 对话流程



```mermaid
graph LR
    subgraph 用户请求处理
    A[用户请求] --> B[向量化] --> C[问题向量]
    end

    subgraph 文档处理
    Z[本地文档] --> Y[非结构化加载器] --> X[文本数据]
    X --> W[数据切片] --> V[文本块] --> U[向量化] --> T[向量数据库]
    end

    subgraph 答案生成
    C --> D[问题检索]
    T --> D
    D --> H[相关段落context]
    A --> I[prompt模板]
    H --> I --> E[prompt+context] --> F[大模型] --> G[答案]
    end
```

#### 用户历史对话服务

```mermaid
graph TD
	A[用户对话] --> B[检查用户有无历史对话] --> |无|C[根据用户ID+随机ID创建对话记录] --> F[存储对话]
	B[检查用户有无历史对话] --> |有|D[抽取对话ID中的历史对话] --> F[存储对话]
	B[检查用户有无历史对话] --> |有|E[从现有对话框中获取历史对话] --> F[存储对话]
```



### 3.2 社区

#### 核心功能架构

```mermaid
graph TD
    A[内容生产] --> B[智能推荐]
    B --> C[用户互动]
    A --> D[RAG知识库]
    D --> E[Chatbot增强]
    
```

#### 功能实现细节

##### 核心功能模块

| 功能维度     | 核心能力说明                                          | 预计工作量    | 预计交付  |
| ------------ | -------------------------------------------------- |------------ |------------ |
| **内容创作** | 支持富文本+匿名模式编辑，支持富文本展示                  | 4 week | Progress 1 April 7 |
| **社区互动** | 匿名点赞/评论系统                                     | 4 week | Progress 2 May 5 |
| **智能推荐** | 基于用户心理画像的个性化推荐（结合实时情绪状态+长期兴趣标签） | 4 week | Progress 3 June 16 |
| **知识沉淀** | 自动生成结构化案例库，用于增强 Chatbot 对话效果           | 4 week | Progress 4 July 7 |

##### 整体技术实现方案

```mermaid
graph TD
    A[微信小程序] -->|WebSocket| B[API Gateway]
    B --> C[创作服务]
    B --> D[互动服务]
    B --> E[知识库服务]
    C --> F[MySQL]
    D --> G[Redis]
    E --> H[RAG引擎]
```

##### Chatbot集成方案(RAG增强流程)

```mermaid
sequenceDiagram
    participant U as 用户
    participant C as Chatbot
    participant R as RAG引擎
    participant K as 社区知识库

    U->>C: "最近总是失眠焦虑"
    C->>R: 查询相似案例请求
    R->>K: 语义检索[焦虑,失眠]
    K-->>R: 返回TOP3案例 
    R->>R: 生成对话策略
    R-->>C: 建议话术+社区资源
    C->>U: "很多用户通过正念练习改善睡眠，这是社区里分享的方法..."
```

##### 内容搜索和推荐方案

1. **数据存储层**
   - **MongoDB 核心集合设计**：
     ```javascript
     // 用户集合（users）
     {
       _id: ObjectId,
       username: String,
       preferences: { tags: [String], topics: [String] }, // 动态更新的用户兴趣
       behavior_history: [ // 固定长度队列（保留最近100条）
         { action: "search/click/like", content_id: ObjectId, timestamp: Date }
       ]
     }
     
     // 内容集合（contents）
     {
       _id: ObjectId,
       title: String,
       body: String,
       tags: [String],
       embeddings: [Float], // 文本向量（通过AI模型预计算）
       stats: { views: Int, likes: Int },
       created_at: Date
     }
     ```

   - **索引策略**：
     - 内容集合：`tags`（多键索引）、`created_at`（降序复合索引）、`title`（文本索引）
     - 用户行为日志：`content_id` + `timestamp` 复合索引

2. **搜索模块**
   - **中文搜索实现**：
     - 预处理：使用 `jieba` 对内容标题/正文分词，存储为 `tags` 数组字段
     - 查询时：将用户输入同样分词后，通过 `$in` + `$text` 索引联合查询
     - 权重策略：标题匹配权重 > 标签匹配 > 正文匹配

   - **性能优化**：
     - 分页采用 `seek pagination`（基于 `_id` + `created_at` 游标分页，避免skip性能问题）
     - 热词缓存：Redis 存储近期高频搜索词，辅助自动补全

3. **推荐模块**
   
   - **冷启动策略**：
     - 新用户：基于全局热门内容（`stats.likes` 降序）
     - 新内容：基于标签相似性推荐（余弦相似度匹配 `tags` 字段）
   
   - **实时推荐流程**：
     ```python
     # 用户触发行为（如点击内容）后：
     1. 更新用户.behavior_history（维护固定长度队列）
     2. 基于最近10条行为的 content.embeddings 计算平均向量
     3. 在 contents 集合中 ANN 检索相似内容（MongoDB $vectorSearch）
     4. 混合热度权重（0.2*views + 0.3*likes）生成最终推荐列表
     4. 结果缓存至 Redis（用户ID为key，过期时间5分钟）
     ```

4. **AI增强**

- **文本向量化**：
  - 使用 `BERT-base-Chinese` 模型生成内容 `embeddings`（768维）
  - 预计算：内容入库时通过批处理生成向量
  - 更新策略：内容修改后触发向量重算

- **轻量级主题建模**：
  - 对 `tags` 字段进行 TF-IDF 统计，自动合并高频关联标签（如 "机器学习" 和 "AI"）
  - 结果用于用户兴趣画像的 `preferences.topics` 字段

- **深度学习部署**

  - **模型选型**：
    - 双塔召回模型：用户行为序列（通过LSTM编码） + 内容向量 计算相似度
    - 离线训练：TensorFlow，每周全量更新
    - 在线服务：TF Serving + Docker 容器化，响应时间 <50ms


  - **特征工程**：
    
    ```python
    # 用户特征：
    [
      mean(behavior_embeddings), // 行为序列的向量均值
      preferences.topic_weights, // 主题兴趣分布（通过历史行为统计）
      time_decay_factors // 按行为时间衰减加权（最近行为权重更高）
    ]
    
    # 内容特征：
    [
      embeddings, 
      tags_onehot, 
      stats_normalized // 归一化的热度值
    ]
    ```

5. **技术栈**

| 模块     | 核心组件                   |
| -------- | -------------------------- |
| 向量搜索 | MongoDB $vectorSearch      |
| 缓存     | Redis                      |
| 行为队列 | MongoDB Update with $slice |
| NLP模型  | BERT-base-Chinese          |

6. **基础性能要求**

- 90% 搜索请求响应时间 <200ms（含中文分词）
- 支持1000 QPS 并发查询

TODO(@xuhanlin)

#### 运行效果示例

##### 心理历程分享

```markdown
**匿名用户@高考复读**: 
"⬆️ 内耗三个月后终于决定再战了！分享我的心理重建过程：
1️⃣ 每天写『成就日记』对抗自我否定
2️⃣ 参加线下心理支持小组
3️⃣ 阅读《自卑与超越 /》获得力量
👉 想知道大家如何走出失利阴霾？"

```

##### 学习资源分享

```markdown
**认证咨询师@李医生**: 
"【专业资源】最新发布的CBT疗法自助手册包含：
- 自动思维记录表模板
- 行为激活周计划表
- 10分钟正念练习音频
支持导出PDF格式，欢迎取用❤️"

```

##### Chatbot交互案例

```markdown
用户: 觉得最近所有人都讨厌我...
Chatbot: 
"这种被孤立感确实很难受呢（共情），社区里有很多类似经历的朋友：
1️⃣ @匿名用户 通过每日感恩练习改善人际关系认知
2️⃣ @小白 参加社交焦虑训练营的经验分享
需要我为你详细解读这些方法吗？"
```

### 3.3 User Profile Feature

Users can view and edit their personal information in the profile section.

### 3.4 Psychological Assessment Feature

The Psychological Assessment feature is mainly designed to help users understand their mental health status through regular assessments, detailed reports, and trend analysis. By combining questionnaire results and chat history analysis, this feature provides users with valuable insights into their emotional state, stress levels, and key concerns over time. And there is another function to read user's real-time mental state.

#### Key Functions

##### 1. Regular Assessments

- Frequency: Monthly assessments for regular users.
- Data Sources:
  - Questionnaire Results: Users complete a psychological questionnaire.
  - Chat History: Analysis of user chat history with the AI assistant.
- Assessment Report:
  - Emotional Score: A sentiment analysis score derived from chat history.
  - Stress Level: A calculated score based on questionnaire responses.
  - Keyword List: A list of high-frequency keywords extracted from chat history (e.g., ["stress", "anxiety"]).

##### 2. Visualization Report

##### 3. Trend Analysis

Trend Analysis function is to identify patterns and trends in the user's mental health status and provide long-term insights to help users track their progress after continuous assessments.

##### 4. Real-time mental state

Real-time mental state function will employ a sentiment score to reflect the user's current mental state, which is derived from the real-time conversation between the AI Agent and the user, and with this score, the system will be able to offer more appropriate content for the user in the community based on their current needs.  In other words, the real-time mental state function enables the three modules of AI dialog, community, and user assessment to interact and produce a more intelligent AI dialog system.

---

#### Technical Implementation

##### 1. Assessment Data

| **Content**         | **Data Source**          | **Technology**                          |
|----------------------|--------------------------|-----------------------------------------|
| Emotional score      | Chat History             | Sentiment analysis by NLP APIs    |
| Stress level         | Questionnaire Results    | Design a psychological questionnaire and calculate stress levels based on user responses|
| High-frequency keyword List| Chat History| Extract keywords using NLP techniques (e.g., NLP API, TF-IDF, LDA)

###### Example

User ID: 12345 | Assessment Date: 2025-03-01  

- Emotional Score: 0.3 (Negative)  
- Stress Level: 7.5 (High)  
- Keyword List: ["stress", "anxiety", "work pressure"]  

###### 2. Trend Analysis

- Emotional Score Trend: [Line Chart]
- Stress Level Trend: [Line Chart]
- Keyword Cloud: [Word Cloud]

###### 3. Real-time mental state

The user's real-time mental state can be evaluated by performing sentiment analysis using NLP on the user chat conversations within a reasonably short time period and context.  

## 4. Roadmap

TODO(@all)

(WANG Xueyao / Features 3.3 and 3.4)

| **Tasks**         | **Estimated completion time**          | **Estimated number of learning hours**                          |
|----------------------|--------------------------|-----------------------------------------|
| User Profile Feature | Progress 1 April 7 | 2-3 Weeks
| Regular Assessments | Progress 2 May 5 | 4 Weeks
| Visualization Report| Progress 3 June 16 | 2 Weeks
| Trend Analysis | Progress 3 June 16  | 2 Weeks
| Real-time mental state | Progress 4 July 7  | 4-6 Weeks

Item Time  
Short proposal February 5  
Detailed Proposal March 10  
Progress 1 April 7  
Progress 2 May 5  
Interim Report & Presentation June 1  
Progress 3 June 16  
Progress 4 July 7  
Webpage July 15  
Project Report July 18  
Oral Examination end of July  
Revised Project Report August 1  
