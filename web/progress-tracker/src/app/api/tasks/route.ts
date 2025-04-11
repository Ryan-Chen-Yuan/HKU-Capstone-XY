import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import { v4 as uuidv4 } from 'uuid';

// 获取所有任务
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const milestoneId = searchParams.get('milestone_id');
    const userId = searchParams.get('user_id');
    
    const db = await getDb();
    let tasks;
    
    if (milestoneId) {
      tasks = await db.all(`
        SELECT t.*, u.name as user_name 
        FROM Tasks t
        LEFT JOIN Users u ON t.user_id = u.id
        WHERE t.milestone_id = ?
        ORDER BY t.due_date
      `, [milestoneId]);
    } else if (userId) {
      tasks = await db.all(`
        SELECT t.*, m.title as milestone_title 
        FROM Tasks t
        LEFT JOIN Milestones m ON t.milestone_id = m.id
        WHERE t.user_id = ?
        ORDER BY t.due_date
      `, [userId]);
    } else {
      tasks = await db.all(`
        SELECT t.*, u.name as user_name, m.title as milestone_title 
        FROM Tasks t
        LEFT JOIN Users u ON t.user_id = u.id
        LEFT JOIN Milestones m ON t.milestone_id = m.id
        ORDER BY t.due_date
      `);
    }
    
    return NextResponse.json({ 
      success: true, 
      tasks 
    });
  } catch (error) {
    console.error('获取任务列表错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取任务列表失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 创建新任务
export async function POST(request: NextRequest) {
  try {
    const { title, description, status, start_date, due_date, completed_date, progress, priority, user_id, milestone_id } = await request.json();
    
    if (!title || !status || !start_date || !due_date || !priority || !user_id) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    
    // 检查用户是否存在
    const existingUser = await db.get('SELECT * FROM Users WHERE id = ?', [user_id]);
    if (!existingUser) {
      return NextResponse.json({ 
        success: false, 
        message: '用户不存在' 
      }, { status: 404 });
    }
    
    // 如果提供了里程碑ID，检查里程碑是否存在
    if (milestone_id) {
      const existingMilestone = await db.get('SELECT * FROM Milestones WHERE id = ?', [milestone_id]);
      if (!existingMilestone) {
        return NextResponse.json({ 
          success: false, 
          message: '里程碑不存在' 
        }, { status: 404 });
      }
    }
    
    const taskId = uuidv4();
    
    await db.run(
      'INSERT INTO Tasks (id, title, description, status, start_date, due_date, completed_date, progress, priority, user_id, milestone_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [taskId, title, description || null, status, start_date, due_date, completed_date || null, progress || 0, priority, user_id, milestone_id || null]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: '任务创建成功', 
      taskId 
    });
  } catch (error) {
    console.error('创建任务错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '创建任务失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
