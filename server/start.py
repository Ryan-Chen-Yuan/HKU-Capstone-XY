#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
心理咨询对话系统启动脚本
"""

import sys
import os
from pathlib import Path
from app import app

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))


def check_environment():
    """检查环境变量配置"""
    # 首先尝试加载环境变量
    try:
        from load_env import load_environment

        load_environment()
    except ImportError:
        print("⚠️ 无法加载环境变量模块，使用系统环境变量")
        from dotenv import load_dotenv

        load_dotenv()
    
    # 设置tokenizers并行处理环境变量，避免fork警告
    if not os.getenv("TOKENIZERS_PARALLELISM"):
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        print("🔧 设置 TOKENIZERS_PARALLELISM=false 以避免并行处理警告")

    # TODO: 整理实际所需的环境变量
    required_vars = ["OPENAI_API_KEY", "BASE_URL", "MODEL_NAME"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请确保在.env文件中设置这些变量")
        return False

    print("✅ 环境变量检查通过")
    return True

def initialize_rag_system():
    """初始化RAG系统"""
    rag_enabled = os.environ.get("ENABLE_RAG", "true").lower() == "true"
    
    if not rag_enabled:
        print("ℹ️ RAG 功能已禁用")
        return True
    
    # 确保tokenizers并行处理设置正确
    if not os.getenv("TOKENIZERS_PARALLELISM"):
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    try:
        print("🔍 初始化RAG系统...")
        
        # 导入新的RAG核心模块
        from rag.core.rag_service import RAGCoreService
        import torch
        
        # 设置路径
        knowledge_source_dir = str(Path(__file__).parent / "knowledge_source")
        data_dir = str(Path(__file__).parent / "data")
        embedding_model_path = str(Path(__file__).parent / "qwen_embeddings")
        rerank_model_path = str(Path(__file__).parent / "qwen_reranker")
        
        # 设备选择（为MacBook Pro优化）
        device_config = os.environ.get("RAG_DEVICE", "auto").lower()
        force_cpu = os.environ.get("RAG_FORCE_CPU", "false").lower() == "true"
        
        if force_cpu:
            device = "cpu"
            print(f"🖥️ 强制使用设备: {device}")
        elif device_config == "auto":
            # 自动选择设备
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = "mps"
                # 安全的MPS内存管理设置
                mps_ratio = os.environ.get("PYTORCH_MPS_HIGH_WATERMARK_RATIO", "0.0")
                try:
                    # 验证MPS ratio有效性
                    ratio_float = float(mps_ratio)
                    if ratio_float < 0.0 or ratio_float > 1.0:
                        print(f"⚠️ 无效的MPS内存比率: {mps_ratio}，使用默认值0.0")
                        mps_ratio = "0.0"
                        os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = mps_ratio
                    
                    # 对于MPS，使用保守的内存管理设置
                    os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
                    
                    # 设置MPS内存管理环境变量
                    os.environ["PYTORCH_MPS_ALLOCATOR_POLICY"] = "garbage_collection"
                    
                    # 测试MPS是否真正可用
                    try:
                        test_device = torch.device("mps")
                        test_tensor = torch.ones(2, 2, device=test_device)
                        _ = test_tensor * 2  # 简单的运算测试
                        # 清理测试张量
                        del test_tensor
                        torch.mps.empty_cache()
                        print(f"🧠 MPS设备测试成功，使用优化的内存管理")
                        
                        # 显示MPS内存管理说明
                        print(f"   💡 MPS内存管理说明:")
                        print(f"   • 高水位线比率: {mps_ratio} (0.0=无限制，0.7=默认)")
                        print(f"   • 垃圾回收策略: 启用")
                        print(f"   • 批处理大小: {os.environ.get('RAG_BATCH_SIZE', '8')} (可在.env中调整)")
                        
                    except Exception as mps_e:
                        print(f"⚠️ MPS设备测试失败，回退到CPU: {mps_e}")
                        device = "cpu"
                        
                except ValueError:
                    print(f"⚠️ MPS内存比率格式错误: {mps_ratio}，使用CPU设备")
                    device = "cpu"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
            print(f"🖥️ 自动选择设备: {device}")
        else:
            device = device_config
            print(f"🖥️ 指定使用设备: {device}")
        
        # 获取分块配置
        chunk_size = int(os.environ.get("RAG_CHUNK_SIZE", "512"))
        chunk_overlap = int(os.environ.get("RAG_CHUNK_OVERLAP", "50"))
        batch_size = int(os.environ.get("RAG_BATCH_SIZE", "8" if device == "mps" else "32"))
        
        print(f"📄 分块配置: 大小={chunk_size}, 重叠={chunk_overlap}")
        print(f"🔢 批处理大小: {batch_size}")
        
        # 如果是MPS设备，显示内存管理信息
        if device == "mps":
            mps_ratio = os.environ.get("PYTORCH_MPS_HIGH_WATERMARK_RATIO", "0.0")
            print(f"🧠 MPS内存管理: 高水位线比率={mps_ratio}, 垃圾回收策略=启用")
        
        # 创建RAG核心服务
        rag_service = RAGCoreService(
            knowledge_source_dir=knowledge_source_dir,
            data_dir=data_dir,
            embedding_model_path=embedding_model_path,
            rerank_model_path=rerank_model_path,
            device=device,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # 初始化RAG系统（会扫描和处理新文件）
        success = rag_service.initialize()
        
        if success:
            stats = rag_service.get_statistics()
            print(f"✅ RAG系统初始化成功:")
            print(f"   - 已处理文件: {stats['knowledge_base']['processed_files']}")
            print(f"   - 向量库文档块: {stats['vector_store']['total_chunks']}")
            print(f"   - 嵌入维度: {stats['vector_store']['embedding_dim']}")
            print(f"   - 计算设备: {stats['vector_store'].get('device', 'unknown')}")
            
            # 将RAG服务存储到全局变量，供其他模块使用
            import sys
            import __main__
            __main__.rag_service = rag_service
            # 同时也存储到start模块（如果被作为模块导入）
            sys.modules['start'] = sys.modules[__name__]
            sys.modules['start'].rag_service = rag_service
            
            # 现在初始化聊天服务，确保它能找到全局RAG服务
            print("💬 初始化聊天服务...")
            from service.chat_langgraph_optimized import get_chat_service_instance
            get_chat_service_instance()
            print("✅ 聊天服务初始化完成")
            
        else:
            print("❌ RAG系统初始化失败")
            return False
            
        return True
        
    except ImportError as e:
        print(f"⚠️ RAG 依赖模块缺失: {e}")
        print("RAG 功能将被禁用，请检查依赖包安装")
        return True  # 不阻止系统启动
    except Exception as e:
        print(f"❌ RAG系统初始化错误: {e}")
        return False


def check_dependencies():
    """检查依赖包"""
    try:
        import flask
        import langchain_openai
        import langgraph
        import snownlp
        import pydantic

        print("✅ 基础依赖包检查通过")
        
        # 检查 RAG 依赖
        rag_enabled = os.environ.get("ENABLE_RAG", "true").lower() == "true"
        if rag_enabled:
            try:
                import numpy
                import faiss
                import sentence_transformers
                import torch
                import transformers
                import fitz  # PyMuPDF
                print("✅ RAG 依赖包检查通过")
            except ImportError as e:
                print(f"⚠️ RAG 依赖包缺失: {e}")
                print("RAG 功能将被禁用，请运行安装命令:")
                print("pip install -r requirements_rag.txt")
        else:
            print("ℹ️ RAG 功能已禁用")
        
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False


def check_prompt_files():
    """检查提示文件"""
    prompt_dir = Path(__file__).parent / "prompt"
    required_files = [
        "counselor_prompt.txt",
        "planning_prompt.txt",
        "guided_inquiry_prompt.txt",
        "pattern_analysis_prompt.txt",
    ]

    missing_files = []
    for file in required_files:
        if not (prompt_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"⚠️ 缺少提示文件: {', '.join(missing_files)}")
        print("系统将使用默认提示模板")
    else:
        print("✅ 提示文件检查通过")

    return True


def initialize_data_directories():
    """初始化数据目录"""
    data_dir = Path(__file__).parent / "data"
    subdirs = ["messages", "patterns", "plans", "events"]

    data_dir.mkdir(exist_ok=True)
    for subdir in subdirs:
        (data_dir / subdir).mkdir(exist_ok=True)

    print("✅ 数据目录初始化完成")


def start_server():
    """启动服务器"""
    print("🚀 启动心理咨询对话系统...")
    print("📊 使用集成版架构:")
    print("   - 统一数据库管理")
    print("   - 用户画像存储")
    print("   - 长短期记忆")
    print("   - 危机检测")
    print("   - 行为模式分析")
    print("   - 情绪评分")
    print("   - 智能日志记录")
    print()

    # 显示日志配置
    chat_logging = os.environ.get("ENABLE_CHAT_LOGGING", "true").lower() == "true"
    emotion_logging = os.environ.get("ENABLE_EMOTION_LOGGING", "true").lower() == "true"
    detailed_logging = (
        os.environ.get("ENABLE_DETAILED_LOGGING", "true").lower() == "true"
    )

    print("📝 日志配置:")
    print(f"   聊天日志: {'✅ 启用' if chat_logging else '❌ 禁用'}")
    print(f"   情绪日志: {'✅ 启用' if emotion_logging else '❌ 禁用'}")
    print(f"   详细日志: {'✅ 启用' if detailed_logging else '❌ 禁用'}")
    print()

    # 获取配置
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5858))
    DEBUG = os.environ.get("FLASK_ENV", "production") == "development"

    print(f"🌐 服务器地址: http://{HOST}:{PORT}")
    print(f"🔧 调试模式: {'开启' if DEBUG else '关闭'}")
    print()
    print("API端点:")
    print(f"  - POST http://{HOST}:{PORT}/api/chat - 聊天对话")
    print(f"  - GET  http://{HOST}:{PORT}/api/chat/history - 对话历史")
    print(f"  - POST http://{HOST}:{PORT}/api/mood - 情绪分析")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)

    try:
        app.run(host=HOST, port=PORT, debug=DEBUG)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")


def main():
    """主函数"""
    print("🩺 心理咨询对话系统")
    print("=" * 50)

    # 检查环境
    if not check_environment():
        return

    if not check_dependencies():
        return

    check_prompt_files()
    initialize_data_directories()

    # 初始化RAG系统
    if not initialize_rag_system():
        print("RAG系统初始化失败，是否继续启动？(y/N): ", end="")
        choice = input().lower()
        if choice != 'y':
            return


    print("=" * 50)
    start_server()


if __name__ == "__main__":
    main()
