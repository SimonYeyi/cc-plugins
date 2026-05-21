#!/usr/bin/env python3
"""存储后端工厂 - 创建 JSONL 后端实例"""

from jsonl_backend import JSONLBackend
from bug_backend import BugBackend


def create_backend() -> BugBackend:
    """创建 JSONL 后端实例"""
    return JSONLBackend()
