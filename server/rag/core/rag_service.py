#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG核心服务
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from .knowledge_scanner import KnowledgeScanner, DocumentInfo
from .qwen_vector_store import QwenVectorStore
from .rag_retriever import RAGRetriever, RerankedResult

logger = logging.getLogger(__name__)


class RAGCoreService:
    """RAG核心服务"""
    
    def __init__(self, 
                 knowledge_source_dir: str, 
                 data_dir: str,
                 embedding_model_path: str = None,
                 rerank_model_path: str = None,
                 device: str = None,
                 chunk_size: int = 512,
                 chunk_overlap: int = 50):
        """
        初始化RAG核心服务
        
        Args:
            knowledge_source_dir: 知识源目录
            data_dir: 数据目录
            embedding_model_path: 嵌入模型路径
            rerank_model_path: 重排序模型路径
            device: 计算设备
            chunk_size: 文档分块大小
            chunk_overlap: 分块重叠大小
        """
        self.knowledge_source_dir = knowledge_source_dir
        self.data_dir = data_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 初始化组件
        self.scanner = KnowledgeScanner(
            knowledge_source_dir, 
            data_dir,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.vector_store = QwenVectorStore(
            data_dir, 
            embedding_model_path=embedding_model_path,
            device=device
        )
        self.retriever = RAGRetriever(
            self.vector_store,
            rerank_model_path=rerank_model_path,
            device=device
        )
        
        self.is_initialized = False
        
        logger.info("RAG核心服务初始化完成")
    
    def initialize(self) -> bool:
        """
        初始化RAG系统
        - 扫描知识库文件
        - 加载/构建向量索引
        - 处理新文件
        
        Returns:
            是否初始化成功
        """
        try:
            logger.info("开始初始化RAG系统...")
            
            # 1. 尝试加载已有索引
            index_loaded = self.vector_store.load_index()
            
            # 2. 检查是否有文件变化（快速检查）
            if not self.scanner.has_changes():
                if index_loaded:
                    logger.info("知识库无变化，跳过文件扫描和处理")
                    self.is_initialized = True
                    return True
                else:
                    logger.info("首次运行，需要扫描和处理文件")
            else:
                logger.info("检测到知识库变化，开始扫描文件")
            
            # 3. 扫描新文件和修改的文件
            new_files = self.scanner.scan_for_new_files()
            
            # 4. 处理需要更新的文件
            if new_files:
                logger.info(f"发现 {len(new_files)} 个需要处理的文件")
                processed_count = self._process_new_files(new_files)
                logger.info(f"成功处理 {processed_count} 个文件")
                
                # 保存更新后的索引
                self.vector_store.save_index()
            elif not index_loaded:
                logger.warning("没有找到已有索引，且无新文件可处理")
                logger.warning("RAG系统将在空索引状态下运行")
            else:
                logger.info("向量索引已加载，无新文件需要处理")
            
            self.is_initialized = True
            logger.info("RAG系统初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"RAG系统初始化失败: {e}")
            return False
    
    def _process_new_files(self, new_files: List[DocumentInfo]) -> int:
        """处理新文件"""
        documents = []
        processed_count = 0
        
        for doc_info in new_files:
            try:
                # 提取文档内容
                content = self.scanner.extract_document_content(doc_info)
                if content.strip():
                    documents.append((content, doc_info.file_name))
                    logger.info(f"提取文档内容: {doc_info.file_name} ({len(content)} 字符)")
                else:
                    logger.warning(f"文档内容为空: {doc_info.file_name}")
                    continue
                    
            except Exception as e:
                logger.error(f"处理文档失败 {doc_info.file_name}: {e}")
                continue
        
        # 批量添加到向量存储
        if documents:
            try:
                chunks_count = self.vector_store.add_documents(documents)
                
                # 标记文件为已处理
                for i, doc_info in enumerate(new_files):
                    if i < len(documents):
                        # 估算这个文件的chunk数量
                        file_chunks = chunks_count // len(documents)  # 平均分配
                        self.scanner.mark_as_processed(doc_info.file_path, file_chunks)
                        processed_count += 1
                
            except Exception as e:
                logger.error(f"向量化文档失败: {e}")
        
        return processed_count
    
    def search(self, 
               query: str, 
               top_k: int = 5, 
               use_rerank: bool = True) -> List[RerankedResult]:
        """
        执行RAG搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            use_rerank: 是否使用重排序
            
        Returns:
            搜索结果列表
        """
        if not self.is_initialized:
            logger.warning("RAG系统未初始化")
            return []
        
        return self.retriever.search(query, top_k, use_rerank)
    
    def get_context_for_query(self, 
                             query: str, 
                             top_k: int = 3, 
                             use_rerank: bool = True) -> str:
        """
        为查询生成上下文
        
        Args:
            query: 查询文本
            top_k: 使用的文档块数量
            use_rerank: 是否使用重排序
            
        Returns:
            格式化的上下文字符串
        """
        if not self.is_initialized:
            logger.warning("RAG系统未初始化")
            return ""
        
        return self.retriever.get_context_for_query(query, top_k, use_rerank)
    
    def force_rebuild_index(self):
        """强制重建索引"""
        logger.info("开始强制重建向量索引...")
        
        # 清空现有索引
        self.vector_store.clear()
        
        # 重新扫描所有文件
        all_files = []
        knowledge_dir = Path(self.knowledge_source_dir)
        
        if knowledge_dir.exists():
            for file_path in knowledge_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in {'.pdf', '.md', '.txt'}:
                    stat = file_path.stat()
                    doc_info = DocumentInfo(
                        file_path=str(file_path),
                        file_name=file_path.name,
                        file_hash="",  # 重建时不需要检查哈希
                        file_size=stat.st_size,
                        modification_time=stat.st_mtime,
                        document_type=file_path.suffix.lower()[1:]
                    )
                    all_files.append(doc_info)
        
        # 处理所有文件
        if all_files:
            processed_count = self._process_new_files(all_files)
            self.vector_store.save_index()
            logger.info(f"索引重建完成，处理了 {processed_count} 个文件")
        else:
            logger.warning("没有找到可处理的文件")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        scanner_stats = self.scanner.get_processed_stats()
        vector_stats = self.vector_store.get_stats()
        
        return {
            'knowledge_base': scanner_stats,
            'vector_store': vector_stats,
            'is_initialized': self.is_initialized,
            'rerank_enabled': self.retriever.rerank_enabled
        }
    
    def print_debug_info(self, query: str, results: List[RerankedResult]):
        """打印调试信息"""
        self.retriever.print_debug_info(query, results)
