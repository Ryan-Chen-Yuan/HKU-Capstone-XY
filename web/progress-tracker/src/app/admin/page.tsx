'use client';

import { useState, useEffect } from 'react';
import { 
  ArrowPathIcon, 
  UserIcon, 
  ClipboardDocumentListIcon, 
  DocumentTextIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

// 仪表盘卡片组件
function DashboardCard({ title, value, icon, color }: { 
  title: string; 
  value: string | number; 
  icon: React.ReactNode;
  color: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 flex items-center">
      <div className={`rounded-full p-4 ${color}`}>
        {icon}
      </div>
      <div className="ml-4">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
      </div>
    </div>
  );
}

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    users: 0,
    projects: 0,
    tasks: 0,
    proposals: 0
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // 获取统计数据
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setIsLoading(true);
        
        // 获取用户数量
        const usersRes = await fetch('/api/users');
        const usersData = await usersRes.json();
        
        // 获取项目数量
        const projectsRes = await fetch('/api/projects');
        const projectsData = await projectsRes.json();
        
        // 获取任务数量
        const tasksRes = await fetch('/api/tasks');
        const tasksData = await tasksRes.json();
        
        // 获取提案数量
        const proposalsRes = await fetch('/api/proposals');
        const proposalsData = await proposalsRes.json();
        
        setStats({
          users: usersData.users?.length || 0,
          projects: projectsData.projects?.length || 0,
          tasks: tasksData.tasks?.length || 0,
          proposals: proposalsData.proposals?.length || 0
        });
      } catch (err) {
        console.error('获取统计数据失败:', err);
        setError('获取统计数据失败，请刷新页面重试');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchStats();
  }, []);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">仪表盘</h1>
        <p className="text-gray-500">欢迎使用毕设项目进度展示系统管理后台</p>
      </div>
      
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}
      
      {isLoading ? (
        <div className="flex justify-center my-12">
          <ArrowPathIcon className="h-8 w-8 text-blue-500 animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <DashboardCard 
            title="用户数量" 
            value={stats.users} 
            icon={<UserIcon className="h-6 w-6 text-blue-500" />}
            color="bg-blue-100"
          />
          <DashboardCard 
            title="项目数量" 
            value={stats.projects} 
            icon={<ChartBarIcon className="h-6 w-6 text-green-500" />}
            color="bg-green-100"
          />
          <DashboardCard 
            title="任务数量" 
            value={stats.tasks} 
            icon={<ClipboardDocumentListIcon className="h-6 w-6 text-orange-500" />}
            color="bg-orange-100"
          />
          <DashboardCard 
            title="提案数量" 
            value={stats.proposals} 
            icon={<DocumentTextIcon className="h-6 w-6 text-purple-500" />}
            color="bg-purple-100"
          />
        </div>
      )}
      
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">系统信息</h2>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500">系统名称</h3>
              <p className="text-gray-900">毕设项目进度展示系统</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">版本</h3>
              <p className="text-gray-900">1.0.0</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">前端框架</h3>
              <p className="text-gray-900">Next.js</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">数据库</h3>
              <p className="text-gray-900">SQLite</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
