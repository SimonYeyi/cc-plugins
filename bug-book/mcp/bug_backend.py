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
    
    # -------------------- 3. 搜索原语 --------------------
    
    @abstractmethod
    def search_by_keyword(self, keyword: str, limit: int) -> list[dict]:
        """关键词搜索"""
        pass
    
    @abstractmethod
    def search_by_tag(self, tag: str, limit: int) -> list[dict]:
        """标签搜索"""
        pass
    
    @abstractmethod
    def search_recent(self, days: int, limit: int) -> list[dict]:
        """最近创建搜索"""
        pass
    
    @abstractmethod
    def search_high_score(self, min_score: float, limit: int) -> list[dict]:
        """高分搜索"""
        pass
    
    @abstractmethod
    def search_top_critical(self, limit: int) -> list[dict]:
        """关键 bug 搜索"""
        pass
    
    @abstractmethod
    def search_recent_unverified(self, days: int, limit: int) -> list[dict]:
        """未验证搜索"""
        pass
    
    @abstractmethod
    def search_by_status_and_score(
        self, status: str, min_score: float, max_score: Optional[float],
        verified: Optional[bool], order_by: str, limit: int
    ) -> list[dict]:
        """自定义搜索"""
        pass
    
    @abstractmethod
    def search_by_module_patterns(self, pattern: str, limit: int) -> list[dict]:
        """模块模式搜索"""
        pass
    
    # -------------------- 4. 辅助方法 --------------------
    
    @abstractmethod
    def check_bug_paths(self, bug_id: int) -> list[str]:
        """检查 bug 的路径是否有效，返回无效路径列表"""
        pass
    
    @abstractmethod
    def count_bugs(self) -> int:
        """统计 bug 总数"""
        pass
    
    @abstractmethod
    def list_unverified_old(self, days: int, limit: int) -> list[dict]:
        """列出长期未验证的 bug"""
        pass
    
    @abstractmethod
    def compact_file(self) -> int:
        """压缩文件：移除 invalid 记录，相同ID只保留最后一条，返回清理数量"""
        pass
    
    # -------------------- 5. 索引查询 --------------------
    
    @abstractmethod
    def recall_by_path(self, file_path: str, limit: int = 10) -> list[dict]:
        """按路径召回（利用索引）"""
        pass

    

