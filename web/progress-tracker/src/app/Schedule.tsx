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
  Progress,
  Badge,
  Separator
} from '@/components/ui/ui-components';
import getStatusBadge, { formatDate } from './global';

export default function Schedule() {
  // 项目基本信息
  const projectInfo = {
    name: "毕设项目进度展示网站",
    startDate: "2025-02-20",
    endDate: "2025-07-07",
    daysTotal: 105,
    daysElapsed: 30,
    progress: 25
  };

  // 里程碑数据
  const milestones = [
    { 
      id: 1, 
      title: 'Business need analysis', 
      description: 'Define project scope and objectives',
      startDate: '2025-02-20', 
      endDate: '2025-03-15', 
      status: 'completed', 
      progress: 100 
    },
    { 
      id: 2, 
      title: 'Prototype design', 
      description: 'Complete UI design and define technical architecture',
      startDate: '2025-03-01', 
      endDate: '2025-03-20', 
      status: 'completed', 
      progress: 100 
    },
    { 
      id: 3, 
      title: 'Development phase', 
      description: 'Implement frontend and backend core features',
      startDate: '2025-03-10', 
      endDate: '2025-03-30', 
      status: 'in_progress', 
      progress: 50 
    },
    { 
      id: 4, 
      title: 'Testing phase', 
      description: 'Perform functional testing, performance testing and user testing to fix issues',
      startDate: '2025-06-01', 
      endDate: '2025-06-30', 
      status: 'pending', 
      progress: 0 
    },
    { 
      id: 5, 
      title: 'Deployment', 
      description: 'Deploy the system to a production environment',
      startDate: '2025-06-20', 
      endDate: '2025-07-20', 
      status: 'pending', 
      progress: 0 
    }
  ];

  // 计算时间进度
  const calculateTimeProgress = () => {
    const today = new Date();
    const start = new Date(projectInfo.startDate);
    const end = new Date(projectInfo.endDate);
    const totalDays = (end - start) / (1000 * 60 * 60 * 24);
    const elapsedDays = (today - start) / (1000 * 60 * 60 * 24);
    return Math.min(Math.round((elapsedDays / totalDays) * 100), 100);
  };

  // 计算两个日期之间的天数
  const getDaysBetween = (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    return Math.round((end - start) / (1000 * 60 * 60 * 24));
  };

  // 计算里程碑的时间线位置
  const calculateSchedulePosition = (startDate, endDate) => {
    const projectStart = new Date(projectInfo.startDate);
    const projectEnd = new Date(projectInfo.endDate);
    const milestoneStart = new Date(startDate);
    const milestoneEnd = new Date(endDate);
    
    const totalDuration = projectEnd - projectStart;
    const startPosition = ((milestoneStart - projectStart) / totalDuration) * 100;
    const endPosition = ((milestoneEnd - projectStart) / totalDuration) * 100;
    
    return {
      left: `${startPosition}%`,
      width: `${endPosition - startPosition}%`
    };
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <Container>
        {/* 页面标题 */}
        {/* <div className="mb-12">
          <PageTitle className="mb-3">项目进度</PageTitle>
          <PageDescription>跟踪项目整体进度和里程碑完成情况</PageDescription>
        </div> */}

        {/* 项目概览 */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Project Overview</h2>
          <Card>
            <CardHeader>
              {/* <CardTitle>{projectInfo.name}</CardTitle> */}
              <p className="text-gray-500">
              Project period: {formatDate(projectInfo.startDate)} - {formatDate(projectInfo.endDate)}
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Timeline</h3>
                  <div className="flex justify-between text-sm mb-1">
                    {/* <span>Days Elapsed</span> */}
                    <span>{calculateTimeProgress()}%</span>
                  </div>
                  <Progress value={calculateTimeProgress()} className="mb-2" />
                  <p className="text-sm text-gray-500">
                    past {projectInfo.daysElapsed} days / total {projectInfo.daysTotal} days
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Progress</h3>
                  <div className="flex justify-between text-sm mb-1">
                    {/* <span>Completion</span> */}
                    <span>{projectInfo.progress}%</span>
                  </div>
                  <Progress value={projectInfo.progress} className="mb-2" />
                  <p className="text-sm text-gray-500">
                    completed {milestones.filter(m => m.status === 'completed').length} milestones / total {milestones.length} milestones
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Evaluation</h3>
                  <div className="relative h-8 bg-gray-100 rounded-md overflow-hidden">
                    <div 
                      className="absolute top-0 left-0 h-full bg-blue-600" 
                      style={{ width: `${calculateTimeProgress()}%` }}
                    >
                      <span className="absolute inset-0 flex items-center justify-center text-xs text-white font-medium">
                        timeline {calculateTimeProgress()}%
                      </span>
                    </div>
                    <div 
                      className="absolute top-0 left-0 h-full bg-green-600 border-r-2 border-white" 
                      style={{ width: `${projectInfo.progress}%` }}
                    >
                      <span className="absolute inset-0 flex items-center justify-center text-xs text-white font-medium">
                        {projectInfo.progress}%
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-500 mt-2">
                    {projectInfo.progress > calculateTimeProgress() ? 'ahead schedule' : 'behind schedule'}:
                    {Math.abs(projectInfo.progress - calculateTimeProgress())}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Project Timeline */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Project Timeline</h2>
          <Card>
            <CardContent className="pt-6">
              <div className="relative">
                {/* 时间线轴 */}
                <div className="absolute top-8 left-0 right-0 h-1 bg-gray-200"></div>
                
                {/* 今天的标记 */}
                <div 
                  className="absolute top-4 h-9 w-0.5 bg-red-500" 
                  style={{ left: `${calculateTimeProgress()}%` }}
                >
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-red-500 text-white text-xs px-2 py-1 rounded">
                    today
                  </div>
                </div>
                
                {/* 里程碑标记 */}
                <div className="relative h-16">
                  {milestones.map((milestone) => {
                    const position = calculateSchedulePosition(milestone.startDate, milestone.endDate);
                    return (
                      <div 
                        key={milestone.id}
                        className={`absolute top-6 h-3 rounded-full ${
                          milestone.status === 'completed' ? 'bg-green-500' : 
                          milestone.status === 'in_progress' ? 'bg-blue-500' : 
                          'bg-gray-300'
                        }`}
                        style={{ left: position.left, width: position.width }}
                        title={milestone.title}
                      ></div>
                    );
                  })}
                </div>
                
                {/* 起始和结束日期标记 */}
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span>{formatDate(projectInfo.startDate)}</span>
                  <span>{formatDate(projectInfo.endDate)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Milestone Detail */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Milestone Details</h2>
          <div className="space-y-6">
            {milestones.map((milestone) => (
              <Card key={milestone.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle>{milestone.title}</CardTitle>
                      <p className="text-gray-500">{milestone.description}</p>
                    </div>
                    <div>
                      {getStatusBadge(milestone.status)}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Time period</p>
                      <p className="font-medium">
                        {formatDate(milestone.startDate)} - {formatDate(milestone.endDate)}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        last {getDaysBetween(milestone.startDate, milestone.endDate)} days
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Progress</p>
                      <div className="flex justify-between text-sm mb-1">
                        {/* <span>progress</span> */}
                        <span>{milestone.progress}%</span>
                      </div>
                      <Progress value={milestone.progress} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </Container>
    </main>
  );
}
