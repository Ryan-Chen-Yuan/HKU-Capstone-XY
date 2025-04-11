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
import { useRouter } from 'next/navigation';

export default function ProposalDetail({ params }) {
  const proposalId = params.id;
  const router = useRouter();
  const [proposal, setProposal] = useState(null);
  const [sections, setSections] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isSectionModalOpen, setIsSectionModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [currentSection, setCurrentSection] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    order_num: 0
  });

  // 获取提案详情
  const fetchProposalDetail = async () => {
    try {
      setIsLoading(true);
      setError('');
      
      const response = await fetch(`/api/proposals/${proposalId}`);
      const data = await response.json();
      
      if (data.success) {
        setProposal(data.proposal);
        setSections(data.sections || []);
        setDocuments(data.documents || []);
      } else {
        setError(data.message || '获取提案详情失败');
      }
    } catch (err) {
      console.error('获取提案详情错误:', err);
      setError('获取提案详情失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    if (proposalId) {
      fetchProposalDetail();
    }
  }, [proposalId]);

  // 处理表单输入变化
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // 打开新增章节模态框
  const openAddSectionModal = () => {
    setCurrentSection(null);
    
    setFormData({
      title: '',
      content: '',
      order_num: sections.length
    });
    setIsSectionModalOpen(true);
  };

  // 打开编辑章节模态框
  const openEditSectionModal = (section) => {
    setCurrentSection(section);
    setFormData({
      title: section.title,
      content: section.content,
      order_num: section.order_num
    });
    setIsSectionModalOpen(true);
  };

  // 打开删除确认模态框
  const openDeleteModal = (section) => {
    setCurrentSection(section);
    setIsDeleteModalOpen(true);
  };

  // 提交章节表单
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setIsLoading(true);
      setError('');
      
      let response;
      
      if (currentSection) {
        // 更新章节
        response = await fetch(`/api/proposal-sections/${currentSection.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });
      } else {
        // 创建章节
        response = await fetch('/api/proposal-sections', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...formData,
            proposal_id: proposalId
          }),
        });
      }
      
      const data = await response.json();
      
      if (data.success) {
        setIsSectionModalOpen(false);
        fetchProposalDetail();
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

  // 删除章节
  const handleDelete = async () => {
    if (!currentSection) return;
    
    try {
      setIsLoading(true);
      setError('');
      
      const response = await fetch(`/api/proposal-sections/${currentSection.id}`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIsDeleteModalOpen(false);
        fetchProposalDetail();
      } else {
        setError(data.message || '删除失败');
      }
    } catch (err) {
      console.error('删除章节错误:', err);
      setError('删除失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !proposal) {
    return (
      <div className="flex justify-center my-12">
        <ArrowPathIcon className="h-8 w-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex justify-between items-center">
        <div>
          <button 
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-800 mb-2"
          >
            &larr; 返回提案列表
          </button>
          <h1 className="text-2xl font-semibold text-gray-900">{proposal?.title}</h1>
          <p className="text-gray-500">管理提案章节和内容</p>
        </div>
        <button
          onClick={openAddSectionModal}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-1" />
          新增章节
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
      
      {sections.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <p className="text-gray-500">该提案还没有章节内容，请点击"新增章节"按钮添加内容。</p>
        </div>
      ) : (
        <div className="space-y-6">
          {sections.sort((a, b) => a.order_num - b.order_num).map((section) => (
            <div key={section.id} className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">{section.title}</h3>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => openEditSectionModal(section)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      <PencilIcon className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => openDeleteModal(section)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
                
                <div className="prose max-w-none">
                  {section.content.split('\n').map((paragraph, idx) => (
                    <p key={idx} className="text-gray-700 mb-2">{paragraph}</p>
                  ))}
                </div>
              </div>
              
              <div className="bg-gray-50 px-6 py-3 flex justify-between items-center">
                <span className="text-sm text-gray-500">顺序: {section.order_num + 1}</span>
                <span className="text-sm text-gray-500">
                  最后更新: {new Date(section.updated_at).toLocaleString('zh-CN')}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* 章节表单模态框 */}
      <Transition appear show={isSectionModalOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => setIsSectionModalOpen(false)}>
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
                <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 text-gray-900"
                  >
                    {currentSection ? '编辑章节' : '新增章节'}
                  </Dialog.Title>
                  
                  <form onSubmit={handleSubmit} className="mt-4">
                    <div className="mb-4">
                      <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                        章节标题
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
                      <label htmlFor="content" className="block text-sm font-medium text-gray-700">
                        章节内容
                      </label>
                      <textarea
                        id="content"
                        name="content"
                        rows={10}
                        value={formData.content}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        required
                      />
                    </div>
                    
                    <div className="mb-4">
                      <label htmlFor="order_num" className="block text-sm font-medium text-gray-700">
                        显示顺序
                      </label>
                      <input
                        type="number"
                        id="order_num"
                        name="order_num"
                        min="0"
                        value={formData.order_num}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        required
                      />
                      <p className="mt-1 text-xs text-gray-500">数字越小，显示越靠前</p>
                    </div>
                    
                    <div className="mt-6 flex justify-end space-x-3">
                      <button
                        type="button"
                        onClick={() => setIsSectionModalOpen(false)}
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
                      您确定要删除章节 <span className="font-semibold">{currentSection?.title}</span> 吗？此操作不可撤销。
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
