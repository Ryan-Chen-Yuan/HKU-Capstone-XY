# Detailed Proposal Draft

---

## Background

### 心理咨询市场

- **供需失衡**：中国心理咨询师缺口大，单次咨询费用普遍在500-1000元区间，形成高门槛服务。
- **地域限制**：专业资源集中在一线城市集中，二三线城市用户获取服务困难。
- **认知滞后**：潜在需求者因"病耻感"回避线下咨询。

### 竞品报告

- **情智星球**：<https://www.sohu.com/a/830612921_122042791>
- **AI心语**：<https://news.qq.com/rain/a/20241106A09XWS00>

### AI's scope

#### Pros

1. **颠覆性的成本结构**：以DeepSeek模型价格为例，每百万Token仅需几块钱，远低于人类心理咨询师价格。且不受地点、时间安排等限制。
2. **实时情绪响应**：7x24在线提供情感支持和安慰，帮助青少年表达和理解自己的情绪。
3. **信息和资源提供**：提供关于心理健康、应对策略等方面的信息。

#### Cons

1. **深层次的情感问题**：如创伤处理、深层次的自我认同问题等，需要专业心理咨询师的介入。
2. **紧急情况**：如自杀倾向、严重的心理危机等，需要即时的专业干预。
3. **法律和医学问题**：如家庭暴力、严重精神疾病等，需要专业的法律和医学介入。

## Scope

### 不做模型优化

专注于用LLM的能力提供心理咨询服务，而不是训练用于心理咨询的大模型。

### 不做TTS(Text to Speech)

文字与语音的转化是一个专业性很强的领域，本项目提供基于文本的回复。

### 做心理对话 Chatbot

根据来访者的需求提供倾听和咨询服务。

### 做心理内容社区

由用户发帖驱动的日常生活、心理学习资源、咨询经历分享。

### 做心理评测工具

自动检测实时情绪水平，主动评测心理量表。

### 隐私政策合规

参考HIPAA/GDPR合规框架标准，实现所有场景的隐私政策覆盖和数据脱敏。  

---

## Design(包括工作量评估)

### AI 对话

TODO(@yuyitao)

### 社区

#### 内容分享和互动

TODO(@chenyuan)
TODO(@suyingcheng)

#### 内容搜索和推荐

TODO(@xuhanlin)

### (个人信息与评测@wangxueyao)

### User Profile Feature

#### Overview
Users can view and edit their personal information in the profile section.

### Psychological Assessment Feature

#### Overview

The Psychological Assessment feature is designed to help users understand their mental health status through regular assessments, detailed reports, and trend analysis. By combining questionnaire results and chat history analysis, this feature provides users with valuable insights into their emotional state, stress levels, and key concerns over time.

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
- Identify patterns and trends in the user's mental health status and provide long-term insights to help users track their progress after continuous assessments.
---

#### Technical Implementation

###### Assessment Data
| **Content**         | **Data Source**          | **Technology**                          |
|----------------------|--------------------------|-----------------------------------------|
| Emotional score      | Chat History             | Sentiment analysis by NLP APIs    |
| Stress level         | Questionnaire Results    | Design a psychological questionnaire and calculate stress levels based on user responses|
| High-frequency keyword List| Chat History| Extract keywords using NLP techniques (e.g., NLP API, TF-IDF, LDA).
 |


##### Example

###### User ID: 12345 | Assessment Date: 2025-03-01

###### Emotional Score: 0.3 (Negative)
###### Stress Level: 7.5 (High)
###### Keyword List: ["stress", "anxiety", "work pressure"]


###### Trend Analysis
- Emotional Score Trend: [Line Chart]
- Stress Level Trend: [Line Chart]
- Keyword Cloud: [Word Cloud]


## Roadmap

TODO(@all)

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
