# 毕设项目进度展示网站升级

## 项目概述

本项目是对现有毕设项目进度展示网站的升级，主要添加了后台管理系统、用户认证功能、账号管理功能，并采用苹果风格重新设计了UI。

## 主要功能

- **后台管理系统**：允许用户修改所有板块的信息
- **用户认证**：实现用户登录和权限控制
- **账号管理**：为每个组员分配账号，管理用户权限
- **苹果风格UI**：采用简洁、明亮、优雅的设计风格

## 技术栈

- **前端框架**：Next.js 15.1.4
- **样式框架**：Tailwind CSS
- **编程语言**：TypeScript
- **数据库**：SQLite (Cloudflare D1兼容)
- **认证**：JWT (JSON Web Tokens)

## 快速开始

### 安装依赖

```bash
cd progress-tracker
npm install
```·

### 开发环境运行

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 启动生产服务器

```bash
npm run start
```

## 系统初始化

首次使用系统时，需要初始化数据库：
1. 访问登录页面：`/login`
2. 点击"初始化数据库"按钮
3. 使用默认管理员账号登录（用户名：admin，密码：admin123）

## 文档

详细的使用说明和技术文档请参考：
- [用户手册](./user_manual.md)
- [管理员指南](./admin_guide.md)

## 项目结构

```
progress-tracker/
├── src/                   # 源代码目录
│   ├── app/              # 页面组件
│   │   ├── page.tsx      # 首页
│   │   ├── login/        # 登录页面
│   │   ├── admin/        # 管理后台
│   │   ├── members/      # 组员进度页面
│   │   ├── progress/     # 项目进度页面
│   │   ├── proposal/     # 项目设计页面
│   │   └── about/        # 关于页面
│   ├── components/       # 可复用组件
│   │   ├── ui/           # UI组件库
│   │   └── admin/        # 管理后台组件
│   ├── lib/              # 工具函数和数据
│   │   ├── db/           # 数据库相关
│   │   ├── auth.ts       # 认证相关
│   │   └── middleware.ts # 中间件
│   └── hooks/            # 自定义钩子
├── public/               # 静态资源
└── package.json          # 项目依赖
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT
