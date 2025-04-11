'use client';

// API服务封装，用于前后端集成
export class ApiService {
  // 获取认证头
  static getAuthHeaders() {
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null;
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  // 通用请求方法
  static async request(url, method = 'GET', data = null) {
    try {
      const headers = {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders()
      };

      const options = {
        method,
        headers,
        cache: 'no-store'
      };

      if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
      }

      const response = await fetch(url, options);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || '请求失败');
      }

      return result;
    } catch (error) {
      console.error(`API请求错误 (${url}):`, error);
      throw error;
    }
  }

  // 用户相关API
  static async getUsers() {
    return this.request('/api/users');
  }

  static async getUser(id) {
    return this.request(`/api/users/${id}`);
  }

  static async createUser(userData) {
    return this.request('/api/users', 'POST', userData);
  }

  static async updateUser(id, userData) {
    return this.request(`/api/users/${id}`, 'PUT', userData);
  }

  static async deleteUser(id) {
    return this.request(`/api/users/${id}`, 'DELETE');
  }

  // 项目相关API
  static async getProjects() {
    return this.request('/api/projects');
  }

  static async getProject(id) {
    return this.request(`/api/projects/${id}`);
  }

  static async createProject(projectData) {
    return this.request('/api/projects', 'POST', projectData);
  }

  static async updateProject(id, projectData) {
    return this.request(`/api/projects/${id}`, 'PUT', projectData);
  }

  static async deleteProject(id) {
    return this.request(`/api/projects/${id}`, 'DELETE');
  }

  // 里程碑相关API
  static async getMilestones() {
    return this.request('/api/milestones');
  }

  static async getMilestone(id) {
    return this.request(`/api/milestones/${id}`);
  }

  static async createMilestone(milestoneData) {
    return this.request('/api/milestones', 'POST', milestoneData);
  }

  static async updateMilestone(id, milestoneData) {
    return this.request(`/api/milestones/${id}`, 'PUT', milestoneData);
  }

  static async deleteMilestone(id) {
    return this.request(`/api/milestones/${id}`, 'DELETE');
  }

  // 任务相关API
  static async getTasks() {
    return this.request('/api/tasks');
  }

  static async getTask(id) {
    return this.request(`/api/tasks/${id}`);
  }

  static async createTask(taskData) {
    return this.request('/api/tasks', 'POST', taskData);
  }

  static async updateTask(id, taskData) {
    return this.request(`/api/tasks/${id}`, 'PUT', taskData);
  }

  static async deleteTask(id) {
    return this.request(`/api/tasks/${id}`, 'DELETE');
  }

  // 提案相关API
  static async getProposals() {
    return this.request('/api/proposals');
  }

  static async getProposal(id) {
    return this.request(`/api/proposals/${id}`);
  }

  static async createProposal(proposalData) {
    return this.request('/api/proposals', 'POST', proposalData);
  }

  static async updateProposal(id, proposalData) {
    return this.request(`/api/proposals/${id}`, 'PUT', proposalData);
  }

  static async deleteProposal(id) {
    return this.request(`/api/proposals/${id}`, 'DELETE');
  }

  // 提案章节相关API
  static async getProposalSections(proposalId) {
    return this.request(`/api/proposal-sections?proposal_id=${proposalId}`);
  }

  static async getProposalSection(id) {
    return this.request(`/api/proposal-sections/${id}`);
  }

  static async createProposalSection(sectionData) {
    return this.request('/api/proposal-sections', 'POST', sectionData);
  }

  static async updateProposalSection(id, sectionData) {
    return this.request(`/api/proposal-sections/${id}`, 'PUT', sectionData);
  }

  static async deleteProposalSection(id) {
    return this.request(`/api/proposal-sections/${id}`, 'DELETE');
  }

  // 文档相关API
  static async getDocuments() {
    return this.request('/api/documents');
  }

  static async getDocument(id) {
    return this.request(`/api/documents/${id}`);
  }

  static async createDocument(documentData) {
    return this.request('/api/documents', 'POST', documentData);
  }

  static async updateDocument(id, documentData) {
    return this.request(`/api/documents/${id}`, 'PUT', documentData);
  }

  static async deleteDocument(id) {
    return this.request(`/api/documents/${id}`, 'DELETE');
  }

  // 认证相关API
  static async login(username, password) {
    return this.request('/api/auth/login', 'POST', { username, password });
  }

  static async verifyToken() {
    return this.request('/api/auth/verify');
  }

  static async initializeDatabase() {
    return this.request('/api/auth/init', 'POST');
  }
}
