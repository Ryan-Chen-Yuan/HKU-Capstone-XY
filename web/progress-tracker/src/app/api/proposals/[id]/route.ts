import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';

// 获取单个Proposal
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const proposalId = params.id;
    const db = await getDb();
    
    const proposal = await db.get(`
      SELECT p.*, pr.name as project_name 
      FROM Proposals p
      LEFT JOIN Projects pr ON p.project_id = pr.id
      WHERE p.id = ?
    `, [proposalId]);
    
    if (!proposal) {
      return NextResponse.json({ 
        success: false, 
        message: 'Proposal不存在' 
      }, { status: 404 });
    }
    
    // 获取Proposal章节
    const sections = await db.all(
      'SELECT * FROM ProposalSections WHERE proposal_id = ? ORDER BY order_num',
      [proposalId]
    );
    
    // 获取相关文档
    const documents = await db.all(
      'SELECT * FROM Documents WHERE proposal_id = ?',
      [proposalId]
    );
    
    return NextResponse.json({ 
      success: true, 
      proposal,
      sections,
      documents
    });
  } catch (error) {
    console.error('获取Proposal信息错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取Proposal信息失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 更新Proposal
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const proposalId = params.id;
    const { title } = await request.json();
    
    if (!title) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
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
    
    // 更新Proposal
    await db.run(
      'UPDATE Proposals SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [title, proposalId]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: 'Proposal更新成功' 
    });
  } catch (error) {
    console.error('更新Proposal错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '更新Proposal失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 删除Proposal
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const proposalId = params.id;
    const db = await getDb();
    
    // 检查Proposal是否存在
    const existingProposal = await db.get('SELECT * FROM Proposals WHERE id = ?', [proposalId]);
    if (!existingProposal) {
      return NextResponse.json({ 
        success: false, 
        message: 'Proposal不存在' 
      }, { status: 404 });
    }
    
    // 开始事务
    await db.run('BEGIN TRANSACTION');
    
    try {
      // 删除Proposal章节
      await db.run('DELETE FROM ProposalSections WHERE proposal_id = ?', [proposalId]);
      
      // 删除相关文档
      await db.run('DELETE FROM Documents WHERE proposal_id = ?', [proposalId]);
      
      // 删除Proposal
      await db.run('DELETE FROM Proposals WHERE id = ?', [proposalId]);
      
      // 提交事务
      await db.run('COMMIT');
      
      return NextResponse.json({ 
        success: true, 
        message: 'Proposal删除成功' 
      });
    } catch (error) {
      // 回滚事务
      await db.run('ROLLBACK');
      throw error;
    }
  } catch (error) {
    console.error('删除Proposal错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '删除Proposal失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
