import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import { v4 as uuidv4 } from 'uuid';

// 获取所有项目
export async function GET() {
  try {
    const db = await getDb();
    const projects = await db.all('SELECT * FROM Projects');
    
    return NextResponse.json({ 
      success: true, 
      projects 
    });
  } catch (error) {
    console.error('获取项目列表错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取项目列表失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 创建新项目
export async function POST(request: NextRequest) {
  try {
    const { name, description, start_date, end_date, progress } = await request.json();
    
    if (!name || !start_date || !end_date) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    const projectId = uuidv4();
    
    await db.run(
      'INSERT INTO Projects (id, name, description, start_date, end_date, progress) VALUES (?, ?, ?, ?, ?, ?)',
      [projectId, name, description || null, start_date, end_date, progress || 0]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: '项目创建成功', 
      projectId 
    });
  } catch (error) {
    console.error('创建项目错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '创建项目失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
