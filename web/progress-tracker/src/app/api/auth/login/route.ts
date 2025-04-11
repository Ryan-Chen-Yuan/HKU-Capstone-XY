import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

// 用户登录
export async function POST(request: NextRequest) {
  try {
    const { username, password } = await request.json();
    
    if (!username || !password) {
      return NextResponse.json({ 
        success: false, 
        message: '用户名和密码不能为空' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    
    // 查询用户
    if (!db) {
      return NextResponse.json({ 
        success: false, 
        message: '数据库连接失败' 
      }, { status: 500 });
    }
    
    const user = await db.get('SELECT * FROM Users WHERE username = ?', [username]);
    if (!user) {
      return NextResponse.json({ 
        success: false, 
        message: '用户名或密码错误' 
      }, { status: 401 });
    }
    
    // 验证密码
    const isPasswordValid = await bcrypt.compare(password, user.password_hash);
    if (!isPasswordValid) {
      return NextResponse.json({ 
        success: false, 
        message: '用户名或密码错误' 
      }, { status: 401 });
    }
    
    // 生成JWT令牌
    const token = jwt.sign(
      { 
        id: user.id,
        username: user.username,
        role: user.role
      },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '30d' }
    );
    
    // 返回用户信息和令牌
    return NextResponse.json({
      success: true,
      message: '登录成功',
      user: {
        id: user.id,
        username: user.username,
        name: user.name,
        role: user.role,
        email: user.email
      },
      token
    });
  } catch (error) {
    console.error('登录错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '登录失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
