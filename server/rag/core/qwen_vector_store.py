#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基于Qwen模型的向量存储服务
"""

import os
import json
import pickle
import logging
import numpy as np
import torch
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

import faiss
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """文档块"""
    chunk_id: str
    content: str
    source_file: str
    chunk_index: int
    metadata: Dict[str, Any] = None


@dataclass
class SearchResult:
    """搜索结果"""
    chunk: DocumentChunk
    score: float
    rank: int


class QwenVectorStore:
    """基于Qwen的向量存储"""
    
    def __init__(self, data_dir: str, embedding_model_path: str = None, device: str = None):
        """
        初始化向量存储
        
        Args:
            data_dir: 数据目录
            embedding_model_path: 嵌入模型路径
            device: 计算设备
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 向量存储文件
        self.index_file = self.data_dir / "faiss_index.bin"
        self.metadata_file = self.data_dir / "chunks_metadata.json"
        self.chunks_file = self.data_dir / "document_chunks.pkl"
        
        # 设备选择 (为MacBook Pro优化)
        if device is None or device == "auto":
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = "mps"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
        
        # 验证设备有效性
        valid_devices = ["cpu", "cuda", "mps"]
        if device not in valid_devices:
            logger.warning(f"无效的设备类型 '{device}'，使用 'cpu' 作为默认值")
            device = "cpu"
            
        # 对于MPS设备，进行安全性检查
        if device == "mps":
            try:
                # 测试MPS设备是否真正可用
                test_device = torch.device("mps")
                test_tensor = torch.ones(2, 2, device=test_device)
                _ = test_tensor * 2
                # 清理测试张量
                del test_tensor
                torch.mps.empty_cache()
                logger.info("MPS设备可用性测试通过")
                
                # 设置MPS内存管理
                os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
                os.environ["PYTORCH_MPS_ALLOCATOR_POLICY"] = "garbage_collection"
                
            except Exception as e:
                logger.warning(f"MPS设备测试失败，回退到CPU: {e}")
                device = "cpu"
            
        self.device = device
        logger.info(f"向量存储使用设备: {self.device}")
        
        # MPS内存管理设置（仅在确认MPS可用时）
        if self.device == "mps":
            # 设置保守的MPS内存管理
            os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
            os.environ["PYTORCH_MPS_ALLOCATOR_POLICY"] = "garbage_collection"
            logger.info("向量存储使用优化的MPS内存管理设置")
            
            # 额外的MPS稳定性检查
            try:
                test_device = torch.device("mps")
                test_tensor = torch.ones(2, 2, device=test_device)
                _ = test_tensor * 2
                # 清理测试张量
                del test_tensor
                torch.mps.empty_cache()
                logger.info("向量存储MPS设备稳定性检查通过")
            except Exception as e:
                logger.warning(f"向量存储MPS设备稳定性检查失败，回退到CPU: {e}")
                self.device = "cpu"
        
        # 嵌入模型
        self.embedding_model_path = embedding_model_path or "./qwen_embeddings"
        self.embedding_model = None
        self.embedding_dim = 768  # Qwen3-Embedding-0.6B的维度
        
        # FAISS索引
        self.index = None
        self.chunks: List[DocumentChunk] = []
        self.chunk_metadata: Dict[str, Any] = {}
        
        # 分块参数
        self.chunk_size = 512
        self.overlap_size = 100
        
        logger.info(f"初始化Qwen向量存储，设备: {self.device}")
    
    def _load_embedding_model(self):
        """加载嵌入模型"""
        if self.embedding_model is not None:
            return
        
        try:
            logger.info(f"加载Qwen嵌入模型: {self.embedding_model_path}")
            
            # MPS设备预清理
            if self.device == "mps":
                torch.mps.empty_cache()
                logger.info("模型加载前MPS内存清理完成")
            
            # 使用SentenceTransformer加载
            if os.path.exists(self.embedding_model_path):
                self.embedding_model = SentenceTransformer(
                    self.embedding_model_path,
                    device=self.device
                )
            else:
                # 如果本地模型不存在，尝试下载
                logger.warning(f"本地模型不存在，尝试下载Qwen嵌入模型")
                self.embedding_model = SentenceTransformer(
                    "Qwen/Qwen3-Embedding-0.6B",
                    device=self.device
                )
            
            # 获取实际的嵌入维度
            test_embedding = self.embedding_model.encode(["测试文本"])
            self.embedding_dim = test_embedding.shape[1]
            
            # 清理测试嵌入
            del test_embedding
            if self.device == "mps":
                torch.mps.empty_cache()
                logger.info("模型加载后MPS内存清理完成")
            
            logger.info(f"嵌入模型加载成功，维度: {self.embedding_dim}")
            
        except Exception as e:
            logger.error(f"加载嵌入模型失败: {e}")
            raise
    
    def _split_text_into_chunks(self, text: str, source_file: str) -> List[DocumentChunk]:
        """将文本分割成块"""
        chunks = []
        
        # 简单的滑动窗口分块
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_id = f"{source_file}_{chunk_index}"
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    content=chunk_text,
                    source_file=source_file,
                    chunk_index=chunk_index,
                    metadata={
                        'start_pos': start,
                        'end_pos': end,
                        'text_length': len(chunk_text)
                    }
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # 移动窗口，考虑重叠
            start = end - self.overlap_size if end < len(text) else end
        
        logger.debug(f"文档分块完成: {source_file} -> {len(chunks)} 块")
        return chunks
    
    def _create_faiss_index(self):
        """创建FAISS索引"""
        if self.device == "mps" or self.device == "cuda":
            # GPU设备使用FlatIP (内积)
            self.index = faiss.IndexFlatIP(self.embedding_dim)
        else:
            # CPU使用余弦相似度
            self.index = faiss.IndexFlatIP(self.embedding_dim)
        
        logger.info(f"创建FAISS索引: 维度={self.embedding_dim}, 设备={self.device}")
    
    def load_index(self) -> bool:
        """加载已存在的索引"""
        try:
            if not (self.index_file.exists() and self.metadata_file.exists() and self.chunks_file.exists()):
                logger.info("向量索引文件不存在，需要重新构建")
                return False
            
            print("📥 加载向量索引...")
            
            # 加载FAISS索引
            print("   - 加载FAISS索引...")
            self.index = faiss.read_index(str(self.index_file))
            
            # 加载元数据
            print("   - 加载元数据...")
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.chunk_metadata = json.load(f)
            
            # 加载文档块
            print("   - 加载文档块...")
            with open(self.chunks_file, 'rb') as f:
                self.chunks = pickle.load(f)
            
            print(f"✅ 向量索引加载成功: {len(self.chunks)} 个文档块")
            logger.info(f"向量索引加载成功: {len(self.chunks)} 个文档块")
            return True
            
        except Exception as e:
            logger.error(f"加载向量索引失败: {e}")
            print(f"❌ 加载向量索引失败: {e}")
            return False
    
    def save_index(self):
        """保存索引到磁盘"""
        try:
            print("💾 保存向量索引...")
            
            if self.index is not None:
                print("   - 保存FAISS索引...")
                faiss.write_index(self.index, str(self.index_file))
            
            # 保存元数据
            print("   - 保存元数据...")
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.chunk_metadata, f, ensure_ascii=False, indent=2)
            
            # 保存文档块
            print("   - 保存文档块...")
            with open(self.chunks_file, 'wb') as f:
                pickle.dump(self.chunks, f)
            
            print("✅ 向量索引保存完成")
            logger.info("向量索引保存成功")
            
        except Exception as e:
            logger.error(f"保存向量索引失败: {e}")
            print(f"❌ 保存向量索引失败: {e}")
    
    def add_documents(self, documents: List[Tuple[str, str]]) -> int:
        """
        添加文档到向量存储
        
        Args:
            documents: [(文档内容, 源文件路径), ...]
            
        Returns:
            添加的文档块数量
        """
        self._load_embedding_model()
        
        if self.index is None:
            self._create_faiss_index()
        
        all_chunks = []
        all_texts = []
        
        # 处理所有文档 - 添加进度条
        print(f"📄 开始处理 {len(documents)} 个文档...")
        for content, source_file in tqdm(documents, desc="分析文档", unit="个"):
            chunks = self._split_text_into_chunks(content, source_file)
            all_chunks.extend(chunks)
            all_texts.extend([chunk.content for chunk in chunks])
        
        if not all_texts:
            return 0
        
        print(f"📊 总共生成 {len(all_texts)} 个文档块")
        
        # 批量生成嵌入 - 添加进度条
        logger.info(f"生成 {len(all_texts)} 个文档块的嵌入向量...")
        
        # 计算批次 - 支持环境变量配置
        default_batch_size = 8 if self.device == "mps" else 32
        batch_size = int(os.environ.get("RAG_BATCH_SIZE", default_batch_size))
        
        # 如果是MPS设备，确保批次大小不会太大
        if self.device == "mps" and batch_size > 16:
            logger.warning(f"MPS设备批次大小过大({batch_size})，调整为16")
            batch_size = 16
        
        total_batches = (len(all_texts) + batch_size - 1) // batch_size
        
        all_embeddings = []
        print(f"🧠 开始生成嵌入向量 (设备: {self.device}, 批大小: {batch_size})...")
        
        # 分批处理，显示进度
        for i in tqdm(range(0, len(all_texts), batch_size), 
                     desc="生成向量", unit="batch", total=total_batches):
            batch_texts = all_texts[i:i+batch_size]
            
            # MPS内存管理
            if self.device == "mps":
                import torch
                # 清理MPS缓存
                torch.mps.empty_cache()
                # 设置随机种子
                torch.manual_seed(42)
            
            try:
                batch_embeddings = self.embedding_model.encode(
                    batch_texts, 
                    batch_size=batch_size,
                    convert_to_numpy=True,
                    normalize_embeddings=True,  # 归一化，用于余弦相似度
                    show_progress_bar=False  # 禁用内部进度条，避免冲突
                )
                all_embeddings.append(batch_embeddings)
                
                # MPS内存清理
                if self.device == "mps":
                    torch.mps.empty_cache()
                    
            except RuntimeError as e:
                if "out of memory" in str(e).lower():
                    print(f"⚠️ 批次 {i//batch_size + 1} 内存不足，尝试更小的批次...")
                    # 尝试更小的批次
                    smaller_batch_size = max(1, batch_size // 2)
                    sub_embeddings = []
                    
                    for j in range(0, len(batch_texts), smaller_batch_size):
                        sub_batch = batch_texts[j:j+smaller_batch_size]
                        if self.device == "mps":
                            torch.mps.empty_cache()
                        
                        sub_embedding = self.embedding_model.encode(
                            sub_batch,
                            batch_size=smaller_batch_size,
                            convert_to_numpy=True,
                            normalize_embeddings=True,
                            show_progress_bar=False
                        )
                        sub_embeddings.append(sub_embedding)
                        
                        if self.device == "mps":
                            torch.mps.empty_cache()
                    
                    # 合并子批次
                    if sub_embeddings:
                        batch_embeddings = np.vstack(sub_embeddings)
                        all_embeddings.append(batch_embeddings)
                else:
                    raise e
        
        # 合并所有嵌入向量
        embeddings = np.vstack(all_embeddings)
        
        # 添加到FAISS索引 - 添加进度条
        print(f"🗂️ 将 {len(embeddings)} 个向量添加到FAISS索引...")
        
        # 对于大量向量，分批添加到FAISS
        faiss_batch_size = 1000
        for i in tqdm(range(0, len(embeddings), faiss_batch_size), 
                     desc="更新索引", unit="batch"):
            end_idx = min(i + faiss_batch_size, len(embeddings))
            batch_vectors = embeddings[i:end_idx].astype(np.float32)
            self.index.add(batch_vectors)
        
        # 更新文档块列表
        self.chunks.extend(all_chunks)
        
        # 更新元数据
        print("📋 更新元数据...")
        for i, chunk in enumerate(tqdm(all_chunks, desc="更新元数据", unit="块")):
            self.chunk_metadata[chunk.chunk_id] = {
                'source_file': chunk.source_file,
                'chunk_index': chunk.chunk_index,
                'content_length': len(chunk.content),
                'vector_index': len(self.chunks) - len(all_chunks) + i
            }
        
        logger.info(f"成功添加 {len(all_chunks)} 个文档块到向量存储")
        print(f"✅ 向量存储更新完成: +{len(all_chunks)} 个文档块")
        return len(all_chunks)
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        向量搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        if self.index is None or len(self.chunks) == 0:
            logger.warning("向量索引为空")
            return []
        
        self._load_embedding_model()
        
        # 生成查询向量
        query_embedding = self.embedding_model.encode(
            [query], 
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        # 搜索
        scores, indices = self.index.search(
            query_embedding.astype(np.float32), 
            min(top_k, len(self.chunks))
        )
        
        # 构建结果
        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.chunks):
                result = SearchResult(
                    chunk=self.chunks[idx],
                    score=float(score),
                    rank=rank + 1
                )
                results.append(result)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取向量存储统计信息"""
        return {
            'total_chunks': len(self.chunks),
            'embedding_dim': self.embedding_dim,
            'device': self.device,
            'index_exists': self.index is not None,
            'chunk_size': self.chunk_size,
            'overlap_size': self.overlap_size
        }
    
    def clear(self):
        """清空向量存储"""
        self.index = None
        self.chunks = []
        self.chunk_metadata = {}
        
        # 删除文件
        for file in [self.index_file, self.metadata_file, self.chunks_file]:
            if file.exists():
                file.unlink()
        
        logger.info("向量存储已清空")
