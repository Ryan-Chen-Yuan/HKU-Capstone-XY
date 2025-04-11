import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { withAuth, isAdmin } from '@/lib/middleware';

// 定义需要管理员权限的路径
const adminPaths = [
  '/api/users',
  '/api/projects',
  '/api/milestones',
  '/api/tasks',
  '/api/proposals',
  '/api/proposal-sections',
  '/api/documents',
];

// 定义不需要认证的路径
const publicPaths = [
  '/api/auth/login',
  '/api/auth/init',
  '/login',
  '/',
];

// 中间件函数
export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // 公共路径不需要认证
  if (publicPaths.some(path => pathname.startsWith(path))) {
    return NextResponse.next();
  }
  
  // 管理员路径需要管理员权限
  if (adminPaths.some(path => pathname.startsWith(path))) {
    return withAuth(request, async (req) => {
      if (!isAdmin(req)) {
        return NextResponse.json({ 
          success: false, 
          message: '需要管理员权限' 
        }, { status: 403 });
      }
      return NextResponse.next();
    });
  }
  
  // 其他API路径需要普通认证
  if (pathname.startsWith('/api/')) {
    return withAuth(request, () => NextResponse.next());
  }
  
  // 其他路径直接通过
  return NextResponse.next();
}

// 配置匹配路径
export const config = {
  matcher: [
    '/api/:path*',
    '/admin/:path*',
  ],
};
