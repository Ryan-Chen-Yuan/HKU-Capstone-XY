'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { ApiService } from './api-service';

// 创建数据上下文
const DataContext = createContext();

// 数据提供者组件
export function DataProvider({ children }) {
  const [projects, setProjects] = useState([]);
  const [users, setUsers] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [milestones, setMilestones] = useState([]);
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 初始化数据
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // 并行获取多个数据源
        const [
          projectsResponse, 
          usersResponse, 
          tasksResponse, 
          milestonesResponse,
          proposalsResponse
        ] = await Promise.all([
          ApiService.getProjects(),
          ApiService.getUsers(),
          ApiService.getTasks(),
          ApiService.getMilestones(),
          ApiService.getProposals()
        ]);
        
        setProjects(projectsResponse.projects || []);
        setUsers(usersResponse.users || []);
        setTasks(tasksResponse.tasks || []);
        setMilestones(milestonesResponse.milestones || []);
        setProposals(proposalsResponse.proposals || []);
      } catch (err) {
        console.error('获取初始数据错误:', err);
        setError('获取数据失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };
    
    fetchInitialData();
  }, []);

  // 刷新数据方法
  const refreshData = async (dataType) => {
    try {
      setLoading(true);
      setError(null);
      
      switch (dataType) {
        case 'projects':
          const projectsResponse = await ApiService.getProjects();
          setProjects(projectsResponse.projects || []);
          break;
        case 'users':
          const usersResponse = await ApiService.getUsers();
          setUsers(usersResponse.users || []);
          break;
        case 'tasks':
          const tasksResponse = await ApiService.getTasks();
          setTasks(tasksResponse.tasks || []);
          break;
        case 'milestones':
          const milestonesResponse = await ApiService.getMilestones();
          setMilestones(milestonesResponse.milestones || []);
          break;
        case 'proposals':
          const proposalsResponse = await ApiService.getProposals();
          setProposals(proposalsResponse.proposals || []);
          break;
        case 'all':
          await fetchInitialData();
          break;
        default:
          throw new Error('未知的数据类型');
      }
    } catch (err) {
      console.error('刷新数据错误:', err);
      setError('刷新数据失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 提供上下文值
  const value = {
    projects,
    users,
    tasks,
    milestones,
    proposals,
    loading,
    error,
    refreshData,
    // 项目相关方法
    getProject: (id) => projects.find(p => p.id === id),
    createProject: async (projectData) => {
      const result = await ApiService.createProject(projectData);
      await refreshData('projects');
      return result;
    },
    updateProject: async (id, projectData) => {
      const result = await ApiService.updateProject(id, projectData);
      await refreshData('projects');
      return result;
    },
    deleteProject: async (id) => {
      const result = await ApiService.deleteProject(id);
      await refreshData('projects');
      return result;
    },
    // 用户相关方法
    getUser: (id) => users.find(u => u.id === id),
    createUser: async (userData) => {
      const result = await ApiService.createUser(userData);
      await refreshData('users');
      return result;
    },
    updateUser: async (id, userData) => {
      const result = await ApiService.updateUser(id, userData);
      await refreshData('users');
      return result;
    },
    deleteUser: async (id) => {
      const result = await ApiService.deleteUser(id);
      await refreshData('users');
      return result;
    },
    // 任务相关方法
    getTask: (id) => tasks.find(t => t.id === id),
    getUserTasks: (userId) => tasks.filter(t => t.user_id === userId),
    getMilestoneTasks: (milestoneId) => tasks.filter(t => t.milestone_id === milestoneId),
    createTask: async (taskData) => {
      const result = await ApiService.createTask(taskData);
      await refreshData('tasks');
      return result;
    },
    updateTask: async (id, taskData) => {
      const result = await ApiService.updateTask(id, taskData);
      await refreshData('tasks');
      return result;
    },
    deleteTask: async (id) => {
      const result = await ApiService.deleteTask(id);
      await refreshData('tasks');
      return result;
    },
    // 里程碑相关方法
    getMilestone: (id) => milestones.find(m => m.id === id),
    getProjectMilestones: (projectId) => milestones.filter(m => m.project_id === projectId),
    createMilestone: async (milestoneData) => {
      const result = await ApiService.createMilestone(milestoneData);
      await refreshData('milestones');
      return result;
    },
    updateMilestone: async (id, milestoneData) => {
      const result = await ApiService.updateMilestone(id, milestoneData);
      await refreshData('milestones');
      return result;
    },
    deleteMilestone: async (id) => {
      const result = await ApiService.deleteMilestone(id);
      await refreshData('milestones');
      return result;
    },
    // 提案相关方法
    getProposal: (id) => proposals.find(p => p.id === id),
    getProjectProposals: (projectId) => proposals.filter(p => p.project_id === projectId),
    createProposal: async (proposalData) => {
      const result = await ApiService.createProposal(proposalData);
      await refreshData('proposals');
      return result;
    },
    updateProposal: async (id, proposalData) => {
      const result = await ApiService.updateProposal(id, proposalData);
      await refreshData('proposals');
      return result;
    },
    deleteProposal: async (id) => {
      const result = await ApiService.deleteProposal(id);
      await refreshData('proposals');
      return result;
    }
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
}

// 使用数据的钩子
export function useData() {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
}
