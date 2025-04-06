import { NextRequest, NextResponse } from 'next/server';
import { getToken } from 'next-auth/jwt';
import { NextMiddleware } from 'next/server';

// JWT认证中间件
export async function withAuth(
  request: NextRequest,
  handler: NextMiddleware
) {
  try {
    // 排除不需要认证的路由
    const publicPaths = ['/api/auth/login', '/api/auth/init'];
    const path = request.nextUrl.pathname;
    
    if (publicPaths.includes(path)) {
      return handler(request);
    }
    
    // 验证JWT令牌
    const token = await getToken({ 
      req: request, 
      secret: process.env.NEXTAUTH_SECRET || 'your-secret-key' 
    });
    
    if (!token) {
      return NextResponse.json({ 
        success: false, 
        message: '未授权访问' 
      }, { status: 401 });
    }
    
    // 将用户信息添加到请求中
    (request as any).user = {
      id: token.id,
      username: token.username,
      role: token.role
    };
    
    // 继续处理请求
    return handler(request);
  } catch (error) {
    console.error('认证中间件错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '认证失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 检查管理员权限
export function isAdmin(request: NextRequest) {
  const user = (request as any).user;
  return user && user.role === 'admin';
}

// 管理员权限中间件
export async function withAdminAuth(
  request: NextRequest,
  handler: NextMiddleware
) {
  try {
    // 先进行JWT认证
    const response = await withAuth(request, async (req) => {
      // 检查是否为管理员
      if (!isAdmin(req)) {
        return NextResponse.json({ 
          success: false, 
          message: '需要管理员权限' 
        }, { status: 403 });
      }
      
      // 继续处理请求
      return handler(req);
    });
    
    return response;
  } catch (error) {
    console.error('管理员权限中间件错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '权限验证失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
