import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import bcrypt from 'bcryptjs';
import { v4 as uuidv4 } from 'uuid';

// 获取所有用户
export async function GET() {
  try {
    const db = await getDb();
    const users = await db.all('SELECT id, username, name, role, email, avatar, created_at, updated_at FROM Users');
    
    return NextResponse.json({ 
      success: true, 
      users 
    });
  } catch (error) {
    console.error('获取用户列表错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取用户列表失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 创建新用户
export async function POST(request: NextRequest) {
  try {
    const { username, password, name, role, email, avatar } = await request.json();
    
    if (!username || !password || !name || !role) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    
    // 检查用户名是否已存在
    const existingUser = await db.get('SELECT * FROM Users WHERE username = ?', [username]);
    if (existingUser) {
      return NextResponse.json({ 
        success: false, 
        message: '用户名已存在' 
      }, { status: 400 });
    }
    
    // 加密密码
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);
    
    // 创建用户
    const userId = uuidv4();
    await db.run(
      'INSERT INTO Users (id, username, password_hash, name, role, email, avatar) VALUES (?, ?, ?, ?, ?, ?, ?)',
      [userId, username, hashedPassword, name, role, email || null, avatar || null]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: '用户创建成功', 
      userId 
    });
  } catch (error) {
    console.error('创建用户错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '创建用户失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
