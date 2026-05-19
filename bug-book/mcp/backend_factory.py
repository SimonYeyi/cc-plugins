#!/usr/bin/env python3
"""存储后端工厂 - 创建 JSONL 后端实例"""

from jsonl_backend import JSONLBackend
from storage_backend import BugStorageBackend


def create_backend() -> BugStorageBackend:
    """创建 JSONL 后端实例"""
    return JSONLBackend()
