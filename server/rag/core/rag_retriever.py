#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG检索器 - 包含Qwen重排序功能
"""

import logging
import torch
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from sentence_transformers import CrossEncoder
from .qwen_vector_store import QwenVectorStore, SearchResult, DocumentChunk

logger = logging.getLogger(__name__)


@dataclass
class RerankedResult:
    """重排序后的结果"""
    chunk: DocumentChunk
    similarity_score: float  # 原始相似度分数
    rerank_score: Optional[float]  # 重排序分数
    final_rank: int


class RAGRetriever:
    """RAG检索器"""
    
    def __init__(self, vector_store: QwenVectorStore, rerank_model_path: str = None, device: str = None):
        """
        初始化检索器
        
        Args:
            vector_store: 向量存储
            rerank_model_path: 重排序模型路径
            device: 计算设备
        """
        self.vector_store = vector_store
        
        # 设备选择
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
            
        self.device = device
        
        # MPS内存管理设置
        if self.device == "mps":
            import os
            # 设置保守的MPS内存管理
            os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
            logger.info("重排序器使用保守的MPS内存管理设置")
            
            # 额外的MPS稳定性检查
            try:
                test_device = torch.device("mps")
                test_tensor = torch.ones(2, 2, device=test_device)
                _ = test_tensor * 2
                logger.info("重排序器MPS设备稳定性检查通过")
            except Exception as e:
                logger.warning(f"重排序器MPS设备稳定性检查失败，回退到CPU: {e}")
                self.device = "cpu"
        
        # 重排序模型
        self.rerank_model_path = rerank_model_path or "./qwen_reranker"
        self.rerank_model = None
        self.rerank_enabled = True
        
        logger.info(f"初始化RAG检索器，设备: {self.device}")
    
    def _load_rerank_model(self):
        """加载重排序模型"""
        if self.rerank_model is not None or not self.rerank_enabled:
            return
        
        try:
            logger.info(f"加载Qwen重排序模型: {self.rerank_model_path}")
            
            # 使用CrossEncoder加载
            self.rerank_model = CrossEncoder(
                self.rerank_model_path,
                device=self.device,
                trust_remote_code=True
            )
            
            logger.info("重排序模型加载成功")
            
        except Exception as e:
            logger.warning(f"加载重排序模型失败: {e}")
            logger.warning("将禁用重排序功能")
            self.rerank_enabled = False
    
    def search(self, 
               query: str, 
               top_k: int = 5, 
               use_rerank: bool = True, 
               rerank_top_k: int = None) -> List[RerankedResult]:
        """
        执行RAG搜索
        
        Args:
            query: 查询文本
            top_k: 最终返回结果数量
            use_rerank: 是否使用重排序
            rerank_top_k: 重排序候选数量 (默认为top_k*2)
            
        Returns:
            重排序后的结果列表
        """
        if rerank_top_k is None:
            rerank_top_k = max(top_k * 2, 10)  # 获取更多候选用于重排序
        
        # 1. 向量搜索获取候选结果
        search_results = self.vector_store.search(query, rerank_top_k)
        
        if not search_results:
            return []
        
        # 2. 重排序 (如果启用)
        if use_rerank and self.rerank_enabled:
            reranked_results = self._rerank_results(query, search_results, top_k)
        else:
            # 不使用重排序，直接转换格式
            reranked_results = []
            for i, result in enumerate(search_results[:top_k]):
                reranked_results.append(RerankedResult(
                    chunk=result.chunk,
                    similarity_score=result.score,
                    rerank_score=None,
                    final_rank=i + 1
                ))
        
        return reranked_results
    
    def _rerank_results(self, query: str, search_results: List[SearchResult], top_k: int) -> List[RerankedResult]:
        """重排序搜索结果"""
        self._load_rerank_model()
        
        if not self.rerank_enabled or self.rerank_model is None:
            # 重排序不可用，返回原始结果（去重）
            reranked_results = []
            seen_content = set()
            
            for i, result in enumerate(search_results):
                # 内容去重
                content_key = self._get_content_key(result.chunk.content)
                if content_key in seen_content:
                    continue
                seen_content.add(content_key)
                
                reranked_results.append(RerankedResult(
                    chunk=result.chunk,
                    similarity_score=result.score,
                    rerank_score=None,
                    final_rank=len(reranked_results) + 1
                ))
                
                if len(reranked_results) >= top_k:
                    break
                    
            return reranked_results
        
        try:
            # 对搜索结果进行预去重
            unique_results = []
            seen_content = set()
            
            for result in search_results:
                content_key = self._get_content_key(result.chunk.content)
                if content_key not in seen_content:
                    seen_content.add(content_key)
                    unique_results.append(result)
            
            logger.debug(f"重排序前去重: {len(search_results)} -> {len(unique_results)} 个候选")
            
            # 准备重排序输入
            pairs = []
            for result in unique_results:
                pairs.append([query, result.chunk.content])
            
            # 执行重排序
            logger.debug(f"对 {len(pairs)} 个候选结果进行重排序")
            rerank_scores = self.rerank_model.predict(pairs, batch_size=8)
            
            # 组合结果并排序
            combined_results = []
            for i, (result, rerank_score) in enumerate(zip(unique_results, rerank_scores)):
                combined_results.append(RerankedResult(
                    chunk=result.chunk,
                    similarity_score=result.score,
                    rerank_score=float(rerank_score),
                    final_rank=0  # 临时值，排序后会更新
                ))
            
            # 按重排序分数排序（从高到低）
            combined_results.sort(key=lambda x: x.rerank_score, reverse=True)
            
            # 更新最终排名并截取top_k
            final_results = []
            for i, result in enumerate(combined_results[:top_k]):
                result.final_rank = i + 1
                final_results.append(result)
            
            logger.debug(f"重排序完成，返回top {len(final_results)} 结果")
            return final_results
            
        except Exception as e:
            logger.error(f"重排序失败: {e}")
            # 回退到原始结果（去重）
            reranked_results = []
            seen_content = set()
            
            for i, result in enumerate(search_results):
                content_key = self._get_content_key(result.chunk.content)
                if content_key in seen_content:
                    continue
                seen_content.add(content_key)
                
                reranked_results.append(RerankedResult(
                    chunk=result.chunk,
                    similarity_score=result.score,
                    rerank_score=None,
                    final_rank=len(reranked_results) + 1
                ))
                
                if len(reranked_results) >= top_k:
                    break
                    
            return reranked_results
    
    def _get_content_key(self, content: str) -> str:
        """生成内容的唯一标识符"""
        import hashlib
        # 使用前200个字符的hash作为去重键，更精确
        content_sample = content[:200].strip()
        content_hash = hashlib.md5(content_sample.encode('utf-8')).hexdigest()[:16]
        return content_hash
    
    def get_context_for_query(self, query: str, top_k: int = 3, use_rerank: bool = True) -> str:
        """
        为查询生成上下文
        
        Args:
            query: 查询文本
            top_k: 使用的文档块数量
            use_rerank: 是否使用重排序
            
        Returns:
            格式化的上下文字符串
        """
        results = self.search(query, top_k, use_rerank)
        
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[文档{i}] 来源: {result.chunk.source_file}")
            context_parts.append(result.chunk.content)
            context_parts.append("")  # 空行分隔
        
        return "\n".join(context_parts)
    
    def print_debug_info(self, query: str, results: List[RerankedResult]):
        """打印调试信息"""
        print(f"\n🔍 查询: {query}")
        print(f"📊 检索结果: {len(results)} 个文档块")
        print("-" * 60)
        
        for result in results:
            print(f"📄 排名 {result.final_rank}")
            print(f"   文件: {result.chunk.source_file}")
            print(f"   相似度: {result.similarity_score:.4f}")
            if result.rerank_score is not None:
                print(f"   重排序分数: {result.rerank_score:.4f}")
            print(f"   内容预览: {result.chunk.content[:100]}...")
            print()
    
    def disable_rerank(self):
        """禁用重排序"""
        self.rerank_enabled = False
        logger.info("重排序功能已禁用")
    
    def enable_rerank(self):
        """启用重排序"""
        self.rerank_enabled = True
        logger.info("重排序功能已启用")
