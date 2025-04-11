import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import { v4 as uuidv4 } from 'uuid';

// 获取所有里程碑
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const projectId = searchParams.get('project_id');
    
    const db = await getDb();
    let milestones;
    
    if (projectId) {
      milestones = await db.all('SELECT * FROM Milestones WHERE project_id = ? ORDER BY due_date', [projectId]);
    } else {
      milestones = await db.all('SELECT * FROM Milestones ORDER BY due_date');
    }
    
    return NextResponse.json({ 
      success: true, 
      milestones 
    });
  } catch (error) {
    console.error('获取里程碑列表错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取里程碑列表失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 创建新里程碑
export async function POST(request: NextRequest) {
  try {
    const { project_id, title, description, due_date, status, progress } = await request.json();
    
    if (!project_id || !title || !due_date || !status) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    
    // 检查项目是否存在
    const existingProject = await db.get('SELECT * FROM Projects WHERE id = ?', [project_id]);
    if (!existingProject) {
      return NextResponse.json({ 
        success: false, 
        message: '项目不存在' 
      }, { status: 404 });
    }
    
    const milestoneId = uuidv4();
    
    await db.run(
      'INSERT INTO Milestones (id, project_id, title, description, due_date, status, progress) VALUES (?, ?, ?, ?, ?, ?, ?)',
      [milestoneId, project_id, title, description || null, due_date, status, progress || 0]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: '里程碑创建成功', 
      milestoneId 
    });
  } catch (error) {
    console.error('创建里程碑错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '创建里程碑失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
