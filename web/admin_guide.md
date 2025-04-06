# 毕设项目进度展示网站管理员指南

## 1. 系统架构概述

毕设项目进度展示网站采用现代化的技术架构，包括：

- **前端**：Next.js 15.1.4 + Tailwind CSS + TypeScript
- **后端**：Next.js API Routes
- **数据库**：SQLite (Cloudflare D1兼容)
- **认证**：JWT (JSON Web Tokens)
- **部署**：Node.js生产服务器

系统采用了模块化设计，主要包括以下模块：
- 用户认证模块
- 数据管理模块
- 前端展示模块
- 后台管理模块

## 2. 系统初始化

### 2.1 数据库初始化

系统首次使用时需要初始化数据库，步骤如下：

1. 访问登录页面：`/login`
2. 系统会自动检测数据库是否已初始化
3. 如未初始化，点击"初始化数据库"按钮
4. 初始化过程会创建所有必要的数据表，并添加默认数据：
   - 默认管理员账号
   - 示例团队成员
   - 示例项目数据
   - 示例里程碑和任务
   - 示例Proposal内容

### 2.2 默认管理员账号

初始化后的默认管理员账号：
- 用户名：admin
- 密码：admin123

**重要**：出于安全考虑，请在首次登录后立即修改默认密码。

## 3. 用户管理

### 3.1 用户角色

系统支持以下用户角色：

1. **管理员(admin)**：拥有系统的完全访问权限
2. **团队成员(member)**：可以管理自己的任务和进度
3. **访客(guest)**：只能查看公开页面，无需账号

### 3.2 创建用户

1. 登录管理后台
2. 进入"用户管理"页面
3. 点击"创建用户"按钮
4. 填写用户信息：
   - 用户名（必填，唯一）
   - 密码（必填，建议8位以上）
   - 姓名（必填）
   - 角色（必填，选择admin或member）
   - 邮箱（可选）
   - 头像URL（可选）
5. 点击"保存"按钮

### 3.3 用户权限管理

不同角色的用户拥有不同的权限：

- **管理员**：
  - 可以访问所有页面和功能
  - 可以创建、编辑和删除所有数据
  - 可以管理用户账号

- **团队成员**：
  - 可以访问所有公开页面
  - 可以查看和编辑自己的任务
  - 不能访问用户管理功能
  - 不能编辑其他用户的任务

## 4. 数据管理

### 4.1 项目管理

系统设计为主要管理一个主项目，但支持扩展为多项目。项目信息包括：
- 项目名称
- 项目描述
- 开始日期
- 结束日期
- 项目进度

修改项目信息：
1. 登录管理后台
2. 进入"项目管理"页面
3. 点击"编辑"按钮
4. 修改项目信息
5. 点击"保存"按钮

### 4.2 里程碑管理

里程碑代表项目的重要阶段，信息包括：
- 标题
- 描述
- 开始日期
- 截止日期
- 状态（待处理、进行中、已完成、已延期）
- 完成进度

添加里程碑：
1. 登录管理后台
2. 进入"里程碑管理"页面
3. 点击"创建里程碑"按钮
4. 填写里程碑信息
5. 点击"保存"按钮

### 4.3 任务管理

任务是分配给团队成员的工作项，信息包括：
- 标题
- 描述
- 状态（待处理、进行中、已完成、已延期）
- 开始日期
- 截止日期
- 完成日期
- 完成进度
- 优先级（高、中、低）
- 负责人
- 关联的里程碑

添加任务：
1. 登录管理后台
2. 进入"任务管理"页面
3. 点击"创建任务"按钮
4. 填写任务信息
5. 点击"保存"按钮

### 4.4 Proposal管理

Proposal是项目设计方案，由多个章节组成，信息包括：
- 标题
- 关联的项目

章节信息包括：
- 标题
- 内容
- 排序号

编辑Proposal章节：
1. 登录管理后台
2. 进入"Proposal管理"页面
3. 点击"查看章节"按钮
4. 编辑现有章节或添加新章节
5. 点击"保存"按钮

### 4.5 文档管理

文档是与项目相关的文件，信息包括：
- 标题
- 描述
- 文件URL
- 文件类型
- 上传日期
- 关联的Proposal

上传文档：
1. 登录管理后台
2. 进入"Proposal管理"页面
3. 点击"查看章节"按钮
4. 在"相关文档"部分，点击"上传文档"按钮
5. 填写文档信息并选择文件
6. 点击"上传"按钮

## 5. 系统维护

### 5.1 数据备份

建议定期备份数据库，以防数据丢失：
1. 导出数据库文件
2. 将备份文件存储在安全位置

### 5.2 系统更新

系统更新步骤：
1. 备份当前系统和数据
2. 部署新版本代码
3. 运行必要的数据迁移脚本
4. 测试系统功能

### 5.3 性能优化

如果系统运行变慢，可以尝试以下优化措施：
- 清理不必要的数据
- 优化数据库查询
- 增加服务器资源

### 5.4 安全维护

为保障系统安全，建议：
- 定期更改管理员密码
- 定期检查用户账号活动
- 确保服务器安全更新
- 监控异常登录活动

## 6. 故障排除

### 6.1 常见问题及解决方案

#### 登录问题
- **问题**：无法登录系统
- **解决方案**：
  - 确认用户名和密码正确
  - 检查数据库连接
  - 重置用户密码

#### 数据显示问题
- **问题**：数据不显示或显示错误
- **解决方案**：
  - 刷新页面
  - 清除浏览器缓存
  - 检查数据库记录

#### API错误
- **问题**：API请求返回错误
- **解决方案**：
  - 检查API路由是否正确
  - 检查请求参数
  - 查看服务器日志

### 6.2 日志查看

系统日志可以帮助诊断问题：
- 前端控制台日志：在浏览器开发者工具中查看
- 服务器日志：在服务器端查看Node.js日志

## 7. 系统扩展

### 7.1 添加新功能

如需添加新功能，建议遵循以下步骤：
1. 分析需求
2. 设计功能
3. 实现后端API
4. 实现前端界面
5. 测试功能
6. 部署更新

### 7.2 自定义界面

如需自定义界面，可以修改以下文件：
- `/src/components/ui/ui-components.tsx`：UI组件库
- `/src/app/page.tsx`等页面文件：页面布局和内容
- `/src/app/globals.css`：全局样式

### 7.3 集成第三方服务

系统支持集成第三方服务，如：
- 文件存储服务
- 邮件通知服务
- 分析工具

集成步骤：
1. 安装必要的依赖包
2. 配置API密钥和连接信息
3. 实现集成代码
4. 测试功能

## 8. 技术支持

如有任何技术问题，请联系系统开发团队：
- 邮箱：support@example.com
- 电话：123-456-7890

## 9. 附录

### 9.1 API文档

系统提供以下API端点：

#### 认证API
- `POST /api/auth/login`：用户登录
- `POST /api/auth/init`：初始化数据库

#### 用户API
- `GET /api/users`：获取所有用户
- `GET /api/users/:id`：获取单个用户
- `POST /api/users`：创建用户
- `PUT /api/users/:id`：更新用户
- `DELETE /api/users/:id`：删除用户

#### 项目API
- `GET /api/projects`：获取所有项目
- `GET /api/projects/:id`：获取单个项目
- `POST /api/projects`：创建项目
- `PUT /api/projects/:id`：更新项目
- `DELETE /api/projects/:id`：删除项目

#### 里程碑API
- `GET /api/milestones`：获取所有里程碑
- `GET /api/milestones/:id`：获取单个里程碑
- `POST /api/milestones`：创建里程碑
- `PUT /api/milestones/:id`：更新里程碑
- `DELETE /api/milestones/:id`：删除里程碑

#### 任务API
- `GET /api/tasks`：获取所有任务
- `GET /api/tasks/:id`：获取单个任务
- `POST /api/tasks`：创建任务
- `PUT /api/tasks/:id`：更新任务
- `DELETE /api/tasks/:id`：删除任务

#### Proposal API
- `GET /api/proposals`：获取所有Proposal
- `GET /api/proposals/:id`：获取单个Proposal
- `POST /api/proposals`：创建Proposal
- `PUT /api/proposals/:id`：更新Proposal
- `DELETE /api/proposals/:id`：删除Proposal

#### Proposal章节API
- `GET /api/proposal-sections`：获取所有章节
- `GET /api/proposal-sections/:id`：获取单个章节
- `POST /api/proposal-sections`：创建章节
- `PUT /api/proposal-sections/:id`：更新章节
- `DELETE /api/proposal-sections/:id`：删除章节

#### 文档API
- `GET /api/documents`：获取所有文档
- `GET /api/documents/:id`：获取单个文档
- `POST /api/documents`：创建文档
- `PUT /api/documents/:id`：更新文档
- `DELETE /api/documents/:id`：删除文档

### 9.2 数据库结构

系统使用以下数据表：

#### 用户表 (Users)
```sql
CREATE TABLE Users (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  email TEXT UNIQUE,
  avatar TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 项目表 (Projects)
```sql
CREATE TABLE Projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  progress INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 里程碑表 (Milestones)
```sql
CREATE TABLE Milestones (
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
);
```

#### 任务表 (Tasks)
```sql
CREATE TABLE Tasks (
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
);
```

#### Proposal表 (Proposals)
```sql
CREATE TABLE Proposals (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  title TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES Projects(id)
);
```

#### Proposal章节表 (ProposalSections)
```sql
CREATE TABLE ProposalSections (
  id TEXT PRIMARY KEY,
  proposal_id TEXT NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  order_num INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (proposal_id) REFERENCES Proposals(id)
);
```

#### 文档表 (Documents)
```sql
CREATE TABLE Documents (
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
);
```
