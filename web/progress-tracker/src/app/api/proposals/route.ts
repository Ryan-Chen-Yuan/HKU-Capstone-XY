import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import { v4 as uuidv4 } from 'uuid';

// 获取所有Proposal
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const projectId = searchParams.get('project_id');
    
    const db = await getDb();
    let proposals;
    
    if (projectId) {
      proposals = await db.all('SELECT * FROM Proposals WHERE project_id = ?', [projectId]);
    } else {
      proposals = await db.all(`
        SELECT p.*, pr.name as project_name 
        FROM Proposals p
        LEFT JOIN Projects pr ON p.project_id = pr.id
      `);
    }
    
    return NextResponse.json({ 
      success: true, 
      proposals 
    });
  } catch (error) {
    console.error('获取Proposal列表错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取Proposal列表失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 创建新Proposal
export async function POST(request: NextRequest) {
  try {
    const { project_id, title } = await request.json();
    
    if (!project_id || !title) {
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
    
    const proposalId = uuidv4();
    
    await db.run(
      'INSERT INTO Proposals (id, project_id, title) VALUES (?, ?, ?)',
      [proposalId, project_id, title]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: 'Proposal创建成功', 
      proposalId 
    });
  } catch (error) {
    console.error('创建Proposal错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '创建Proposal失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
