import { Database } from 'sqlite';
import sqlite3 from 'sqlite3';
import { v4 as uuidv4 } from 'uuid';
import bcrypt from 'bcryptjs';

// 数据库类型定义
export interface DbUser {
  id: string;
  username: string;
  password_hash: string;
  name: string;
  role: string;
  email?: string;
  avatar?: string;
  created_at: string;
  updated_at: string;
}

export interface DbProject {
  id: string;
  name: string;
  description?: string;
  start_date: string;
  end_date: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface DbMilestone {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  due_date: string;
  start_date?: string;
  status: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface DbTask {
  id: string;
  title: string;
  description?: string;
  status: string;
  start_date: string;
  due_date: string;
  completed_date?: string;
  progress: number;
  priority: string;
  user_id: string;
  milestone_id?: string;
  created_at: string;
  updated_at: string;
}

export interface DbProposal {
  id: string;
  project_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface DbProposalSection {
  id: string;
  proposal_id: string;
  title: string;
  content: string;
  order_num: number;
  created_at: string;
  updated_at: string;
}

export interface DbDocument {
  id: string;
  title: string;
  description?: string;
  file_url: string;
  file_type: string;
  upload_date: string;
  proposal_id?: string;
  created_at: string;
  updated_at: string;
}

// 数据库类
class DB {
  private db: Database | null = null;
  private initialized = false;

  // 初始化数据库
  async init() {
    if (this.initialized) return;

    try {
      // 使用内存数据库进行开发
      const sqlite = require('sqlite');
      const sqlite3 = require('sqlite3');
      
      this.db = await sqlite.open({
        filename: ':memory:',
        driver: sqlite3.Database
      });

      await this.createTables();
      this.initialized = true;
      console.log('数据库初始化成功');
    } catch (error) {
      console.error('数据库初始化错误:', error);
      throw error;
    }
  }

  // 获取数据库实例的公共方法
  async getDatabase() {
    if (!this.db) await this.init();
    return this.db;
  }

  // 创建数据库表
  private async createTables() {
    if (!this.db) throw new Error('数据库未初始化');

    // 用户表
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS Users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        email TEXT UNIQUE,
        avatar TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 项目表
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS Projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        start_date TIMESTAMP NOT NULL,
        end_date TIMESTAMP NOT NULL,
        progress INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 里程碑表
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS Milestones (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        start_date TIMESTAMP,
        due_date TIMESTAMP NOT NULL,
        status TEXT NOT NULL,
        progress INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES Projects(id)
      )
    `);

    // 任务表
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS Tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        start_date TIMESTAMP NOT NULL,
        due_date TIMESTAMP NOT NULL,
        completed_date TIMESTAMP,
        progress INTEGER DEFAULT 0,
        priority TEXT NOT NULL,
        user_id TEXT NOT NULL,
        milestone_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(id),
        FOREIGN KEY (milestone_id) REFERENCES Milestones(id)
      )
    `);

    // Proposal表
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS Proposals (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        title TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES Projects(id)
      )
    `);

    // Proposal章节表
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS ProposalSections (
        id TEXT PRIMARY KEY,
        proposal_id TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        order_num INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (proposal_id) REFERENCES Proposals(id)
      )
    `);

    // 文档表
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS Documents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        file_url TEXT NOT NULL,
        file_type TEXT NOT NULL,
        upload_date TIMESTAMP NOT NULL,
        proposal_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (proposal_id) REFERENCES Proposals(id)
      )
    `);
  }

  // 初始化示例数据
  async initializeData() {
    if (!this.db) await this.init();

    try {
      // 创建管理员用户
      const adminId = uuidv4();
      const passwordHash = await bcrypt.hash('admin123', 10);
      await this.db!.run(
        'INSERT INTO Users (id, username, password_hash, name, role) VALUES (?, ?, ?, ?, ?)',
        [adminId, 'admin', passwordHash, '管理员', 'admin']
      );

      // 创建示例项目
      const projectId = uuidv4();
      await this.db!.run(
        'INSERT INTO Projects (id, name, description, start_date, end_date, progress) VALUES (?, ?, ?, ?, ?, ?)',
        [projectId, '毕设项目进度展示网站', '展示毕业设计项目的进度和成果', '2025-01-01', '2025-06-30', 30]
      );

      // 创建示例里程碑
      const milestone1Id = uuidv4();
      const milestone2Id = uuidv4();
      await this.db!.run(
        'INSERT INTO Milestones (id, project_id, title, description, due_date, status, progress) VALUES (?, ?, ?, ?, ?, ?, ?)',
        [milestone1Id, projectId, '需求分析', '完成项目需求分析和规划', '2025-02-15', '已完成', 100]
      );
      await this.db!.run(
        'INSERT INTO Milestones (id, project_id, title, description, due_date, status, progress) VALUES (?, ?, ?, ?, ?, ?, ?)',
        [milestone2Id, projectId, '系统设计', '完成系统架构和数据库设计', '2025-03-15', '进行中', 60]
      );

      // 创建示例任务
      await this.db!.run(
        'INSERT INTO Tasks (id, title, description, status, start_date, due_date, progress, priority, user_id, milestone_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [uuidv4(), '用户需求调研', '收集和分析用户需求', '已完成', '2025-01-10', '2025-01-20', 100, '高', adminId, milestone1Id]
      );
      await this.db!.run(
        'INSERT INTO Tasks (id, title, description, status, start_date, due_date, progress, priority, user_id, milestone_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [uuidv4(), '数据库设计', '设计数据库结构和关系', '进行中', '2025-02-20', '2025-03-05', 70, '高', adminId, milestone2Id]
      );

      // 创建示例提案
      const proposalId = uuidv4();
      await this.db!.run(
        'INSERT INTO Proposals (id, project_id, title) VALUES (?, ?, ?)',
        [proposalId, projectId, '毕设项目设计方案']
      );

      // 创建示例提案章节
      await this.db!.run(
        'INSERT INTO ProposalSections (id, proposal_id, title, content, order_num) VALUES (?, ?, ?, ?, ?)',
        [uuidv4(), proposalId, '项目背景', '本项目旨在解决毕业设计项目进度展示和管理的问题...', 1]
      );
      await this.db!.run(
        'INSERT INTO ProposalSections (id, proposal_id, title, content, order_num) VALUES (?, ?, ?, ?, ?)',
        [uuidv4(), proposalId, '技术方案', '本项目采用Next.js作为前端框架，SQLite作为数据库...', 2]
      );

      console.log('示例数据初始化成功');
    } catch (error) {
      console.error('示例数据初始化错误:', error);
      throw error;
    }
  }

  // 用户相关方法
  async getUsers() {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM Users');
  }

  async getUser(id: string) {
    if (!this.db) await this.init();
    return this.db!.get('SELECT * FROM Users WHERE id = ?', [id]);
  }

  async getUserByUsername(username: string) {
    if (!this.db) await this.init();
    return this.db!.get('SELECT * FROM Users WHERE username = ?', [username]);
  }

  async createUser(userData: Partial<DbUser>) {
    if (!this.db) await this.init();
    const id = uuidv4();
    const now = new Date().toISOString();
    
    await this.db!.run(
      `INSERT INTO Users (id, username, password_hash, name, role, email, avatar, created_at, updated_at) 
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [id, userData.username, userData.password_hash, userData.name, userData.role, userData.email || null, userData.avatar || null, now, now]
    );
    
    return this.getUser(id);
  }

  async updateUser(id: string, userData: Partial<DbUser>) {
    if (!this.db) await this.init();
    const now = new Date().toISOString();
    
    const user = await this.getUser(id);
    if (!user) return null;
    
    const updates = [];
    const values = [];
    
    if (userData.username) {
      updates.push('username = ?');
      values.push(userData.username);
    }
    
    if (userData.password_hash) {
      updates.push('password_hash = ?');
      values.push(userData.password_hash);
    }
    
    if (userData.name) {
      updates.push('name = ?');
      values.push(userData.name);
    }
    
    if (userData.role) {
      updates.push('role = ?');
      values.push(userData.role);
    }
    
    if (userData.email !== undefined) {
      updates.push('email = ?');
      values.push(userData.email || null);
    }
    
    if (userData.avatar !== undefined) {
      updates.push('avatar = ?');
      values.push(userData.avatar || null);
    }
    
    updates.push('updated_at = ?');
    values.push(now);
    
    values.push(id);
    
    await this.db!.run(
      `UPDATE Users SET ${updates.join(', ')} WHERE id = ?`,
      values
    );
    
    return this.getUser(id);
  }

  async deleteUser(id: string) {
    if (!this.db) await this.init();
    
    const user = await this.getUser(id);
    if (!user) return false;
    
    await this.db!.run('DELETE FROM Users WHERE id = ?', [id]);
    return true;
  }

  // 项目相关方法
  async getProjects() {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM Projects');
  }

  async getProject(id: string) {
    if (!this.db) await this.init();
    return this.db!.get('SELECT * FROM Projects WHERE id = ?', [id]);
  }

  async createProject(projectData: Partial<DbProject>) {
    if (!this.db) await this.init();
    const id = uuidv4();
    const now = new Date().toISOString();
    
    await this.db!.run(
      `INSERT INTO Projects (id, name, description, start_date, end_date, progress, created_at, updated_at) 
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [id, projectData.name, projectData.description || null, projectData.start_date, projectData.end_date, projectData.progress || 0, now, now]
    );
    
    return this.getProject(id);
  }

  async updateProject(id: string, projectData: Partial<DbProject>) {
    if (!this.db) await this.init();
    const now = new Date().toISOString();
    
    const project = await this.getProject(id);
    if (!project) return null;
    
    const updates = [];
    const values = [];
    
    if (projectData.name) {
      updates.push('name = ?');
      values.push(projectData.name);
    }
    
    if (projectData.description !== undefined) {
      updates.push('description = ?');
      values.push(projectData.description || null);
    }
    
    if (projectData.start_date) {
      updates.push('start_date = ?');
      values.push(projectData.start_date);
    }
    
    if (projectData.end_date) {
      updates.push('end_date = ?');
      values.push(projectData.end_date);
    }
    
    if (projectData.progress !== undefined) {
      updates.push('progress = ?');
      values.push(projectData.progress);
    }
    
    updates.push('updated_at = ?');
    values.push(now);
    
    values.push(id);
    
    await this.db!.run(
      `UPDATE Projects SET ${updates.join(', ')} WHERE id = ?`,
      values
    );
    
    return this.getProject(id);
  }

  async deleteProject(id: string) {
    if (!this.db) await this.init();
    
    const project = await this.getProject(id);
    if (!project) return false;
    
    await this.db!.run('DELETE FROM Projects WHERE id = ?', [id]);
    return true;
  }

  // 里程碑相关方法
  async getMilestones() {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM Milestones');
  }

  async getMilestone(id: string) {
    if (!this.db) await this.init();
    return this.db!.get('SELECT * FROM Milestones WHERE id = ?', [id]);
  }

  async getProjectMilestones(projectId: string) {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM Milestones WHERE project_id = ?', [projectId]);
  }

  async createMilestone(milestoneData: Partial<DbMilestone>) {
    if (!this.db) await this.init();
    const id = uuidv4();
    const now = new Date().toISOString();
    
    await this.db!.run(
      `INSERT INTO Milestones (id, project_id, title, description, start_date, due_date, status, progress, created_at, updated_at) 
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [id, milestoneData.project_id, milestoneData.title, milestoneData.description || null, milestoneData.start_date || null, milestoneData.due_date, milestoneData.status, milestoneData.progress || 0, now, now]
    );
    
    return this.getMilestone(id);
  }

  async updateMilestone(id: string, milestoneData: Partial<DbMilestone>) {
    if (!this.db) await this.init();
    const now = new Date().toISOString();
    
    const milestone = await this.getMilestone(id);
    if (!milestone) return null;
    
    const updates = [];
    const values = [];
    
    if (milestoneData.project_id) {
      updates.push('project_id = ?');
      values.push(milestoneData.project_id);
    }
    
    if (milestoneData.title) {
      updates.push('title = ?');
      values.push(milestoneData.title);
    }
    
    if (milestoneData.description !== undefined) {
      updates.push('description = ?');
      values.push(milestoneData.description || null);
    }
    
    if (milestoneData.start_date !== undefined) {
      updates.push('start_date = ?');
      values.push(milestoneData.start_date || null);
    }
    
    if (milestoneData.due_date) {
      updates.push('due_date = ?');
      values.push(milestoneData.due_date);
    }
    
    if (milestoneData.status) {
      updates.push('status = ?');
      values.push(milestoneData.status);
    }
    
    if (milestoneData.progress !== undefined) {
      updates.push('progress = ?');
      values.push(milestoneData.progress);
    }
    
    updates.push('updated_at = ?');
    values.push(now);
    
    values.push(id);
    
    await this.db!.run(
      `UPDATE Milestones SET ${updates.join(', ')} WHERE id = ?`,
      values
    );
    
    return this.getMilestone(id);
  }

  async deleteMilestone(id: string) {
    if (!this.db) await this.init();
    
    const milestone = await this.getMilestone(id);
    if (!milestone) return false;
    
    await this.db!.run('DELETE FROM Milestones WHERE id = ?', [id]);
    return true;
  }

  // 任务相关方法
  async getTasks() {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM Tasks');
  }

  async getTask(id: string) {
    if (!this.db) await this.init();
    return this.db!.get('SELECT * FROM Tasks WHERE id = ?', [id]);
  }

  async getUserTasks(userId: string) {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM Tasks WHERE user_id = ?', [userId]);
  }

  async getMilestoneTasks(milestoneId: string) {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM Tasks WHERE milestone_id = ?', [milestoneId]);
  }

  async createTask(taskData: Partial<DbTask>) {
    if (!this.db) await this.init();
    const id = uuidv4();
    const now = new Date().toISOString();
    
    await this.db!.run(
      `INSERT INTO Tasks (id, title, description, status, start_date, due_date, completed_date, progress, priority, user_id, milestone_id, created_at, updated_at) 
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [id, taskData.title, taskData.description || null, taskData.status, taskData.start_date, taskData.due_date, taskData.completed_date || null, taskData.progress || 0, taskData.priority, taskData.user_id, taskData.milestone_id || null, now, now]
    );
    
    return this.getTask(id);
  }

  async updateTask(id: string, taskData: Partial<DbTask>) {
    if (!this.db) await this.init();
    const now = new Date().toISOString();
    
    const task = await this.getTask(id);
    if (!task) return null;
    
    const updates = [];
    const values = [];
    
    if (taskData.title) {
      updates.push('title = ?');
      values.push(taskData.title);
    }
    
    if (taskData.description !== undefined) {
      updates.push('description = ?');
      values.push(taskData.description || null);
    }
    
    if (taskData.status) {
      updates.push('status = ?');
      values.push(taskData.status);
    }
    
    if (taskData.start_date) {
      updates.push('start_date = ?');
      values.push(taskData.start_date);
    }
    
    if (taskData.due_date) {
      updates.push('due_date = ?');
      values.push(taskData.due_date);
    }
    
    if (taskData.completed_date !== undefined) {
      updates.push('completed_date = ?');
      values.push(taskData.completed_date || null);
    }
    
    if (taskData.progress !== undefined) {
      updates.push('progress = ?');
      values.push(taskData.progress);
    }
    
    if (taskData.priority) {
      updates.push('priority = ?');
      values.push(taskData.priority);
    }
    
    if (taskData.user_id) {
      updates.push('user_id = ?');
      values.push(taskData.user_id);
    }
    
    if (taskData.milestone_id !== undefined) {
      updates.push('milestone_id = ?');
      values.push(taskData.milestone_id || null);
    }
    
    updates.push('updated_at = ?');
    values.push(now);
    
    values.push(id);
    
    await this.db!.run(
      `UPDATE Tasks SET ${updates.join(', ')} WHERE id = ?`,
      values
    );
    
    return this.getTask(id);
  }

  async deleteTask(id: string) {
    if (!this.db) await this.init();
    
    const task = await this.getTask(id);
    if (!task) return false;
    
    await this.db!.run('DELETE FROM Tasks WHERE id = ?', [id]);
    return true;
  }

  // Proposal相关方法
  async getProposals() {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM Proposals');
  }

  async getProposal(id: string) {
    if (!this.db) await this.init();
    return this.db!.get('SELECT * FROM Proposals WHERE id = ?', [id]);
  }

  async getProjectProposals(projectId: string) {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM Proposals WHERE project_id = ?', [projectId]);
  }

  async createProposal(proposalData: Partial<DbProposal>) {
    if (!this.db) await this.init();
    const id = uuidv4();
    const now = new Date().toISOString();
    
    await this.db!.run(
      `INSERT INTO Proposals (id, project_id, title, created_at, updated_at) 
       VALUES (?, ?, ?, ?, ?)`,
      [id, proposalData.project_id, proposalData.title, now, now]
    );
    
    return this.getProposal(id);
  }

  async updateProposal(id: string, proposalData: Partial<DbProposal>) {
    if (!this.db) await this.init();
    const now = new Date().toISOString();
    
    const proposal = await this.getProposal(id);
    if (!proposal) return null;
    
    const updates = [];
    const values = [];
    
    if (proposalData.project_id) {
      updates.push('project_id = ?');
      values.push(proposalData.project_id);
    }
    
    if (proposalData.title) {
      updates.push('title = ?');
      values.push(proposalData.title);
    }
    
    updates.push('updated_at = ?');
    values.push(now);
    
    values.push(id);
    
    await this.db!.run(
      `UPDATE Proposals SET ${updates.join(', ')} WHERE id = ?`,
      values
    );
    
    return this.getProposal(id);
  }

  async deleteProposal(id: string) {
    if (!this.db) await this.init();
    
    const proposal = await this.getProposal(id);
    if (!proposal) return false;
    
    await this.db!.run('DELETE FROM Proposals WHERE id = ?', [id]);
    return true;
  }

  // Proposal章节相关方法
  async getProposalSections() {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM ProposalSections');
  }

  async getProposalSection(id: string) {
    if (!this.db) await this.init();
    return this.db!.get('SELECT * FROM ProposalSections WHERE id = ?', [id]);
  }

  async getProposalSectionsByProposal(proposalId: string) {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM ProposalSections WHERE proposal_id = ? ORDER BY order_num', [proposalId]);
  }

  async createProposalSection(sectionData: Partial<DbProposalSection>) {
    if (!this.db) await this.init();
    const id = uuidv4();
    const now = new Date().toISOString();
    
    await this.db!.run(
      `INSERT INTO ProposalSections (id, proposal_id, title, content, order_num, created_at, updated_at) 
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [id, sectionData.proposal_id, sectionData.title, sectionData.content, sectionData.order_num, now, now]
    );
    
    return this.getProposalSection(id);
  }

  async updateProposalSection(id: string, sectionData: Partial<DbProposalSection>) {
    if (!this.db) await this.init();
    const now = new Date().toISOString();
    
    const section = await this.getProposalSection(id);
    if (!section) return null;
    
    const updates = [];
    const values = [];
    
    if (sectionData.proposal_id) {
      updates.push('proposal_id = ?');
      values.push(sectionData.proposal_id);
    }
    
    if (sectionData.title) {
      updates.push('title = ?');
      values.push(sectionData.title);
    }
    
    if (sectionData.content) {
      updates.push('content = ?');
      values.push(sectionData.content);
    }
    
    if (sectionData.order_num !== undefined) {
      updates.push('order_num = ?');
      values.push(sectionData.order_num);
    }
    
    updates.push('updated_at = ?');
    values.push(now);
    
    values.push(id);
    
    await this.db!.run(
      `UPDATE ProposalSections SET ${updates.join(', ')} WHERE id = ?`,
      values
    );
    
    return this.getProposalSection(id);
  }

  async deleteProposalSection(id: string) {
    if (!this.db) await this.init();
    
    const section = await this.getProposalSection(id);
    if (!section) return false;
    
    await this.db!.run('DELETE FROM ProposalSections WHERE id = ?', [id]);
    return true;
  }
  
  // 文档相关方法
  async getDocuments() {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM Documents');
  }
  
  async getDocument(id: string) {
    if (!this.db) await this.init();
    return this.db!.get('SELECT * FROM Documents WHERE id = ?', [id]);
  }
  
  async getProposalDocuments(proposalId: string) {
    if (!this.db) await this.init();
    return this.db!.all('SELECT * FROM Documents WHERE proposal_id = ?', [proposalId]);
  }
  
  async createDocument(documentData: Partial<DbDocument>) {
    if (!this.db) await this.init();
    const id = uuidv4();
    const now = new Date().toISOString();
    
    await this.db!.run(
      `INSERT INTO Documents (id, title, description, file_url, file_type, upload_date, proposal_id, created_at, updated_at) 
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [id, documentData.title, documentData.description || null, documentData.file_url, documentData.file_type, documentData.upload_date, documentData.proposal_id || null, now, now]
    );
    
    return this.getDocument(id);
  }
  
  async updateDocument(id: string, documentData: Partial<DbDocument>) {
    if (!this.db) await this.init();
    const now = new Date().toISOString();
    
    const document = await this.getDocument(id);
    if (!document) return null;
    
    const updates = [];
    const values = [];
    
    if (documentData.title) {
      updates.push('title = ?');
      values.push(documentData.title);
    }
    
    if (documentData.description !== undefined) {
      updates.push('description = ?');
      values.push(documentData.description || null);
    }
    
    if (documentData.file_url) {
      updates.push('file_url = ?');
      values.push(documentData.file_url);
    }
    
    if (documentData.file_type) {
      updates.push('file_type = ?');
      values.push(documentData.file_type);
    }
    
    if (documentData.upload_date) {
      updates.push('upload_date = ?');
      values.push(documentData.upload_date);
    }
    
    if (documentData.proposal_id !== undefined) {
      updates.push('proposal_id = ?');
      values.push(documentData.proposal_id || null);
    }
    
    updates.push('updated_at = ?');
    values.push(now);
    
    values.push(id);
    
    await this.db!.run(
      `UPDATE Documents SET ${updates.join(', ')} WHERE id = ?`,
      values
    );
    
    return this.getDocument(id);
  }
  
  async deleteDocument(id: string) {
    if (!this.db) await this.init();
    
    const document = await this.getDocument(id);
    if (!document) return false;
    
    await this.db!.run('DELETE FROM Documents WHERE id = ?', [id]);
    return true;
  }
}

// 导出数据库实例
export const db = new DB();

// 添加缺失的函数
export const getDb = async () => {
  await db.init();
  return db.getDatabase();
};

export const initDatabase = async () => {
  await db.init();
  await db.initializeData();
  return true;
};
