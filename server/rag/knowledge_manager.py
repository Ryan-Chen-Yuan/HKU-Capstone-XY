#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知识库管理器

负责扫描knowledge_source文件夹，处理新文档，更新向量库
"""

import os
import hashlib
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class KnowledgeManager:
    """知识库管理器"""
    
    def __init__(self, knowledge_source_dir: str, data_dir: str):
        """
        初始化知识库管理器
        
        Args:
            knowledge_source_dir: 知识源文件夹路径
            data_dir: 数据存储文件夹路径
        """
        self.knowledge_source_dir = Path(knowledge_source_dir)
        self.data_dir = Path(data_dir)
        self.metadata_file = self.data_dir / "knowledge_metadata.json"
        
        # 确保目录存在
        self.data_dir.mkdir(exist_ok=True)
        self.knowledge_source_dir.mkdir(exist_ok=True)
        
        # 支持的文件类型
        self.supported_extensions = {'.txt', '.md', '.pdf', '.docx'}
        
    def get_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def load_metadata(self) -> Dict[str, Any]:
        """加载知识库元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载元数据失败: {e}")
        return {"files": {}, "last_update": None}
    
    def save_metadata(self, metadata: Dict[str, Any]) -> None:
        """保存知识库元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存元数据失败: {e}")
    
    def scan_knowledge_source(self) -> List[Dict[str, Any]]:
        """
        扫描knowledge_source文件夹，找出需要处理的新文件
        
        Returns:
            需要处理的文件列表
        """
        metadata = self.load_metadata()
        current_files = metadata.get("files", {})
        new_files = []
        
        logger.info(f"扫描知识源目录: {self.knowledge_source_dir}")
        
        for file_path in self.knowledge_source_dir.rglob("*"):
            if not file_path.is_file():
                continue
                
            if file_path.suffix.lower() not in self.supported_extensions:
                continue
                
            relative_path = str(file_path.relative_to(self.knowledge_source_dir))
            current_hash = self.get_file_hash(file_path)
            
            # 检查文件是否是新的或已修改
            if (relative_path not in current_files or 
                current_files[relative_path].get("hash") != current_hash):
                
                file_info = {
                    "path": str(file_path),
                    "relative_path": relative_path,
                    "hash": current_hash,
                    "size": file_path.stat().st_size,
                    "modified_time": file_path.stat().st_mtime,
                    "extension": file_path.suffix.lower()
                }
                new_files.append(file_info)
                logger.info(f"发现新文件或已修改文件: {relative_path}")
        
        return new_files
    
    def mark_file_processed(self, file_info: Dict[str, Any]) -> None:
        """标记文件已处理"""
        metadata = self.load_metadata()
        metadata["files"][file_info["relative_path"]] = {
            "hash": file_info["hash"],
            "size": file_info["size"],
            "modified_time": file_info["modified_time"],
            "processed_time": time.time(),
            "extension": file_info["extension"]
        }
        metadata["last_update"] = time.time()
        self.save_metadata(metadata)
    
    def get_processed_files_count(self) -> int:
        """获取已处理文件数量"""
        metadata = self.load_metadata()
        return len(metadata.get("files", {}))
    
    def clean_orphaned_entries(self) -> None:
        """清理已删除文件的元数据条目"""
        metadata = self.load_metadata()
        current_files = metadata.get("files", {})
        
        to_remove = []
        for relative_path in current_files:
            full_path = self.knowledge_source_dir / relative_path
            if not full_path.exists():
                to_remove.append(relative_path)
                logger.info(f"文件已删除，清理元数据: {relative_path}")
        
        for path in to_remove:
            del current_files[path]
        
        if to_remove:
            self.save_metadata(metadata)
            logger.info(f"清理了 {len(to_remove)} 个孤立条目")
