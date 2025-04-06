import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';

// 获取单个文档
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = params.id;
    const document = await db.getDocument(id);
    
    if (!document) {
      return NextResponse.json({ success: false, message: '文档不存在' }, { status: 404 });
    }
    
    return NextResponse.json({ success: true, document });
  } catch (error) {
    console.error('获取文档错误:', error);
    return NextResponse.json({ success: false, message: '获取文档失败' }, { status: 500 });
  }
}

// 更新文档
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = params.id;
    const data = await request.json();
    
    const updatedDocument = await db.updateDocument(id, data);
    
    if (!updatedDocument) {
      return NextResponse.json({ success: false, message: '文档不存在' }, { status: 404 });
    }
    
    return NextResponse.json({ success: true, document: updatedDocument });
  } catch (error) {
    console.error('更新文档错误:', error);
    return NextResponse.json({ success: false, message: '更新文档失败' }, { status: 500 });
  }
}

// 删除文档
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = params.id;
    const success = await db.deleteDocument(id);
    
    if (!success) {
      return NextResponse.json({ success: false, message: '文档不存在' }, { status: 404 });
    }
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('删除文档错误:', error);
    return NextResponse.json({ success: false, message: '删除文档失败' }, { status: 500 });
  }
}
