#!/usr/bin/env python3
"""Bug-book 存储后端抽象接口 - 最小公共接口"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BugStorageBackend(ABC):
    """Bug 存储后端抽象基类 - 仅暴露6个公共方法"""
    
    # -------------------- 1. 统一保存 --------------------
    
    @abstractmethod
    def save_bugs(self, bugs_data) -> Any:
        """统一保存接口（支持多种 mode，支持批量操作）
        
        Args:
            bugs_data: 可以是单个 bug dict、数组或 {'bugs': [...]} 格式
            
        Returns:
            保存结果数据（如 {'results': [...], 'count': N}），失败时抛出异常
        """
        pass
    
    # -------------------- 2. 统一搜索 --------------------
    
    @abstractmethod
    def search_bugs(self, **kwargs) -> dict[str, Any]:
        """统一搜索接口（支持多种模式 + 分页）
        
        Returns:
            搜索结果数据 {'bugs': [...], 'pagination': {...}}，失败时抛出异常
        """
        pass

    # -------------------- 3. 整理 bug-book --------------------

    @abstractmethod
    def organize_bugs(self) -> dict[str, Any]:
        """整理 bug-book，返回结构化数据供模型生成报告

        Returns:
            {
                "invalid_candidates": [...],  # 待标记失效的bug
                "unverified_old": [...],      # 长期未验证的bug
                "statistics": {...},          # 统计信息
                "last_organize_time": "...",  # 最后整理时间
            }
        """
        pass
    
    # -------------------- 4. 获取详情 --------------------
    
    @abstractmethod
    def get_bug_detail(self, bug_id: Any) -> Optional[dict[str, Any]]:
        """获取 bug 详情"""
        pass
    
    # -------------------- 5. 路径召回 --------------------
    
    @abstractmethod
    def recall_by_path(self, file_path: str, limit: int = 10) -> list[dict[str, Any]]:
        """按路径召回相关 bug（用于 hook）"""
        pass
    
    # -------------------- 6. 路径迁移 --------------------
    
    @abstractmethod
    def migrate_bug_paths_after_refactor(
        self, old_path: str, new_path: str
    ) -> list[int]:
        """迁移重构后的路径，返回被迁移的 bug_id 列表"""
        pass

    

