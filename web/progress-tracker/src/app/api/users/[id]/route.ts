import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import bcrypt from 'bcryptjs';

// 获取单个用户
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const userId = params.id;
    const db = await getDb();
    
    const user = await db.get(
      'SELECT id, username, name, role, email, avatar, created_at, updated_at FROM Users WHERE id = ?', 
      [userId]
    );
    
    if (!user) {
      return NextResponse.json({ 
        success: false, 
        message: '用户不存在' 
      }, { status: 404 });
    }
    
    return NextResponse.json({ 
      success: true, 
      user 
    });
  } catch (error) {
    console.error('获取用户信息错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取用户信息失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 更新用户
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const userId = params.id;
    const { name, role, email, avatar, password } = await request.json();
    
    const db = await getDb();
    
    // 检查用户是否存在
    const existingUser = await db.get('SELECT * FROM Users WHERE id = ?', [userId]);
    if (!existingUser) {
      return NextResponse.json({ 
        success: false, 
        message: '用户不存在' 
      }, { status: 404 });
    }
    
    // 构建更新语句
    let updateQuery = 'UPDATE Users SET name = ?, role = ?, email = ?, avatar = ?, updated_at = CURRENT_TIMESTAMP';
    const params = [name, role, email || null, avatar || null];
    
    // 如果提供了新密码，则更新密码
    if (password) {
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash(password, salt);
      updateQuery += ', password_hash = ?';
      params.push(hashedPassword);
    }
    
    updateQuery += ' WHERE id = ?';
    params.push(userId);
    
    // 执行更新
    await db.run(updateQuery, params);
    
    return NextResponse.json({ 
      success: true, 
      message: '用户更新成功' 
    });
  } catch (error) {
    console.error('更新用户错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '更新用户失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 删除用户
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const userId = params.id;
    const db = await getDb();
    
    // 检查用户是否存在
    const existingUser = await db.get('SELECT * FROM Users WHERE id = ?', [userId]);
    if (!existingUser) {
      return NextResponse.json({ 
        success: false, 
        message: '用户不存在' 
      }, { status: 404 });
    }
    
    // 删除用户
    await db.run('DELETE FROM Users WHERE id = ?', [userId]);
    
    return NextResponse.json({ 
      success: true, 
      message: '用户删除成功' 
    });
  } catch (error) {
    console.error('删除用户错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '删除用户失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
