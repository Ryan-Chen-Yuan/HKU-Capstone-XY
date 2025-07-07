# Progress 4 进展报告

## 一、概述

Progress 4 阶段(6月17日 - 7月7日)团队协作完成了以下工作：

1. 基于agent开发框架langgraph重构代码：在保持「perception」->「planing」->「action」工作流的功能和接口不变的同时，
   使项目组织和逻辑更清晰，日志和开关配置更完善，并新增长期记忆、联网检索、自动报警能力。
2. 小程序功能完善和UI优化：完成全部用于最终报告的feature，包括「事件提取」和「情绪识别」的确认和长期存储机制。

## 二、详细进展

### 「langgraph」重构 - 于易涛

- 使用langgraph对项目全流程进行重构
<img width="718" alt="image" src="https://github.com/user-attachments/assets/11e6c6bd-9614-4c40-b8d2-6ddfc605d1f1" />

- 使用nlp模型对用户情绪进行精确判断
<img width="718" alt="image" src="https://github.com/user-attachments/assets/11e6c6bd-9614-4c40-b8d2-6ddfc605d1f1" />

- 引入联网检索和危机干预功能
<img width="315" alt="image" src="https://github.com/user-attachments/assets/137d005d-bff7-45c7-83c1-855d165a81cc" />
<img width="306" alt="image" src="https://github.com/user-attachments/assets/e0e058ac-2a8c-4510-9c3b-e9fabe75ff89" />

### 「情绪感知」模块更新 - 王雪瑶

- 实现了用户反馈机制，允许用户对系统生成的情绪分析结果进行反馈。用户可对分析结果选择“采纳”或“不采纳”。所有被采纳的情绪分析结果会被持久化保存至数据库，作为未来模型和功能优化的依据。

*采纳*
<img width="286" alt="c16e4e92b323ed332addedd725d0ba2" src="https://github.com/user-attachments/assets/a3345db1-5362-4510-8906-e609df32f5c7" />
*拒绝*
<img width="292" alt="e07a773b124229a9d791b9226727f17" src="https://github.com/user-attachments/assets/789dfe5a-6745-477f-ad9f-ae315f48736f" />
*编辑*
<img width="291" alt="123152394ed3a0cd2d48e1207044c89" src="https://github.com/user-attachments/assets/013fe376-3379-40bd-94ae-4e51738fbd9a" />
<img width="295" alt="96c24c688344da4b4eb6504278c7c4d" src="https://github.com/user-attachments/assets/99f4d334-5e19-4eb7-942e-66e83dd71d24" />

### 事件提取功能链路搭建，新增事件服务，优化事件管理逻辑 - 粟英成

- 实现每三轮对话后台异步触发一次事件提取，将提取后的json格式的事件体存入数据库，并支持前端对事件进行查看，确认，编辑，删除。

用户进行三轮对话后会自动触发事件提取
![image](https://github.com/user-attachments/assets/daa25bdd-ee61-4714-b1fb-24f81539cc14)
![image](https://github.com/user-attachments/assets/ab86d664-6f4f-4c1d-84e2-170671dbdfc8)

当用户输入的对话轮数不满三轮或者清空了所有事件，界面会展示无数据提示
![image](https://github.com/user-attachments/assets/f3fcea8d-e083-408e-a9a2-f0f5b11110e2)

### 对话报告生成 - 徐翰林

- 在对话中，用户可以通过发送特定命令来触发智能分析报告生成。系统将基于用户的对话历史、事件记录、情绪数据等信息，自动生成个性化的心理健康分析报告。

报告示例
<img width="314" alt="image" src="https://github.com/user-attachments/assets/c44d951c-e68d-426d-b953-32aa77b7bfd9" />

### Code Review和功能验证 - 陈源

检查上述功能实现效果，Code Review和冲突解决。

## 三、后续计划

**时间**：

7.15 Webpage 展示
7.18 Project Report
7.24 Oral Examination
