import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';

// 获取单个里程碑
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const milestoneId = params.id;
    const db = await getDb();
    
    const milestone = await db.get('SELECT * FROM Milestones WHERE id = ?', [milestoneId]);
    
    if (!milestone) {
      return NextResponse.json({ 
        success: false, 
        message: '里程碑不存在' 
      }, { status: 404 });
    }
    
    // 获取里程碑相关的任务
    const tasks = await db.all(`
      SELECT t.*, u.name as user_name 
      FROM Tasks t
      LEFT JOIN Users u ON t.user_id = u.id
      WHERE t.milestone_id = ?
    `, [milestoneId]);
    
    return NextResponse.json({ 
      success: true, 
      milestone,
      tasks
    });
  } catch (error) {
    console.error('获取里程碑信息错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取里程碑信息失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 更新里程碑
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const milestoneId = params.id;
    const { title, description, due_date, status, progress } = await request.json();
    
    if (!title || !due_date || !status) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    
    // 检查里程碑是否存在
    const existingMilestone = await db.get('SELECT * FROM Milestones WHERE id = ?', [milestoneId]);
    if (!existingMilestone) {
      return NextResponse.json({ 
        success: false, 
        message: '里程碑不存在' 
      }, { status: 404 });
    }
    
    // 更新里程碑
    await db.run(
      'UPDATE Milestones SET title = ?, description = ?, due_date = ?, status = ?, progress = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [title, description || null, due_date, status, progress || 0, milestoneId]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: '里程碑更新成功' 
    });
  } catch (error) {
    console.error('更新里程碑错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '更新里程碑失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 删除里程碑
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const milestoneId = params.id;
    const db = await getDb();
    
    // 检查里程碑是否存在
    const existingMilestone = await db.get('SELECT * FROM Milestones WHERE id = ?', [milestoneId]);
    if (!existingMilestone) {
      return NextResponse.json({ 
        success: false, 
        message: '里程碑不存在' 
      }, { status: 404 });
    }
    
    // 开始事务
    await db.run('BEGIN TRANSACTION');
    
    try {
      // 删除里程碑相关的任务
      await db.run('DELETE FROM Tasks WHERE milestone_id = ?', [milestoneId]);
      
      // 删除里程碑
      await db.run('DELETE FROM Milestones WHERE id = ?', [milestoneId]);
      
      // 提交事务
      await db.run('COMMIT');
      
      return NextResponse.json({ 
        success: true, 
        message: '里程碑删除成功' 
      });
    } catch (error) {
      // 回滚事务
      await db.run('ROLLBACK');
      throw error;
    }
  } catch (error) {
    console.error('删除里程碑错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '删除里程碑失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
