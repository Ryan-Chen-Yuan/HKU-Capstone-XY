import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';

// 获取单个任务
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const taskId = params.id;
    const db = await getDb();
    
    const task = await db.get(`
      SELECT t.*, u.name as user_name, m.title as milestone_title 
      FROM Tasks t
      LEFT JOIN Users u ON t.user_id = u.id
      LEFT JOIN Milestones m ON t.milestone_id = m.id
      WHERE t.id = ?
    `, [taskId]);
    
    if (!task) {
      return NextResponse.json({ 
        success: false, 
        message: '任务不存在' 
      }, { status: 404 });
    }
    
    return NextResponse.json({ 
      success: true, 
      task
    });
  } catch (error) {
    console.error('获取任务信息错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取任务信息失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 更新任务
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const taskId = params.id;
    const { title, description, status, start_date, due_date, completed_date, progress, priority, user_id, milestone_id } = await request.json();
    
    if (!title || !status || !start_date || !due_date || !priority || !user_id) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    
    // 检查任务是否存在
    const existingTask = await db.get('SELECT * FROM Tasks WHERE id = ?', [taskId]);
    if (!existingTask) {
      return NextResponse.json({ 
        success: false, 
        message: '任务不存在' 
      }, { status: 404 });
    }
    
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
    
    // 更新任务
    await db.run(
      'UPDATE Tasks SET title = ?, description = ?, status = ?, start_date = ?, due_date = ?, completed_date = ?, progress = ?, priority = ?, user_id = ?, milestone_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [title, description || null, status, start_date, due_date, completed_date || null, progress || 0, priority, user_id, milestone_id || null, taskId]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: '任务更新成功' 
    });
  } catch (error) {
    console.error('更新任务错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '更新任务失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 删除任务
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const taskId = params.id;
    const db = await getDb();
    
    // 检查任务是否存在
    const existingTask = await db.get('SELECT * FROM Tasks WHERE id = ?', [taskId]);
    if (!existingTask) {
      return NextResponse.json({ 
        success: false, 
        message: '任务不存在' 
      }, { status: 404 });
    }
    
    // 删除任务
    await db.run('DELETE FROM Tasks WHERE id = ?', [taskId]);
    
    return NextResponse.json({ 
      success: true, 
      message: '任务删除成功' 
    });
  } catch (error) {
    console.error('删除任务错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '删除任务失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
