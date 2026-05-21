#!/usr/bin/env python3
"""Bug-book 存储后端抽象接口 - 最小公共接口"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BugBackend(ABC):
    """Bug 存储后端抽象基类 - 只提供原子操作方法
    
    职责：
    - 数据存储和检索
    - 提供细粒度的 CRUD 操作
    
    不负责：
    - 业务逻辑（mode 路由、批量操作等）
    - MCP 协议格式封装
    """
    
    # -------------------- 1. 基础 CRUD --------------------
    
    @abstractmethod
    def add_bug(self, **kwargs) -> tuple[int, float]:
        """新增 bug，返回 (bug_id, score)"""
        pass
    
    @abstractmethod
    def update_bug(self, bug_id: int, **kwargs) -> None:
        """更新 bug 字段"""
        pass
    
    @abstractmethod
    def get_bug(self, bug_id: int) -> Optional[dict[str, Any]]:
        """获取单个 bug"""
        pass
    
    @abstractmethod
    def get_all_bugs(self) -> dict[int, dict[str, Any]]:
        """获取所有 bugs（用于遍历）"""
        pass
    
    # -------------------- 2. 影响关系 --------------------
    
    @abstractmethod
    def add_impact(self, source_bug_id: int, **kwargs) -> int:
        """添加影响关系，返回 impact_id"""
        pass
    
    @abstractmethod
    def delete_impact(self, impact_id: int, prevention_delta: float = 0) -> None:
        """删除影响关系"""
        pass
    
    # -------------------- 3. 查询原语 --------------------

    @abstractmethod
    def find_by_keyword(self, keyword: str, limit: int) -> list[dict]:
        """关键词查询"""
        pass

    @abstractmethod
    def find_by_tag(self, tag: str, limit: int) -> list[dict]:
        """标签查询"""
        pass

    @abstractmethod
    def find_by_created_after(self, days: int, limit: int) -> list[dict]:
        """按创建时间查询"""
        pass

    @abstractmethod
    def find_by_min_score(self, min_score: float, limit: int) -> list[dict]:
        """按最低分数查询"""
        pass

    @abstractmethod
    def find_all_sorted(self, limit: int) -> list[dict]:
        """获取所有记录并按分数排序"""
        pass

    @abstractmethod
    def find_unverified_since(self, days: int, limit: int) -> list[dict]:
        """查询未验证记录"""
        pass

    @abstractmethod
    def query(
        self, status: str, min_score: float, max_score: Optional[float],
        verified: Optional[bool], order_by: str, limit: int
    ) -> list[dict]:
        """通用查询接口"""
        pass

    @abstractmethod
    def find_by_pattern(self, pattern: str, limit: int) -> list[dict]:
        """按路径模式查询"""
        pass
    
    # -------------------- 4. 辅助方法 --------------------
    
    @abstractmethod
    def count_bugs(self) -> int:
        """统计 bug 总数"""
        pass
    
    @abstractmethod
    def find_unverified_old(self, days: int, limit: int) -> list[dict]:
        """列出长期未验证的 bug"""
        pass
    
    @abstractmethod
    def compact_file(self) -> int:
        """压缩文件：移除 invalid 记录，相同ID只保留最后一条，返回清理数量"""
        pass
    
    # -------------------- 5. 索引查询 --------------------
    
    @abstractmethod
    def find_by_path(self, file_path: str, limit: int = 10) -> list[dict]:
        """按路径查询（利用索引）"""
        pass

    

