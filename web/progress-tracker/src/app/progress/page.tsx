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

export default function ProgressPage() {
  // 项目基本信息
  const projectInfo = {
    name: "毕设项目进度展示网站",
    startDate: "2025-01-15",
    endDate: "2025-04-30",
    daysTotal: 105,
    daysElapsed: 55,
    progress: 75
  };

  // 里程碑数据
  const milestones = [
    { 
      id: 1, 
      title: '需求分析', 
      description: '收集和分析用户需求，确定项目范围和目标',
      startDate: '2025-01-15', 
      endDate: '2025-01-25', 
      status: 'completed', 
      progress: 100 
    },
    { 
      id: 2, 
      title: '设计阶段', 
      description: '完成UI设计和数据库设计，确定技术架构',
      startDate: '2025-01-26', 
      endDate: '2025-02-15', 
      status: 'completed', 
      progress: 100 
    },
    { 
      id: 3, 
      title: '开发阶段', 
      description: '实现前后端功能，包括用户认证、数据管理和界面展示',
      startDate: '2025-02-16', 
      endDate: '2025-03-25', 
      status: 'in_progress', 
      progress: 70 
    },
    { 
      id: 4, 
      title: '测试阶段', 
      description: '进行功能测试、性能测试和用户测试，修复问题',
      startDate: '2025-03-26', 
      endDate: '2025-04-15', 
      status: 'pending', 
      progress: 0 
    },
    { 
      id: 5, 
      title: '部署上线', 
      description: '部署系统到生产环境，编写文档，培训用户',
      startDate: '2025-04-16', 
      endDate: '2025-04-30', 
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

  // 获取状态标签样式
  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge variant="success">已完成</Badge>;
      case 'in_progress':
        return <Badge variant="primary">进行中</Badge>;
      case 'pending':
        return <Badge variant="warning">待处理</Badge>;
      case 'delayed':
        return <Badge variant="danger">已延期</Badge>;
      default:
        return <Badge>未知</Badge>;
    }
  };

  // 格式化日期
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  // 计算两个日期之间的天数
  const getDaysBetween = (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    return Math.round((end - start) / (1000 * 60 * 60 * 24));
  };

  // 计算里程碑的时间线位置
  const calculateTimelinePosition = (startDate, endDate) => {
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
        <div className="mb-12">
          <PageTitle className="mb-3">项目进度</PageTitle>
          <PageDescription>跟踪项目整体进度和里程碑完成情况</PageDescription>
        </div>

        {/* 项目概览 */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">项目概览</h2>
          <Card>
            <CardHeader>
              <CardTitle>{projectInfo.name}</CardTitle>
              <p className="text-gray-500">
                项目周期: {formatDate(projectInfo.startDate)} - {formatDate(projectInfo.endDate)}
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">时间进度</h3>
                  <div className="flex justify-between text-sm mb-1">
                    <span>已用时间</span>
                    <span>{calculateTimeProgress()}%</span>
                  </div>
                  <Progress value={calculateTimeProgress()} className="mb-2" />
                  <p className="text-sm text-gray-500">
                    已经过 {projectInfo.daysElapsed} 天 / 总计 {projectInfo.daysTotal} 天
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">工作进度</h3>
                  <div className="flex justify-between text-sm mb-1">
                    <span>完成度</span>
                    <span>{projectInfo.progress}%</span>
                  </div>
                  <Progress value={projectInfo.progress} className="mb-2" />
                  <p className="text-sm text-gray-500">
                    已完成 {milestones.filter(m => m.status === 'completed').length} 个里程碑 / 总计 {milestones.length} 个里程碑
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">进度对比</h3>
                  <div className="relative h-8 bg-gray-100 rounded-md overflow-hidden">
                    <div 
                      className="absolute top-0 left-0 h-full bg-blue-600" 
                      style={{ width: `${calculateTimeProgress()}%` }}
                    >
                      <span className="absolute inset-0 flex items-center justify-center text-xs text-white font-medium">
                        时间 {calculateTimeProgress()}%
                      </span>
                    </div>
                    <div 
                      className="absolute top-0 left-0 h-full bg-green-600 border-r-2 border-white" 
                      style={{ width: `${projectInfo.progress}%` }}
                    >
                      <span className="absolute inset-0 flex items-center justify-center text-xs text-white font-medium">
                        工作 {projectInfo.progress}%
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-500 mt-2">
                    {projectInfo.progress > calculateTimeProgress() ? '进度超前' : '进度滞后'}
                    {Math.abs(projectInfo.progress - calculateTimeProgress())}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 项目时间线 */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">项目时间线</h2>
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
                    今天
                  </div>
                </div>
                
                {/* 里程碑标记 */}
                <div className="relative h-16">
                  {milestones.map((milestone) => {
                    const position = calculateTimelinePosition(milestone.startDate, milestone.endDate);
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

        {/* 里程碑详情 */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">里程碑详情</h2>
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
                      <p className="text-sm text-gray-500 mb-1">时间范围</p>
                      <p className="font-medium">
                        {formatDate(milestone.startDate)} - {formatDate(milestone.endDate)}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        持续 {getDaysBetween(milestone.startDate, milestone.endDate)} 天
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">完成进度</p>
                      <div className="flex justify-between text-sm mb-1">
                        <span>进度</span>
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
