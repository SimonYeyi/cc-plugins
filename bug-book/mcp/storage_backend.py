#!/usr/bin/env python3
"""Bug-book 存储后端抽象接口"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BugStorageBackend(ABC):
    """Bug 存储后端抽象基类"""
    
    # -------------------- CRUD --------------------
    
    @abstractmethod
    def add_bug(
        self,
        title: str,
        phenomenon: str,
        root_cause: Optional[str] = None,
        solution: Optional[str] = None,
        test_case: Optional[str] = None,
        verified: bool = False,
        scores: Optional[dict[str, float]] = None,
        paths: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        keywords: Optional[list[str]] = None,
        recalls: Optional[list[str]] = None,
    ) -> tuple[Any, float]:
        """新增 bug，返回 (bug_id, score)"""
        pass
    
    @abstractmethod
    def update_bug(
        self,
        bug_id: Any,
        title: Optional[str] = None,
        phenomenon: Optional[str] = None,
        root_cause: Optional[str] = None,
        solution: Optional[str] = None,
        test_case: Optional[str] = None,
        status: Optional[str] = None,
        verified: Optional[bool] = None,
        verified_at: Optional[str] = None,
        verified_by: Optional[str] = None,
    ) -> None:
        """更新 bug"""
        pass
    
    @abstractmethod
    def delete_bug(self, bug_id: Any) -> None:
        """删除 bug（软删除）"""
        pass
    
    @abstractmethod
    def get_bug_detail(self, bug_id: Any) -> Optional[dict[str, Any]]:
        """获取 bug 详情"""
        pass
    
    @abstractmethod
    def list_bugs(
        self,
        status: Optional[str] = None,
        order_by: str = "score",
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """列出 bugs"""
        pass
    
    @abstractmethod
    def count_bugs(self) -> int:
        """统计 bug 总数"""
        pass
    
    # -------------------- 分数管理 --------------------
    
    @abstractmethod
    def increment_score(
        self,
        bug_id: Any,
        dimension: str = "occurrences",
        delta: float = 1.0,
    ) -> None:
        """累加分数"""
        pass
    
    # -------------------- 路径和召回管理 --------------------
    
    @abstractmethod
    def update_bug_paths(self, bug_id: Any, new_paths: list[str]) -> None:
        """批量更新路径"""
        pass
    
    @abstractmethod
    def update_bug_recalls(self, bug_id: Any, new_recalls: list[str]) -> None:
        """批量更新召回模式"""
        pass
    
    @abstractmethod
    def add_recall(self, bug_id: Any, pattern: str) -> None:
        """添加召回模式"""
        pass
    
    # -------------------- 搜索功能 --------------------
    
    @abstractmethod
    def search_by_keyword(self, keyword: str, limit: int = 20) -> list[dict[str, Any]]:
        """关键词搜索"""
        pass
    
    @abstractmethod
    def search_by_tag(self, tag: str, limit: int = 20) -> list[dict[str, Any]]:
        """标签搜索"""
        pass
    
    @abstractmethod
    def search_recent(self, days: int = 7, limit: int = 20) -> list[dict[str, Any]]:
        """搜索最近创建的"""
        pass
    
    @abstractmethod
    def search_high_score(
        self, min_score: float = 30.0, limit: int = 20
    ) -> list[dict[str, Any]]:
        """搜索高分 bugs"""
        pass
    
    @abstractmethod
    def search_top_critical(self, limit: int = 20) -> list[dict[str, Any]]:
        """搜索最严重的"""
        pass
    
    @abstractmethod
    def search_recent_unverified(
        self, days: int = 7, limit: int = 20
    ) -> list[dict[str, Any]]:
        """搜索最近未验证的"""
        pass
    
    @abstractmethod
    def search_by_status_and_score(
        self,
        status: str = "active",
        min_score: float = 0.0,
        max_score: Optional[float] = None,
        verified: Optional[bool] = None,
        order_by: str = "score",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """组合搜索"""
        pass
    
    # -------------------- 召回功能 --------------------
    
    @abstractmethod
    def recall_by_path(self, file_path: str, limit: int = 10) -> list[dict[str, Any]]:
        """按路径召回"""
        pass
    
    @abstractmethod
    def recall_by_pattern(self, pattern: str, limit: int = 10) -> list[dict[str, Any]]:
        """按模式召回"""
        pass

    # -------------------- 影响关系 --------------------
    
    @abstractmethod
    def add_impact(
        self,
        source_bug_id: Any,
        solution_change: str,
        impact_description: str,
        impact_type: str = "regression",
        severity: int = 5,
        prevention_delta: float = 3.0,
    ) -> Any:
        """添加影响关系，返回 impact_id"""
        pass
    
    @abstractmethod
    def update_impacted_paths(self, old_path: str, new_path: str) -> int:
        """批量更新影响路径"""
        pass
    
    @abstractmethod
    def delete_impact(self, impact_id: Any, prevention_delta: float = 0) -> None:
        """删除影响记录"""
        pass
    
    # -------------------- 高级功能 --------------------
    
    @abstractmethod
    def mark_invalid(self, bug_id: Any, reason: Optional[str] = None) -> None:
        """标记为无效"""
        pass
    
    @abstractmethod
    def list_unverified_old(
        self, days: int = 30, limit: int = 20
    ) -> list[dict[str, Any]]:
        """列出长期未验证的"""
        pass
    
    @abstractmethod
    def check_path_valid(self, path: str, root: Optional[Any] = None) -> bool:
        """检查路径有效性"""
        pass

    @abstractmethod
    def check_bug_paths(self, bug_id: Any) -> list[str]:
        """检查 bug 的 paths/recalls/impacts 路径是否有效，返回无效路径列表"""
        pass

    @abstractmethod
    def migrate_bug_paths_after_refactor(
        self, old_path: str, new_path: str
    ) -> tuple[list[Any], int]:
        """迁移重构后的路径"""
        pass
    
    # -------------------- 重构后的新接口 --------------------
    
    @abstractmethod
    def save_bugs(self, bugs_data) -> Any:
        """统一保存接口（支持多种 mode，支持批量操作）
        
        Args:
            bugs_data: 可以是单个 bug dict、数组或 {'bugs': [...]} 格式
        """
        pass
    
    @abstractmethod
    def search_bugs(self, **kwargs) -> dict[str, Any]:
        """统一搜索接口（支持多种模式 + 分页）"""
        pass
    
    @abstractmethod
    def compact_file(self) -> int:
        """压缩文件：移除已删除的记录，相同ID只保留最后一条
        
        Returns:
            清理的记录数量（被移除的旧记录数）
        """
        pass
    

