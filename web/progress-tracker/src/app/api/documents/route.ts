import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import { v4 as uuidv4 } from 'uuid';

// 获取所有文档
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const proposalId = searchParams.get('proposal_id');
    
    const db = await getDb();
    let documents;
    
    if (proposalId) {
      documents = await db.all('SELECT * FROM Documents WHERE proposal_id = ?', [proposalId]);
    } else {
      documents = await db.all(`
        SELECT d.*, p.title as proposal_title 
        FROM Documents d
        LEFT JOIN Proposals p ON d.proposal_id = p.id
      `);
    }
    
    return NextResponse.json({ 
      success: true, 
      documents 
    });
  } catch (error) {
    console.error('获取文档列表错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '获取文档列表失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}

// 创建新文档
export async function POST(request: NextRequest) {
  try {
    const { title, description, file_url, file_type, upload_date, proposal_id } = await request.json();
    
    if (!title || !file_url || !file_type || !upload_date) {
      return NextResponse.json({ 
        success: false, 
        message: '缺少必要参数' 
      }, { status: 400 });
    }
    
    const db = await getDb();
    
    // 如果提供了proposal_id，检查Proposal是否存在
    if (proposal_id) {
      const existingProposal = await db.get('SELECT * FROM Proposals WHERE id = ?', [proposal_id]);
      if (!existingProposal) {
        return NextResponse.json({ 
          success: false, 
          message: 'Proposal不存在' 
        }, { status: 404 });
      }
    }
    
    const documentId = uuidv4();
    
    await db.run(
      'INSERT INTO Documents (id, title, description, file_url, file_type, upload_date, proposal_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
      [documentId, title, description || null, file_url, file_type, upload_date, proposal_id || null]
    );
    
    return NextResponse.json({ 
      success: true, 
      message: '文档创建成功', 
      documentId 
    });
  } catch (error) {
    console.error('创建文档错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: '创建文档失败', 
      error: (error as Error).message 
    }, { status: 500 });
  }
}
