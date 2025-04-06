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
      name: 'CHEN Yuan', 
      role: 'Leader', 
      avatar: '/avatars/member1.png',
      email: 'zhangsan@example.com',
      description: (
        <>
          <ul className="list-disc pl-5">
            <li>Develop Medal Feedback feature</li>
            <li>Overall project management</li>
          </ul>
        </>
      )
    },
    { 
      id: 2, 
      name: 'Xu Hanlin', 
      role: 'Member', 
      avatar: '/avatars/member2.png',
      email: 'lisi@example.com',
      description: (
        <>
          <ul className="list-disc pl-5">
            <li>Develop Response Suggestions/Tips feature</li>
            <li>Develop AI Conversation feature</li>
          </ul>
        </>
      )
    },
    { 
      id: 3, 
      name: 'WANG Xueyao', 
      role: 'Member', 
      avatar: '/avatars/member3.png',
      email: 'wangwu@example.com',
      description: (
        <>
          <ul className="list-disc pl-5">
            <li>Develop Mood Score feature</li>
            <li>Develop Project Webpage</li>
          </ul>
        </>
      )
    },
    { 
      id: 4, 
      name: 'YU Yitao', 
      role: 'Member', 
      avatar: '/avatars/member4.png',
      email: 'zhaoliu@example.com',
      description: (
        <>
          <ul className="list-disc pl-5">
            <li>Develop AI Conversation feature</li>
          </ul>
        </>
      )
    },
    { 
      id: 5, 
      name: 'SU Yingcheng', 
      role: 'Member', 
      avatar: '/avatars/member5.png',
      email: 'qianqi@example.com',
      description: (
        <>
          <ul className="list-disc pl-5">
            <li>Develop Event Analysis feature</li>
          </ul>
        </>
      )
    }
  ];

  // 技术栈数据
  const techStack = [
    {
      category: 'Platforms & Frameworks',
      items: [
        { name: 'Wechat Mini Program', description: 'a simple and efficient application development framework and rich components and APIs to help developers develop native applications in WeChat' },
        // { name: 'Tailwind CSS', description: '实用优先的CSS框架，用于快速构建自定义界面' },
        // { name: 'TypeScript', description: '静态类型检查，提高代码质量和开发效率' },
        // { name: 'React Hooks', description: '状态管理和组件逻辑复用' }
      ]
    },
    // {
    //   category: 'Backend & Database',
    //   items: [
    //     // { name: 'Next.js API Routes', description: '提供后端API功能' },
    //     // { name: 'JWT认证', description: '实现用户认证和授权' },
    //     // { name: 'Cloudflare D1', description: 'SQLite兼容的数据库，用于数据存储' }
    //   ]
    // },
    // {
    //   category: 'Deployment & Hosting',
    //   items: [
    //     // { name: 'Node.js', description: '生产服务器环境' },
    //     // { name: 'Cloudflare Pages', description: '静态资源托管和CDN加速' }
    //   ]
    // },
  ];

  // 项目信息
  const projectInfo = {
    name: 'COMP7705 Project Webpage',
    description: 'We are developing an intelligent psychological support platform that integrates a psychological dialogue Chatbot, psychological content community and psychological assessment tools. This platform leverages AI technology and mobile applications to provide users with personalized health services, covering the entire process from emotional assessment to interactive community engagement. The platform is not designed to replace human psychological therapists with AI but to empower individuals with a deeper understanding of themselves and seamlessly connect them to the resources and support they need through the internet.',
    startDate: '2025',
    endDate: '2025-04-30',
    supervisor: 'Prof. Lingpeng Kong',
    department: '计算机科学与技术学院',
    university: 'HKU'
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <Container>
        {/* 项目介绍 */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Project Information</h2>
          <Card>
            {/* <CardHeader>
              <CardTitle>{projectInfo.name}</CardTitle>
            </CardHeader> */}
            <CardContent>
            <dl className="space-y-4">
              <p></p>
              <p className="text-gray-700 mb-6">{projectInfo.description}</p>
            
            </dl>
            <p className="text-gray-700"><strong>Core Features</strong></p>
              <p className="text-gray-700">1. AI-Powered Chatbot: Provides real-time psychological support and guidance.</p>
              <p className="text-gray-700">2. Community Engagement: Users can share experiences and seek advice from peers.</p>
              <p className="text-gray-700">3. Assessment Tools: Offers various psychological assessments to help users understand their mental health status.</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* <div>
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
                </div> */}
                
                <div>
                  {/* <h3 className="text-sm font-medium text-gray-500 mb-2">学术信息</h3> */}
                  <dl className="space-y-6">
                    <p></p>
                    <div className="flex justify-between">
                      <dt className="text-gray-500 ">Project Mentor</dt>
                      <dd className="font-medium">{projectInfo.supervisor}</dd>
                    </div>
                    {/* <div className="flex justify-between">
                      <dt className="text-gray-500">所属院系</dt>
                      <dd className="font-medium">{projectInfo.department}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-500">学校</dt>
                      <dd className="font-medium">{projectInfo.university}</dd>
                    </div> */}
                  </dl>
                </div>
              </div>
              
            </CardContent>
          </Card>
        </div>

        {/* 团队成员 */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">The Team</h2>
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
                  {/* <p className="text-sm text-gray-500">
                    联系方式: <a href={`mailto:${member.email}`} className="text-blue-600 hover:underline">{member.email}</a>
                  </p> */}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* 技术栈 */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Technology Stacks</h2>
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
        {/* <div className="mt-16 text-center text-gray-500 text-sm">
          <p>© 2025 Copyright Reserved</p>
          <p className="mt-1">本网站仅用于学术展示，非商业用途</p>
        </div> */}
      </Container>
    </main>
  );
}
