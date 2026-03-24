#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千问百炼 (Qwen) 输入长度限制处理配置
- 最大输入长度: 258,048 字符
- 安全阈值: 250,000 字符 (预留缓冲空间)
- 自动分块策略
"""

import re
from typing import List, Dict, Any

# Qwen 模型限制配置
QWEN_CONFIG = {
    "max_input_length": 258048,      # Qwen 最大输入长度
    "safe_threshold": 250000,        # 安全阈值，预留 8K 缓冲
    "chunk_overlap": 1000,          # 分块重叠字符数，确保上下文连贯
    "min_chunk_size": 10000,        # 最小分块大小
}

def should_chunk_input(text: str) -> bool:
    """判断是否需要对输入进行分块"""
    return len(text) > QWEN_CONFIG["safe_threshold"]

def smart_chunk_text(text: str, max_chunk_size: int = None) -> List[str]:
    """
    智能分块文本，优先在自然断点处分割
    
    Args:
        text: 要分块的文本
        max_chunk_size: 最大分块大小，默认使用安全阈值
        
    Returns:
        分块后的文本列表
    """
    if max_chunk_size is None:
        max_chunk_size = QWEN_CONFIG["safe_threshold"]
    
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chunk_size
        
        # 如果已经到达文本末尾
        if end >= len(text):
            chunks.append(text[start:])
            break
        
        # 寻找最佳分割点（优先级从高到低）
        best_split = end
        
        # 1. 优先在章节标题后分割（###, ##, # 等）
        section_pattern = r'\n#{1,6}\s'
        for match in re.finditer(section_pattern, text[start:end]):
            if match.start() > max_chunk_size * 0.7:  # 确保不会太早分割
                best_split = start + match.start()
                break
        
        # 2. 如果没找到章节标题，在段落边界分割
        if best_split == end:
            paragraph_pattern = r'\n\s*\n'
            matches = list(re.finditer(paragraph_pattern, text[start:end]))
            if matches:
                # 选择最接近末尾的段落边界
                for match in reversed(matches):
                    if match.start() > max_chunk_size * 0.5:
                        best_split = start + match.end()
                        break
        
        # 3. 如果还是没找到，在句子边界分割
        if best_split == end:
            sentence_pattern = r'[。！？.!?]\s'
            matches = list(re.finditer(sentence_pattern, text[start:end]))
            if matches:
                # 选择最接近末尾的句子边界
                for match in reversed(matches):
                    if match.start() > max_chunk_size * 0.8:
                        best_split = start + match.end()
                        break
        
        # 4. 如果以上都没找到，强制在最大长度处分割
        if best_split == end:
            best_split = end
        
        chunk = text[start:best_split]
        chunks.append(chunk)
        
        # 下一个分块的起始位置（考虑重叠）
        start = best_split - min(QWEN_CONFIG["chunk_overlap"], len(chunk) // 2)
        if start < best_split:  # 确保有进展
            start = best_split
    
    return chunks

def process_large_input_for_qwen(text: str, prompt_template: str = None) -> Dict[str, Any]:
    """
    处理大输入文本以适配 Qwen 模型
    
    Args:
        text: 输入文本
        prompt_template: 提示词模板，包含 {chunk} 占位符
        
    Returns:
        处理结果字典
    """
    if not should_chunk_input(text):
        return {
            "needs_chunking": False,
            "chunks": [text],
            "total_chunks": 1,
            "original_length": len(text),
            "max_chunk_length": len(text)
        }
    
    # 进行智能分块
    chunks = smart_chunk_text(text)
    
    # 如果提供了提示词模板，应用模板
    if prompt_template:
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunk = prompt_template.format(
                chunk=chunk,
                chunk_index=i + 1,
                total_chunks=len(chunks)
            )
            processed_chunks.append(processed_chunk)
        chunks = processed_chunks
    
    return {
        "needs_chunking": True,
        "chunks": chunks,
        "total_chunks": len(chunks),
        "original_length": len(text),
        "max_chunk_length": max(len(chunk) for chunk in chunks) if chunks else 0
    }

def merge_chunk_results(results: List[Any], merge_strategy: str = "concat") -> Any:
    """
    合并分块处理的结果
    
    Args:
        results: 分块处理的结果列表
        merge_strategy: 合并策略 ("concat", "json_merge", "custom")
        
    Returns:
        合并后的结果
    """
    if merge_strategy == "concat":
        if all(isinstance(r, str) for r in results):
            return "\n".join(results)
        else:
            return results
    
    elif merge_strategy == "json_merge":
        # 假设结果是 JSON 对象，进行深度合并
        import json
        merged = {}
        for result in results:
            if isinstance(result, str):
                try:
                    result_obj = json.loads(result)
                except:
                    continue
            else:
                result_obj = result
            
            if isinstance(result_obj, dict):
                merged.update(result_obj)
        
        return merged
    
    else:  # custom or unknown
        return results

# 使用示例
if __name__ == "__main__":
    # 测试用例
    try:
        with open("README-v4.md", "r", encoding="utf-8") as f:
            test_text = f.read()
    except FileNotFoundError:
        # 如果找不到 README-v4.md，使用 README.md
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                test_text = f.read()
        except FileNotFoundError:
            test_text = "这是一个测试文本。" * 10000  # 创建一个长文本用于测试
    
    print(f"原始文本长度: {len(test_text)}")
    
    result = process_large_input_for_qwen(test_text)
    print(f"需要分块: {result['needs_chunking']}")
    print(f"分块数量: {result['total_chunks']}")
    print(f"最大分块长度: {result['max_chunk_length']}")
    
    if result['needs_chunking']:
        print("\n分块预览:")
        for i, chunk in enumerate(result['chunks'][:2]):  # 只显示前两个分块
            print(f"\n--- 分块 {i+1} ---")
            print(f"长度: {len(chunk)}")
            print(f"内容预览: {chunk[:200]}...")