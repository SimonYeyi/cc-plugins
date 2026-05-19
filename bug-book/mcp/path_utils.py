#!/usr/bin/env python3
"""路径匹配辅助函数 - 供 JSONL 后端共用"""

from pathlib import Path


def normalize_path(path: str) -> str:
    """统一路径分隔符为 /"""
    return str(Path(path)).replace("\\", "/")


def match_path(file_path: str, pattern: str) -> bool:
    """判断文件路径是否匹配 pattern。
    
    支持的匹配方式：
    1. 目录通配符：auth/* → 匹配 auth/ 目录下的所有文件
    2. 单段匹配：auth → 匹配路径中包含 auth 段的文件
    3. 多段前缀：src/auth → 匹配以 src/auth 开头的路径
    """
    file_path = normalize_path(file_path)
    pattern = pattern.rstrip("/")
    file_segs = [s for s in file_path.split("/") if s]
    
    if pattern.endswith("/*"):
        base = pattern[:-2]
        base_segs = [s for s in base.split("/") if s]
        if len(base_segs) > len(file_segs):
            return False
        if len(base_segs) == 1:
            return base_segs[0] in file_segs
        if any(p != f for p, f in zip(base_segs, file_segs)):
            return False
        return len(file_segs) > len(base_segs)
    
    pat_segs = [s for s in pattern.split("/") if s]
    if len(pat_segs) > len(file_segs):
        return False
    if len(pat_segs) == 1:
        return pat_segs[0] in file_segs
    return all(p == f for p, f in zip(pat_segs, file_segs))
