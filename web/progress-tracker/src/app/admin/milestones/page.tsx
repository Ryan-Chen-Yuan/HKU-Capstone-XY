'use client';

import { useState, useEffect } from 'react';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  ArrowPathIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';

export default function MilestonesManagement() {
  const [milestones, setMilestones] = useState([]);
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [currentMilestone, setCurrentMilestone] = useState(null);
  const [formData, setFormData] = useState({
    project_id: '',
    title: '',
    description: '',
    due_date: '',
    status: 'pending',
    progress: 0
  });

  // 获取里程碑列表
  const fetchMilestones = async () => {
    try {
      setIsLoading(true);
      setError('');
      
      const response = await fetch('/api/milestones');
      const data = await response.json();
      
      if (data.success) {
        setMilestones(data.milestones);
      } else {
        setError(data.message || '获取里程碑列表失败');
      }
    } catch (err) {
      console.error('获取里程碑列表错误:', err);
      setError('获取里程碑列表失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 获取项目列表
  const fetchProjects = async () => {
    try {
      const response = await fetch('/api/projects');
      const data = await response.json();
      
      if (data.success) {
        setProjects(data.projects);
      }
    } catch (err) {
      console.error('获取项目列表错误:', err);
    }
  };

  // 初始加载
  useEffect(() => {
    Promise.all([fetchMilestones(), fetchProjects()]);
  }, []);

  // 处理表单输入变化
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // 打开新增里程碑模态框
  const openAddModal = () => {
    setCurrentMilestone(null);
    const nextMonth = new Date();
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    
    setFormData({
      project_id: projects.length > 0 ? projects[0].id : '',
      title: '',
      description: '',
      due_date: nextMonth.toISOString().split('T')[0],
      status: 'pending',
      progress: 0
    });
    setIsModalOpen(true);
  };

  // 打开编辑里程碑模态框
  const openEditModal = (milestone) => {
    setCurrentMilestone(milestone);
    setFormData({
      project_id: milestone.project_id,
      title: milestone.title,
      description: milestone.description || '',
      due_date: new Date(milestone.due_date).toISOString().split('T')[0],
      status: milestone.status,
      progress: milestone.progress
    });
    setIsModalOpen(true);
  };

  // 打开删除确认模态框
  const openDeleteModal = (milestone) => {
    setCurrentMilestone(milestone);
    setIsDeleteModalOpen(true);
  };

  // 提交表单
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setIsLoading(true);
      setError('');
      
      let response;
      
      if (currentMilestone) {
        // 更新里程碑
        response = await fetch(`/api/milestones/${currentMilestone.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });
      } else {
        // 创建里程碑
        response = await fetch('/api/milestones', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });
      }
      
      const data = await response.json();
      
      if (data.success) {
        setIsModalOpen(false);
        fetchMilestones();
      } else {
        setError(data.message || '操作失败');
      }
    } catch (err) {
      console.error('提交表单错误:', err);
      setError('操作失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 删除里程碑
  const handleDelete = async () => {
    if (!currentMilestone) return;
    
    try {
      setIsLoading(true);
      setError('');
      
      const response = await fetch(`/api/milestones/${currentMilestone.id}`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIsDeleteModalOpen(false);
        fetchMilestones();
      } else {
        setError(data.message || '删除失败');
      }
    } catch (err) {
      console.error('删除里程碑错误:', err);
      setError('删除失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 格式化日期
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  // 获取状态标签样式
  const getStatusStyle = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'delayed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // 获取状态文本
  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'in_progress':
        return '进行中';
      case 'pending':
        return '待处理';
      case 'delayed':
        return '已延期';
      default:
        return '未知';
    }
  };

  // 获取项目名称
  const getProjectName = (projectId) => {
    const project = projects.find(p => p.id === projectId);
    return project ? project.name : '未知项目';
  };

  return (
    <div>
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">里程碑管理</h1>
          <p className="text-gray-500">管理项目里程碑和进度</p>
        </div>
        <button
          onClick={openAddModal}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-1" />
          新增里程碑
        </button>
      </div>
      
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <ExclamationCircleIcon className="h-5 w-5 text-red-500" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}
      
      {isLoading && !milestones.length ? (
        <div className="flex justify-center my-12">
          <ArrowPathIcon className="h-8 w-8 text-blue-500 animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {milestones.map((milestone) => (
            <div key={milestone.id} className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">{milestone.title}</h3>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusStyle(milestone.status)}`}>
                    {getStatusText(milestone.status)}
                  </span>
                </div>
                
                <p className="text-sm text-gray-500 mb-2">{getProjectName(milestone.project_id)}</p>
                <p className="text-sm text-gray-500 mb-4 line-clamp-2">{milestone.description || '无描述'}</p>
                
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-500 mb-1">
                    <span>进度</span>
                    <span>{milestone.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${milestone.progress}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="flex justify-between text-sm">
                  <div>
                    <p className="text-gray-500">截止日期</p>
                    <p className="font-medium">{formatDate(milestone.due_date)}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-6 py-3 flex justify-end space-x-3">
                <button
                  onClick={() => openEditModal(milestone)}
                  className="text-blue-600 hover:text-blue-900"
                >
                  <PencilIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={() => openDeleteModal(milestone)}
                  className="text-red-600 hover:text-red-900"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* 里程碑表单模态框 */}
      <Transition appear show={isModalOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => setIsModalOpen(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-25" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 text-gray-900"
                  >
                    {currentMilestone ? '编辑里程碑' : '新增里程碑'}
                  </Dialog.Title>
                  
                  <form onSubmit={handleSubmit} className="mt-4">
                    <div className="mb-4">
                      <label htmlFor="project_id" className="block text-sm font-medium text-gray-700">
                        所属项目
                      </label>
                      <select
                        id="project_id"
                        name="project_id"
                        value={formData.project_id}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        required
                      >
                        {projects.map(project => (
                          <option key={project.id} value={project.id}>{project.name}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div className="mb-4">
                      <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                        里程碑名称
                      </label>
                      <input
                        type="text"
                        id="title"
                        name="title"
                        value={formData.title}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        required
                      />
                    </div>
                    
                    <div className="mb-4">
                      <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                        描述
                      </label>
                      <textarea
                        id="description"
                        name="description"
                        rows={3}
                        value={formData.description}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                    
                    <div className="mb-4">
                      <label htmlFor="due_date" className="block text-sm font-medium text-gray-700">
                        截止日期
                      </label>
                      <input
                        type="date"
                        id="due_date"
                        name="due_date"
                        value={formData.due_date}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        required
                      />
                    </div>
                    
                    <div className="mb-4">
                      <label htmlFor="status" className="block text-sm font-medium text-gray-700">
                        状态
                      </label>
                      <select
                        id="status"
                        name="status"
                        value={formData.status}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        required
                      >
                        <option value="pending">待处理</option>
                        <option value="in_progress">进行中</option>
                        <option value="completed">已完成</option>
                        <option value="delayed">已延期</option>
                      </select>
                    </div>
                    
                    <div className="mb-4">
                      <label htmlFor="progress" className="block text-sm font-medium text-gray-700">
                        进度 ({formData.progress}%)
                      </label>
                      <input
                        type="range"
                        id="progress"
                        name="progress"
                        min="0"
                        max="100"
                        value={formData.progress}
                        onChange={handleInputChange}
                        className="mt-1 block w-full"
                      />
                    </div>
                    
                    <div className="mt-6 flex justify-end space-x-3">
                      <button
                        type="button"
                        onClick={() => setIsModalOpen(false)}
                        className="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      >
                        取消
                      </button>
                      <button
                        type="submit"
                        disabled={isLoading}
                        className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                      >
                        {isLoading ? '处理中...' : '保存'}
                      </button>
                    </div>
                  </form>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
      
      {/* 删除确认模态框 */}
      <Transition appear show={isDeleteModalOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => setIsDeleteModalOpen(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-25" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 text-gray-900"
                  >
                    确认删除
                  </Dialog.Title>
                  <div className="mt-2">
                    <p className="text-sm text-gray-500">
                      您确定要删除里程碑 <span className="font-semibold">{currentMilestone?.title}</span> 吗？此操作将同时删除与该里程碑相关的所有任务，且不可撤销。
                    </p>
                  </div>

                  <div className="mt-6 flex justify-end space-x-3">
                    <button
                      type="button"
                      onClick={() => setIsDeleteModalOpen(false)}
                      className="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                      取消
                    </button>
                    <button
                      type="button"
                      onClick={handleDelete}
                      disabled={isLoading}
                      className="inline-flex justify-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
                    >
                      {isLoading ? '处理中...' : '删除'}
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </div>
  );
}
