import os
from pathlib import Path


def find_project_root() -> Path:
    """查找项目根目录"""
    return Path(os.getcwd()).resolve()


def get_data_dir() -> Path:
    """获取数据存储目录"""
    return find_project_root() / "bug-book-data"
