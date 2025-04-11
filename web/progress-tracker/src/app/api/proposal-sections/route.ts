import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import { v4 as uuidv4 } from 'uuid';

// 获取所有Proposal章节
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const proposalId = searchParams.get('proposal_id');
    
    if (!proposalId) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少proposal_id参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    
    // 检查Proposal是否存在
    const existingProposal = await db.get('SELECT * FROM Proposals WHERE id = ?', [proposalId]);
    if (!existingProposal) {
      return NextResponse.json({ 
        success: false, 
        message: 'Proposal不存在' 
      }, { status: 404 });
    }
    
    const sections = await db.all(
      'SELECT * FROM ProposalSections WHERE proposal_id = ? ORDER BY order_num',
      [proposalId]
    );
    
    return NextResponse.json({ 
      success: true, 
      sections 
    });
  } catch (error) {
    console.error('获取Proposal章节列表错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取Proposal章节列表失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 创建新Proposal章节
export async function POST(request: NextRequest) {
  try {
    const { proposal_id, title, content, order_num } = await request.json();
    
    if (!proposal_id || !title || !content || order_num === undefined) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    
    // 检查Proposal是否存在
    const existingProposal = await db.get('SELECT * FROM Proposals WHERE id = ?', [proposal_id]);
    if (!existingProposal) {
      return NextResponse.json({ 
        success: false, 
        message: 'Proposal不存在' 
      }, { status: 404 });
    }
    
    const sectionId = uuidv4();
    
    await db.run(
      'INSERT INTO ProposalSections (id, proposal_id, title, content, order_num) VALUES (?, ?, ?, ?, ?)',
      [sectionId, proposal_id, title, content, order_num]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: 'Proposal章节创建成功', 
      sectionId 
    });
  } catch (error) {
    console.error('创建Proposal章节错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '创建Proposal章节失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
