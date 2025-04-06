'use client';

import React, { useState } from 'react';
import { 
  Container, 
  PageTitle, 
  PageDescription, 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent, 
  CardFooter,
  Button,
  Separator
} from '@/components/ui/ui-components';

export default function ProposalPage() {
  // 提案数据
  const proposal = {
    title: "毕设项目进度展示网站设计方案",
    lastUpdated: "2025-03-01",
    sections: [
      {
        id: 1,
        title: "项目概述",
        content: `本项目旨在开发一个毕设项目进度展示网站，用于展示团队成员的工作进度、项目整体进度以及项目设计方案。网站将采用现代化的设计和技术栈，提供直观的数据可视化和用户友好的界面，方便团队成员、指导教师和其他相关人员了解项目状态。

网站将包含五个主要页面：项目概览、组员进度、项目进度、项目设计和关于页面。同时，网站将提供后台管理功能，允许团队成员更新自己的工作进度和项目信息。`
      },
      {
        id: 2,
        title: "需求分析",
        content: `根据用户需求，网站需要满足以下功能要求：

1. **展示功能**：
   - 展示项目整体进度和关键指标
   - 展示团队成员的工作进度和任务完成情况
   - 展示项目里程碑和时间线
   - 展示项目设计方案和相关文档

2. **管理功能**：
   - 用户认证和授权
   - 后台管理界面
   - 数据更新和维护
   - 文件上传和管理

3. **用户体验**：
   - 简洁明了的界面设计
   - 直观的数据可视化
   - 响应式布局，适配不同设备
   - 良好的交互体验`
      },
      {
        id: 3,
        title: "技术架构",
        content: `本项目采用以下技术栈进行开发：

1. **前端技术**：
   - Next.js 15.1.4：React框架，提供服务端渲染和静态生成功能
   - Tailwind CSS：实用优先的CSS框架，用于快速构建自定义界面
   - TypeScript：静态类型检查，提高代码质量和开发效率
   - React Hooks：状态管理和组件逻辑复用

2. **后端技术**：
   - Next.js API Routes：提供后端API功能
   - JWT认证：实现用户认证和授权
   - Cloudflare D1：SQLite兼容的数据库，用于数据存储

3. **部署环境**：
   - Node.js生产服务器
   - Cloudflare Pages：静态资源托管和CDN加速`
      },
      {
        id: 4,
        title: "数据库设计",
        content: `数据库采用关系型数据库设计，主要包含以下表结构：

1. **用户表 (Users)**：存储用户信息和认证数据
   - id：用户唯一标识
   - username：用户名
   - password_hash：密码哈希
   - name：真实姓名
   - role：用户角色
   - email：电子邮箱
   - avatar：头像URL

2. **项目表 (Projects)**：存储项目基本信息
   - id：项目唯一标识
   - name：项目名称
   - description：项目描述
   - start_date：开始日期
   - end_date：结束日期
   - progress：项目进度

3. **里程碑表 (Milestones)**：存储项目里程碑信息
   - id：里程碑唯一标识
   - project_id：关联的项目ID
   - title：里程碑标题
   - description：里程碑描述
   - due_date：截止日期
   - status：状态
   - progress：完成进度

4. **任务表 (Tasks)**：存储用户任务信息
   - id：任务唯一标识
   - title：任务标题
   - description：任务描述
   - status：任务状态
   - start_date：开始日期
   - due_date：截止日期
   - completed_date：完成日期
   - progress：完成进度
   - priority：优先级
   - user_id：关联的用户ID
   - milestone_id：关联的里程碑ID

5. **Proposal表和章节表**：存储项目设计方案
   - Proposals：提案基本信息
   - ProposalSections：提案章节内容
   - Documents：相关文档和附件`
      },
      {
        id: 5,
        title: "界面设计",
        content: `网站界面采用苹果风格设计，具有以下特点：

1. **设计风格**：
   - 简洁明了：减少视觉干扰，突出重要信息
   - 明亮优雅：采用明亮的配色方案和优雅的排版
   - 一致性：保持各页面设计风格的一致性
   - 细节关注：注重细节处理，如动画过渡、交互反馈等

2. **配色方案**：
   - 主色调：#007AFF（蓝色）
   - 辅助色：#34C759（绿色）、#FF9500（橙色）、#FF3B30（红色）
   - 中性色：黑色、灰色、浅灰、近白色

3. **组件设计**：
   - 卡片式布局：使用圆角矩形卡片组织内容
   - 清晰层次：通过阴影和间距创建视觉层次
   - 直观控件：按钮、输入框等控件设计简洁直观
   - 响应式设计：适配不同屏幕尺寸的设备`
      },
      {
        id: 6,
        title: "功能模块",
        content: `网站主要包含以下功能模块：

1. **用户认证模块**：
   - 登录和注册功能
   - 密码重置功能
   - 会话管理

2. **项目概览模块**：
   - 项目总体进度展示
   - 团队成员进度概览
   - 最近里程碑展示
   - 快速导航链接

3. **组员进度模块**：
   - 团队成员详细信息
   - 任务列表和进度
   - 工作时间统计
   - 团队整体进度对比

4. **项目进度模块**：
   - 项目时间线
   - 里程碑详情
   - 进度对比分析
   - 时间统计

5. **项目设计模块**：
   - 设计方案展示
   - 章节导航
   - 文档下载

6. **后台管理模块**：
   - 用户管理
   - 项目和任务管理
   - 里程碑管理
   - Proposal管理`
      },
      {
        id: 7,
        title: "实施计划",
        content: `项目实施计划分为以下几个阶段：

1. **分析阶段**（1周）：
   - 需求分析和整理
   - 技术选型
   - 架构设计

2. **设计阶段**（1周）：
   - 数据库设计
   - 界面设计
   - API设计

3. **开发阶段**（4周）：
   - 数据库实现
   - 后端API开发
   - 前端界面开发
   - 功能集成

4. **测试阶段**（1周）：
   - 功能测试
   - 性能测试
   - 用户体验测试
   - 问题修复

5. **部署阶段**（1周）：
   - 环境配置
   - 系统部署
   - 文档编写
   - 用户培训`
      },
      {
        id: 8,
        title: "总结与展望",
        content: `本项目旨在开发一个功能完善、界面友好的毕设项目进度展示网站，帮助团队更好地管理和展示项目进度。通过采用现代化的技术栈和设计理念，我们期望打造一个高质量的网站产品。

未来的发展方向可能包括：

1. **功能扩展**：
   - 添加更多数据分析和可视化功能
   - 集成通知和提醒系统
   - 添加团队协作工具

2. **技术优化**：
   - 性能优化
   - 安全性增强
   - 移动应用开发

3. **用户体验提升**：
   - 个性化定制
   - 多语言支持
   - 无障碍功能

我们相信，通过团队的共同努力，这个项目将成为一个成功的毕业设计作品，并为未来类似项目提供有价值的参考。`
      }
    ],
    documents: [
      { id: 1, title: "需求规格说明书", type: "pdf", url: "/documents/requirements.pdf" },
      { id: 2, title: "系统设计文档", type: "pdf", url: "/documents/design.pdf" },
      { id: 3, title: "数据库设计文档", type: "pdf", url: "/documents/database.pdf" },
      { id: 4, title: "UI设计稿", type: "zip", url: "/documents/ui-design.zip" }
    ]
  };

  // 当前选中的章节
  const [selectedSection, setSelectedSection] = useState(proposal.sections[0]);

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <Container>
        {/* 页面标题 */}
        <div className="mb-12">
          <PageTitle className="mb-3">{proposal.title}</PageTitle>
          <PageDescription>最后更新于: {new Date(proposal.lastUpdated).toLocaleDateString('zh-CN')}</PageDescription>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* 目录侧边栏 */}
          <div className="lg:col-span-1">
            <Card className="sticky top-6">
              <CardHeader>
                <CardTitle>目录</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <nav>
                  <ul className="divide-y divide-gray-200">
                    {proposal.sections.map((section) => (
                      <li key={section.id}>
                        <button
                          onClick={() => setSelectedSection(section)}
                          className={`w-full text-left px-6 py-3 text-sm ${
                            selectedSection.id === section.id
                              ? "bg-blue-50 text-blue-600 font-medium"
                              : "text-gray-700 hover:bg-gray-50"
                          }`}
                        >
                          {section.id}. {section.title}
                        </button>
                      </li>
                    ))}
                  </ul>
                </nav>
              </CardContent>
            </Card>
          </div>

          {/* 内容区域 */}
          <div className="lg:col-span-3">
            {/* 章节内容 */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="text-2xl">
                  {selectedSection.id}. {selectedSection.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose max-w-none">
                  {selectedSection.content.split('\n\n').map((paragraph, idx) => (
                    <div key={idx} className="mb-4">
                      {paragraph.includes('**') ? (
                        <div>
                          {paragraph.split('\n').map((line, lineIdx) => {
                            if (line.startsWith('- ')) {
                              return <li key={lineIdx} className="ml-4 mb-1">{line.substring(2)}</li>;
                            } else if (line.startsWith('1. ') || line.startsWith('2. ') || line.startsWith('3. ') || line.startsWith('4. ') || line.startsWith('5. ')) {
                              return <li key={lineIdx} className="ml-4 mb-1">{line.substring(3)}</li>;
                            } else {
                              return (
                                <p key={lineIdx} className="mb-2">
                                  {line.split('**').map((part, partIdx) => {
                                    return partIdx % 2 === 0 ? part : <strong key={partIdx}>{part}</strong>;
                                  })}
                                </p>
                              );
                            }
                          })}
                        </div>
                      ) : (
                        <p>{paragraph}</p>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button
                  variant="outline"
                  disabled={selectedSection.id === 1}
                  onClick={() => {
                    const prevIndex = proposal.sections.findIndex(s => s.id === selectedSection.id) - 1;
                    if (prevIndex >= 0) {
                      setSelectedSection(proposal.sections[prevIndex]);
                    }
                  }}
                >
                  &larr; 上一章节
                </Button>
                <Button
                  variant="outline"
                  disabled={selectedSection.id === proposal.sections.length}
                  onClick={() => {
                    const nextIndex = proposal.sections.findIndex(s => s.id === selectedSection.id) + 1;
                    if (nextIndex < proposal.sections.length) {
                      setSelectedSection(proposal.sections[nextIndex]);
                    }
                  }}
                >
                  下一章节 &rarr;
                </Button>
              </CardFooter>
            </Card>

            {/* 相关文档 */}
            <Card>
              <CardHeader>
                <CardTitle>相关文档</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {proposal.documents.map((doc) => (
                    <a
                      key={doc.id}
                      href={doc.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mr-4">
                        {doc.type === 'pdf' ? 'PDF' : doc.type === 'zip' ? 'ZIP' : 'DOC'}
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900">{doc.title}</h3>
                        <p className="text-sm text-gray-500">{doc.type.toUpperCase()} 文件</p>
                      </div>
                    </a>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </Container>
    </main>
  );
}
