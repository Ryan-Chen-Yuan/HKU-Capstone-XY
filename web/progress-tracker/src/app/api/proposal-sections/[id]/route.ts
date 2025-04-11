import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';

// 获取单个Proposal章节
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const sectionId = params.id;
    const db = await getDb();
    
    const section = await db.get('SELECT * FROM ProposalSections WHERE id = ?', [sectionId]);
    
    if (!section) {
      return NextResponse.json({ 
        success: false, 
        message: 'Proposal章节不存在' 
      }, { status: 404 });
    }
    
    return NextResponse.json({ 
      success: true, 
      section
    });
  } catch (error) {
    console.error('获取Proposal章节信息错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取Proposal章节信息失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 更新Proposal章节
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const sectionId = params.id;
    const { title, content, order_num } = await request.json();
    
    if (!title || !content || order_num === undefined) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    
    // 检查章节是否存在
    const existingSection = await db.get('SELECT * FROM ProposalSections WHERE id = ?', [sectionId]);
    if (!existingSection) {
      return NextResponse.json({ 
        success: false, 
        message: 'Proposal章节不存在' 
      }, { status: 404 });
    }
    
    // 更新章节
    await db.run(
      'UPDATE ProposalSections SET title = ?, content = ?, order_num = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [title, content, order_num, sectionId]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: 'Proposal章节更新成功' 
    });
  } catch (error) {
    console.error('更新Proposal章节错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '更新Proposal章节失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 删除Proposal章节
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const sectionId = params.id;
    const db = await getDb();
    
    // 检查章节是否存在
    const existingSection = await db.get('SELECT * FROM ProposalSections WHERE id = ?', [sectionId]);
    if (!existingSection) {
      return NextResponse.json({ 
        success: false, 
        message: 'Proposal章节不存在' 
      }, { status: 404 });
    }
    
    // 删除章节
    await db.run('DELETE FROM ProposalSections WHERE id = ?', [sectionId]);
    
    return NextResponse.json({ 
      success: true, 
      message: 'Proposal章节删除成功' 
    });
  } catch (error) {
    console.error('删除Proposal章节错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '删除Proposal章节失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
