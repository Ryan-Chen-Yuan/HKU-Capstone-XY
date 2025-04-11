'use client';

import React from 'react';
import { 
  Container, 
  PageTitle, 
  PageDescription, 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent, 
  CardFooter,
  Separator
} from '@/components/ui/ui-components';

export default function AboutPage() {
  // 团队成员数据
  const teamMembers = [
    { 
      id: 1, 
      name: '张三', 
      role: '前端开发', 
      avatar: '/avatars/member1.png',
      email: 'zhangsan@example.com',
      description: '负责网站前端开发和UI实现，擅长React和Next.js框架，对用户体验和交互设计有深入研究。'
    },
    { 
      id: 2, 
      name: '李四', 
      role: '后端开发', 
      avatar: '/avatars/member2.png',
      email: 'lisi@example.com',
      description: '负责网站后端API和数据库设计，擅长Node.js和数据库优化，有丰富的系统架构经验。'
    },
    { 
      id: 3, 
      name: '王五', 
      role: 'UI设计', 
      avatar: '/avatars/member3.png',
      email: 'wangwu@example.com',
      description: '负责网站UI设计和视觉效果，擅长用户界面设计和交互原型制作，注重细节和用户体验。'
    },
    { 
      id: 4, 
      name: '赵六', 
      role: '数据分析', 
      avatar: '/avatars/member4.png',
      email: 'zhaoliu@example.com',
      description: '负责需求分析和数据模型设计，擅长数据分析和可视化，对业务需求有深刻理解。'
    },
    { 
      id: 5, 
      name: '钱七', 
      role: '项目经理', 
      avatar: '/avatars/member5.png',
      email: 'qianqi@example.com',
      description: '负责项目整体规划和团队协调，擅长项目管理和风险控制，确保项目按时高质量完成。'
    }
  ];

  // 技术栈数据
  const techStack = [
    {
      category: '前端技术',
      items: [
        { name: 'Next.js 15.1.4', description: 'React框架，提供服务端渲染和静态生成功能' },
        { name: 'Tailwind CSS', description: '实用优先的CSS框架，用于快速构建自定义界面' },
        { name: 'TypeScript', description: '静态类型检查，提高代码质量和开发效率' },
        { name: 'React Hooks', description: '状态管理和组件逻辑复用' }
      ]
    },
    {
      category: '后端技术',
      items: [
        { name: 'Next.js API Routes', description: '提供后端API功能' },
        { name: 'JWT认证', description: '实现用户认证和授权' },
        { name: 'Cloudflare D1', description: 'SQLite兼容的数据库，用于数据存储' }
      ]
    },
    {
      category: '部署环境',
      items: [
        { name: 'Node.js', description: '生产服务器环境' },
        { name: 'Cloudflare Pages', description: '静态资源托管和CDN加速' }
      ]
    },
    {
      category: '开发工具',
      items: [
        { name: 'VS Code', description: '代码编辑器' },
        { name: 'Git', description: '版本控制系统' },
        { name: 'npm', description: '包管理工具' },
        { name: 'ESLint', description: '代码质量检查工具' }
      ]
    }
  ];

  // 项目信息
  const projectInfo = {
    name: '毕设项目进度展示网站',
    description: '本项目是一个用于展示毕业设计项目进度的网站，包括团队成员的工作进度、项目整体进度以及项目设计方案。网站采用现代化的设计和技术栈，提供直观的数据可视化和用户友好的界面，方便团队成员、指导教师和其他相关人员了解项目状态。',
    startDate: '2025-01-15',
    endDate: '2025-04-30',
    supervisor: '张教授',
    department: '计算机科学与技术学院',
    university: '示例大学'
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <Container>
        {/* 页面标题 */}
        <div className="mb-12">
          <PageTitle className="mb-3">关于项目</PageTitle>
          <PageDescription>了解项目背景、团队成员和技术栈</PageDescription>
        </div>

        {/* 项目介绍 */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">项目介绍</h2>
          <Card>
            <CardHeader>
              <CardTitle>{projectInfo.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 mb-6">{projectInfo.description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">项目信息</h3>
                  <dl className="space-y-2">
                    <div className="flex justify-between">
                      <dt className="text-gray-500">开始日期</dt>
                      <dd className="font-medium">{new Date(projectInfo.startDate).toLocaleDateString('zh-CN')}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-500">结束日期</dt>
                      <dd className="font-medium">{new Date(projectInfo.endDate).toLocaleDateString('zh-CN')}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-500">项目周期</dt>
                      <dd className="font-medium">
                        {Math.round((new Date(projectInfo.endDate) - new Date(projectInfo.startDate)) / (1000 * 60 * 60 * 24))} 天
                      </dd>
                    </div>
                  </dl>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">学术信息</h3>
                  <dl className="space-y-2">
                    <div className="flex justify-between">
                      <dt className="text-gray-500">指导教师</dt>
                      <dd className="font-medium">{projectInfo.supervisor}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-500">所属院系</dt>
                      <dd className="font-medium">{projectInfo.department}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-500">学校</dt>
                      <dd className="font-medium">{projectInfo.university}</dd>
                    </div>
                  </dl>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 团队成员 */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">团队成员</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {teamMembers.map((member) => (
              <Card key={member.id}>
                <CardHeader className="flex flex-col items-center text-center">
                  <div className="h-24 w-24 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-semibold text-3xl mb-4">
                    {member.name.charAt(0)}
                  </div>
                  <div>
                    <CardTitle>{member.name}</CardTitle>
                    <p className="text-gray-500">{member.role}</p>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 mb-4">{member.description}</p>
                  <p className="text-sm text-gray-500">
                    联系方式: <a href={`mailto:${member.email}`} className="text-blue-600 hover:underline">{member.email}</a>
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* 技术栈 */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">技术栈</h2>
          <div className="space-y-8">
            {techStack.map((category, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle>{category.category}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {category.items.map((item, itemIndex) => (
                      <div key={itemIndex} className="flex flex-col md:flex-row md:items-center">
                        <div className="font-medium text-gray-900 md:w-1/4">{item.name}</div>
                        <div className="text-gray-700 md:w-3/4">{item.description}</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* 页脚 */}
        <div className="mt-16 text-center text-gray-500 text-sm">
          <p>© 2025 毕设项目进度展示网站 - 版权所有</p>
          <p className="mt-1">本网站仅用于学术展示，非商业用途</p>
        </div>
      </Container>
    </main>
  );
}
