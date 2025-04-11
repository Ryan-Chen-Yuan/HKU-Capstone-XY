import { NextRequest, NextResponse } from 'next/server';
import { getDb, initDatabase } from '@/lib/db';
import bcrypt from 'bcryptjs';
import { v4 as uuidv4 } from 'uuid';

// 初始化数据库
export async function GET() {
  try {
    await initDatabase();
    
    // 检查是否已有管理员账号
    const db = await getDb();
    if (!db) {
      return NextResponse.json({ 
        success: false, 
        message: '数据库连接失败' 
      }, { status: 500 });
    }
    
    const adminUser = await db.get('SELECT * FROM Users WHERE role = ?', ['admin']);
    
    if (!adminUser) {
      // 创建默认管理员账号
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash('admin123', salt);
      const userId = uuidv4();
      
      await db.run(
        'INSERT INTO Users (id, username, password_hash, name, role) VALUES (?, ?, ?, ?, ?)',
        [userId, 'admin', hashedPassword, '管理员', 'admin']
      );
      
      return NextResponse.json({ 
        success: true, 
        message: '数据库初始化成功，已创建默认管理员账号',
        adminUsername: 'admin',
        adminPassword: 'admin123'
      });
    }
    
    return NextResponse.json({ 
      success: true, 
      message: '数据库初始化成功，管理员账号已存在' 
    });
  } catch (error) {
    console.error('数据库初始化错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '数据库初始化失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 创建新用户
export async function POST(request: NextRequest) {
  try {
    const { username, password, name, role, email } = await request.json();
    
    if (!username || !password || !name || !role) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    if (!db) {
      return NextResponse.json({ 
        success: false, 
        message: '数据库连接失败' 
      }, { status: 500 });
    }
    
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
      'INSERT INTO Users (id, username, password_hash, name, role, email) VALUES (?, ?, ?, ?, ?, ?)',
      [userId, username, hashedPassword, name, role, email || null]
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
