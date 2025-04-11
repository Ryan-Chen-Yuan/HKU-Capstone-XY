import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';

// 获取单个项目
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const projectId = params.id;
    const db = await getDb();
    
    const project = await db.get('SELECT * FROM Projects WHERE id = ?', [projectId]);
    
    if (!project) {
      return NextResponse.json({ 
        success: false, 
        message: '项目不存在' 
      }, { status: 404 });
    }
    
    // 获取项目相关的里程碑
    const milestones = await db.all('SELECT * FROM Milestones WHERE project_id = ?', [projectId]);
    
    // 获取项目相关的任务
    const tasks = await db.all(`
      SELECT t.*, u.name as user_name 
      FROM Tasks t
      LEFT JOIN Users u ON t.user_id = u.id
      WHERE t.milestone_id IN (SELECT id FROM Milestones WHERE project_id = ?)
    `, [projectId]);
    
    return NextResponse.json({ 
      success: true, 
      project,
      milestones,
      tasks
    });
  } catch (error) {
    console.error('获取项目信息错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取项目信息失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 更新项目
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const projectId = params.id;
    const { name, description, start_date, end_date, progress } = await request.json();
    
    if (!name || !start_date || !end_date) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    
    // 检查项目是否存在
    const existingProject = await db.get('SELECT * FROM Projects WHERE id = ?', [projectId]);
    if (!existingProject) {
      return NextResponse.json({ 
        success: false, 
        message: '项目不存在' 
      }, { status: 404 });
    }
    
    // 更新项目
    await db.run(
      'UPDATE Projects SET name = ?, description = ?, start_date = ?, end_date = ?, progress = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [name, description || null, start_date, end_date, progress || 0, projectId]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: '项目更新成功' 
    });
  } catch (error) {
    console.error('更新项目错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '更新项目失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 删除项目
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const projectId = params.id;
    const db = await getDb();
    
    // 检查项目是否存在
    const existingProject = await db.get('SELECT * FROM Projects WHERE id = ?', [projectId]);
    if (!existingProject) {
      return NextResponse.json({ 
        success: false, 
        message: '项目不存在' 
      }, { status: 404 });
    }
    
    // 开始事务
    await db.run('BEGIN TRANSACTION');
    
    try {
      // 删除项目相关的任务
      await db.run(`
        DELETE FROM Tasks 
        WHERE milestone_id IN (SELECT id FROM Milestones WHERE project_id = ?)
      `, [projectId]);
      
      // 删除项目相关的里程碑
      await db.run('DELETE FROM Milestones WHERE project_id = ?', [projectId]);
      
      // 删除项目相关的Proposal章节
      await db.run(`
        DELETE FROM ProposalSections 
        WHERE proposal_id IN (SELECT id FROM Proposals WHERE project_id = ?)
      `, [projectId]);
      
      // 删除项目相关的文档
      await db.run(`
        DELETE FROM Documents 
        WHERE proposal_id IN (SELECT id FROM Proposals WHERE project_id = ?)
      `, [projectId]);
      
      // 删除项目相关的Proposal
      await db.run('DELETE FROM Proposals WHERE project_id = ?', [projectId]);
      
      // 删除项目
      await db.run('DELETE FROM Projects WHERE id = ?', [projectId]);
      
      // 提交事务
      await db.run('COMMIT');
      
      return NextResponse.json({ 
        success: true, 
        message: '项目删除成功' 
      });
    } catch (error) {
      // 回滚事务
      await db.run('ROLLBACK');
      throw error;
    }
  } catch (error) {
    console.error('删除项目错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '删除项目失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
