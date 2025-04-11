// 数据库表结构定义

export interface User {
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

export interface Project {
  id: string;
  name: string;
  description?: string;
  start_date: string;
  end_date: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface Milestone {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  due_date: string;
  status: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface Task {
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

export interface Proposal {
  id: string;
  project_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ProposalSection {
  id: string;
  proposal_id: string;
  title: string;
  content: string;
  order_num: number;
  created_at: string;
  updated_at: string;
}

export interface Document {
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
