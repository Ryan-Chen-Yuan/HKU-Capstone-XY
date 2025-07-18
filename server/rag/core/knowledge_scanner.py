#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知识库文件扫描器
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from datetime import datetime
from tqdm import tqdm

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


@dataclass
class DocumentInfo:
    """文档信息"""
    file_path: str
    file_name: str
    file_hash: str
    file_size: int
    modification_time: float
    document_type: str  # pdf, md, txt
    processed: bool = False
    chunks_count: int = 0


class KnowledgeScanner:
    """知识库文件扫描器"""
    
    def __init__(self, knowledge_source_dir: str, data_dir: str, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        初始化扫描器
        
        Args:
            knowledge_source_dir: 知识源目录
            data_dir: 数据目录 (存放索引文件)
            chunk_size: 文档分块大小
            chunk_overlap: 分块重叠大小
        """
        self.knowledge_source_dir = Path(knowledge_source_dir)
        self.data_dir = Path(data_dir)
        self.index_file = self.data_dir / "knowledge_index.json"
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 支持的文件类型
        self.supported_extensions = {'.pdf', '.md', '.txt'}
        
        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载已处理文件索引
        self.processed_files = self._load_index()
    
    def _load_index(self) -> Dict[str, DocumentInfo]:
        """加载已处理文件索引"""
        if not self.index_file.exists():
            return {}
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            index = {}
            for file_path, info in data.items():
                index[file_path] = DocumentInfo(**info)
            
            logger.info(f"加载已处理文件索引: {len(index)} 个文件")
            return index
            
        except Exception as e:
            logger.warning(f"加载文件索引失败: {e}")
            return {}
    
    def _save_index(self):
        """保存文件索引"""
        try:
            data = {}
            for file_path, doc_info in self.processed_files.items():
                data[file_path] = {
                    'file_path': doc_info.file_path,
                    'file_name': doc_info.file_name,
                    'file_hash': doc_info.file_hash,
                    'file_size': doc_info.file_size,
                    'modification_time': doc_info.modification_time,
                    'document_type': doc_info.document_type,
                    'processed': doc_info.processed,
                    'chunks_count': doc_info.chunks_count
                }
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.debug(f"保存文件索引: {len(data)} 个文件")
            
        except Exception as e:
            logger.error(f"保存文件索引失败: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希失败 {file_path}: {e}")
            return ""
    
    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """从PDF提取文本"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            logger.error(f"PDF文本提取失败 {file_path}: {e}")
            return ""
    
    def _extract_text_from_file(self, file_path: Path) -> str:
        """从文件提取文本内容"""
        try:
            if file_path.suffix.lower() == '.pdf':
                return self._extract_text_from_pdf(file_path)
            else:
                # txt, md 文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception as e:
            logger.error(f"文件文本提取失败 {file_path}: {e}")
            return ""
    
    def scan_for_new_files(self) -> List[DocumentInfo]:
        """
        扫描新文件和已修改的文件
        
        Returns:
            需要处理的文件列表
        """
        if not self.knowledge_source_dir.exists():
            logger.warning(f"知识源目录不存在: {self.knowledge_source_dir}")
            return []
        
        new_files = []
        current_files = set()
        
        # 收集所有支持的文件
        all_files = []
        for file_path in self.knowledge_source_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                all_files.append(file_path)
        
        print(f"📂 扫描 {len(all_files)} 个文件...")
        
        # 扫描所有支持的文件 - 添加进度条
        for file_path in tqdm(all_files, desc="扫描文件", unit="个"):
            current_files.add(str(file_path))
            
            # 获取文件信息
            stat = file_path.stat()
            file_hash = self._calculate_file_hash(file_path)
            
            doc_info = DocumentInfo(
                file_path=str(file_path),
                file_name=file_path.name,
                file_hash=file_hash,
                file_size=stat.st_size,
                modification_time=stat.st_mtime,
                document_type=file_path.suffix.lower()[1:]  # 去掉点号
            )
            
            # 检查是否需要处理
            key = str(file_path)
            if key not in self.processed_files:
                # 新文件
                logger.info(f"发现新文件: {file_path.name}")
                new_files.append(doc_info)
                self.processed_files[key] = doc_info
            elif (self.processed_files[key].file_hash != file_hash or 
                  self.processed_files[key].modification_time != stat.st_mtime):
                # 文件已修改
                logger.info(f"文件已修改: {file_path.name}")
                new_files.append(doc_info)
                self.processed_files[key] = doc_info
        
        # 清理已删除的文件
        removed_files = set(self.processed_files.keys()) - current_files
        for removed_file in removed_files:
            logger.info(f"文件已删除: {self.processed_files[removed_file].file_name}")
            del self.processed_files[removed_file]
        
        # 保存索引
        if new_files or removed_files:
            self._save_index()
        
        print(f"📋 扫描完成: {len(new_files)} 个新文件，{len(removed_files)} 个已删除")
        logger.info(f"扫描完成: 发现 {len(new_files)} 个需要处理的文件")
        return new_files
    
    def has_changes(self) -> bool:
        """
        检查是否有文件变化，无需重新处理的情况直接返回False
        
        Returns:
            True if there are changes that require processing
        """
        if not self.knowledge_source_dir.exists():
            return False
        
        current_files = {}
        
        # 快速扫描当前文件状态
        for file_path in self.knowledge_source_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                stat = file_path.stat()
                current_files[str(file_path)] = {
                    'mtime': stat.st_mtime,
                    'size': stat.st_size
                }
        
        # 比较文件数量
        if len(current_files) != len(self.processed_files):
            return True
        
        # 比较已知文件的修改时间和大小
        for file_path, current_info in current_files.items():
            if file_path not in self.processed_files:
                return True
            
            stored_info = self.processed_files[file_path]
            if (stored_info.modification_time != current_info['mtime'] or 
                stored_info.file_size != current_info['size']):
                return True
        
        return False
    
    def extract_document_content(self, doc_info: DocumentInfo) -> str:
        """提取文档内容"""
        return self._extract_text_from_file(Path(doc_info.file_path))
    
    def mark_as_processed(self, file_path: str, chunks_count: int):
        """标记文件为已处理"""
        if file_path in self.processed_files:
            self.processed_files[file_path].processed = True
            self.processed_files[file_path].chunks_count = chunks_count
            self._save_index()
    
    def get_processed_stats(self) -> Dict[str, int]:
        """获取处理统计信息"""
        total_files = len(self.processed_files)
        processed_files = sum(1 for doc in self.processed_files.values() if doc.processed)
        total_chunks = sum(doc.chunks_count for doc in self.processed_files.values() if doc.processed)
        
        return {
            'total_files': total_files,
            'processed_files': processed_files,
            'pending_files': total_files - processed_files,
            'total_chunks': total_chunks
        }
