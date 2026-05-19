#!/usr/bin/env python3
"""JSONL 存储后端 - 完整实现"""

import json
import os
import random
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage_backend import BugStorageBackend
from config import find_project_root, get_data_dir
from path_utils import normalize_path, match_path


# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
DATA_DIR = get_data_dir()
BUGS_FILE = DATA_DIR / "bug-book.jsonl"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 权重配置
_WEIGHT_DIMENSIONS = frozenset({
    "importance", "complexity", "scope", "difficulty",
    "occurrences", "emotion", "prevention",
})
_DEFAULT_WEIGHTS = {
    "importance": 2.0, "complexity": 1.5, "scope": 1.0,
    "difficulty": 1.0, "occurrences": 1.0, "emotion": 1.5, "prevention": 2.0,
}
_weights_env = os.environ.get("BUG_BOOK_WEIGHTS", "").strip()
if _weights_env:
    try:
        _parsed = json.loads(_weights_env)
        if isinstance(_parsed, dict):
            DEFAULT_WEIGHTS = _DEFAULT_WEIGHTS.copy()
            for k, v in _parsed.items():
                if k in _WEIGHT_DIMENSIONS and isinstance(v, (int, float)):
                    DEFAULT_WEIGHTS[k] = float(v)
        else:
            DEFAULT_WEIGHTS = _DEFAULT_WEIGHTS.copy()
    except Exception:
        DEFAULT_WEIGHTS = _DEFAULT_WEIGHTS.copy()
else:
    DEFAULT_WEIGHTS = _DEFAULT_WEIGHTS.copy()

# 常量
THRESHOLD_HIGH_SCORE = 30
THRESHOLD_OLD_BUGS_DAYS = 30
DEFAULT_LIST_LIMIT = 50
SEARCH_LIMIT = 20
RECALL_LIMIT = 10
RECALL_BATCH_LIMIT = 200
ALLOWED_ORDER_BY = frozenset({"score", "created_at", "updated_at", "id", "title"})

# ID 生成器状态
# 使用时间戳 + 随机数保证团队共享时不冲突


def generate_id() -> int:
    """生成时间戳毫秒级 ID（int），保证团队共享时不冲突"""
    return int(time.time() * 1000) * 100 + random.randint(0, 99)





def _calc_score(scores_dict: dict[str, float]) -> float:
    """计算总分"""
    if not scores_dict:
        return 0.0
    return sum(DEFAULT_WEIGHTS.get(d, 1.0) * v for d, v in scores_dict.items())


def _normalize_path(path: str) -> str:
    """规范化路径（委托给 path_utils）"""
    return normalize_path(path)

class ValidationError(Exception):
    """校验失败"""
    pass


class JSONLBackend(BugStorageBackend):
    """JSONL 存储后端完整实现"""

    def __init__(self):
        # 内存数据结构
        self._bugs = {}                     # id(int) → bug 折叠后
        self._mtime = 0                      # 上次加载时的文件 mtime
        self._loaded = False                  # 是否已加载

        # 索引
        self.keyword_index = defaultdict(list)
        self.path_index = defaultdict(list)
        self.tag_index = defaultdict(list)
        self.recall_index = defaultdict(list)
        self.impacts_index = defaultdict(list)

        # 反向索引：bug_id → {index_type: [keys...]}，用于 O(1) 清除索引
        self._bug_index_refs = {}          # bug_id → {type: [keys...]}

        # 初始化数据
        self._ensure_loaded()

    def _ensure_loaded(self):
        """确保数据已加载（mtime 变化时重新加载）"""
        if not self._loaded:
            self._load_data()
            self._loaded = True
            return

        try:
            current_mtime = os.path.getmtime(BUGS_FILE)
        except OSError:
            return

        if current_mtime > self._mtime:
            self._load_data()
    
    def _load_data(self):
        """全量加载数据并折叠"""
        self._bugs = {}
        self.keyword_index.clear()
        self.path_index.clear()
        self.tag_index.clear()
        self.recall_index.clear()
        self.impacts_index.clear()
        self._bug_index_refs.clear()
        
        if not BUGS_FILE.exists():
            self._mtime = 0
            return
        
        try:
            self._mtime = os.path.getmtime(BUGS_FILE)
        except OSError:
            self._mtime = 0
        
        with open(BUGS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    bug = json.loads(line)
                    self._fold_bug(bug)
                except json.JSONDecodeError:
                    continue
    
    def _fold_bug(self, bug: dict):
        """将 bug 折叠到内存中"""
        bug_id = bug.get('id')
        if bug_id is None:
            return
        
        # 如果 bug 已存在，先清除旧索引
        if bug_id in self._bugs:
            self._clear_indices(bug_id)
        
        # 折叠到内存（包括 status='invalid' 的记录）
        self._bugs[bug_id] = bug
        
        # 重建索引
        self._rebuild_indices(bug)
    
    def _clear_indices(self, bug_id: int):
        """清除指定 bug 的所有索引（O(k)，k=该 bug 涉及的索引 key 数）"""
        if bug_id not in self._bug_index_refs:
            return

        refs = self._bug_index_refs.pop(bug_id, {})

        for index_type, keys in refs.items():
            index = getattr(self, f'{index_type}_index', None)
            if index is None:
                continue
            for key in keys:
                if key in index:
                    index[key] = [bid for bid in index[key] if bid != bug_id]
                    if not index[key]:
                        del index[key]

    def _rebuild_indices(self, bug: dict):
        """重建单个 bug 的索引，并维护反向引用（调用方需先清除旧索引）"""
        bug_id = bug.get('id')
        refs = {}

        # 关键词索引
        for kw in bug.get('keywords', []):
            key = kw.lower()
            self.keyword_index[key].append(bug_id)
            refs.setdefault('keyword', []).append(key)

        # 路径索引
        for path in bug.get('paths', []):
            # 支持字符串和对象两种格式
            path_key = path.get('file') if isinstance(path, dict) else path
            self.path_index[path_key].append(bug_id)
            refs.setdefault('path', []).append(path_key)

        # 标签索引
        for tag in bug.get('tags', []):
            key = tag.lower()
            self.tag_index[key].append(bug_id)
            refs.setdefault('tag', []).append(key)

        # Recall pattern 索引
        for pattern in bug.get('recalls', []):
            self.recall_index[pattern].append(bug_id)
            refs.setdefault('recall', []).append(pattern)

        # 注意：impacts 不再存储路径信息，因此不构建 impacts_index
        # get_impacted_bugs() 功能已废弃

        self._bug_index_refs[bug_id] = refs

    def _append_bug(self, bug: dict):
        """保存单个 bug（追加写入）"""
        with open(BUGS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(bug, ensure_ascii=False) + '\n')
        
        # 使用 _fold_bug 处理（包括删除逻辑）
        self._fold_bug(bug)
        
        # 更新 mtime
        try:
            self._mtime = os.path.getmtime(BUGS_FILE)
        except OSError:
            pass
    
    # =========================================================================
    # CRUD 操作
    # =========================================================================
    def add_bug(self, title: str, phenomenon: str, root_cause: Optional[str] = None,
                solution: Optional[str] = None, test_case: Optional[str] = None,
                verified: bool = False, scores: Optional[dict[str, float]] = None,
                paths: Optional[list[str]] = None, tags: Optional[list[str]] = None,
                keywords: Optional[list[str]] = None, recalls: Optional[list[str]] = None,
                status: str = "active", verified_at: Optional[str] = None, verified_by: Optional[str] = None,
                ) -> tuple[int, float]:
        # verified_by 校验：只能是 AI 或 User
        if verified_by is not None and verified_by not in ("AI", "User"):
            raise ValidationError("verified_by 只能是 AI 或 User")
        final_verified_by = verified_by if verified_by else "AI"

        bug_id = generate_id()
        now = datetime.now().isoformat()

        # 验证与状态关联：已验证必然已修复，否则使用传入的 status
        final_status = "resolved" if verified else status
        # verified_at 使用系统时间（不采纳用户传入的）
        final_verified_at = now if verified else None

        bug = {
            "id": bug_id,
            "title": title,
            "phenomenon": phenomenon,
            "root_cause": root_cause,
            "solution": solution,
            "test_case": test_case,
            "verified": verified,
            "verified_at": final_verified_at,
            "verified_by": final_verified_by,
            "status": final_status,
            "scores": dict(scores) if scores else {},
            "paths": list(paths) if paths else [],
            "tags": list(tags) if tags else [],
            "keywords": list(keywords) if keywords else [],
            "recalls": list(recalls) if recalls else [],
            "impacts": [],
            "created_at": now,
            "updated_at": now,
        }
        
        score = _calc_score(bug["scores"])
        bug["score"] = score
        
        self._append_bug(bug)
        return bug_id, score
    
    def update_bug(self, bug_id: int, title: Optional[str] = None,
                   phenomenon: Optional[str] = None, root_cause: Optional[str] = None,
                   solution: Optional[str] = None, test_case: Optional[str] = None,
                   status: Optional[str] = None, verified: Optional[bool] = None,
                   verified_at: Optional[str] = None, verified_by: Optional[str] = None,
                   paths: Optional[list] = None, recalls: Optional[list] = None,
                   scores: Optional[dict] = None, keywords: Optional[list] = None,
                   tags: Optional[list] = None, **kwargs) -> None:
        if status is not None and status not in ("active", "resolved", "invalid"):
            raise ValidationError(f"无效的 status: {status}")
        
        self._ensure_loaded()
        bug = self._bugs.get(bug_id)
        if not bug:
            # Bug 不存在时静默返回
            return
        
        # 自动同步逻辑
        current_verified = bug.get("verified", False)
        current_status = bug.get("status", "active")
        final_verified = verified if verified is not None else current_verified
        final_status = status if status is not None else current_status
        
        if final_verified and final_status == 'active':
            final_status = 'resolved'
            if status is None:
                status = 'resolved'
        elif not final_verified and final_status == 'resolved':
            final_status = 'active'
            if status is None:
                status = 'active'
        
        # 更新字段
        if title is not None:
            bug["title"] = title
        if phenomenon is not None:
            bug["phenomenon"] = phenomenon
        if root_cause is not None:
            bug["root_cause"] = root_cause
        if solution is not None:
            bug["solution"] = solution
        if test_case is not None:
            bug["test_case"] = test_case
        if status is not None:
            bug["status"] = status
        if verified is not None:
            bug["verified"] = verified
        if verified_at is not None:
            if verified_at == "CURRENT_TIMESTAMP":
                bug["verified_at"] = datetime.now().isoformat()
            else:
                bug["verified_at"] = verified_at
        if verified_by is not None:
            bug["verified_by"] = verified_by
        
        # 更新 paths、recalls、scores、keywords、tags
        if paths is not None:
            bug["paths"] = paths
        if recalls is not None:
            bug["recalls"] = recalls
        if scores is not None:
            bug["scores"] = scores
        if keywords is not None:
            bug["keywords"] = keywords
        if tags is not None:
            bug["tags"] = tags
        
        bug["updated_at"] = datetime.now().isoformat()
        
        # 重新计算分数
        bug["score"] = _calc_score(bug.get("scores", {}))
        
        self._append_bug(bug)
    
    def delete_bug(self, bug_id: int) -> None:
        """删除 bug（标记为 invalid）"""
        self._ensure_loaded()
        if bug_id not in self._bugs:
            return
        
        # 标记为失效
        bug = self._bugs[bug_id]
        bug['status'] = 'invalid'
        bug['updated_at'] = datetime.now().isoformat()
        self._append_bug(bug)
    
    def get_bug_detail(self, bug_id: int) -> Optional[dict[str, Any]]:
        self._ensure_loaded()
        bug = self._bugs.get(bug_id)
        if not bug:
            raise ValidationError(f"Bug #{bug_id} 不存在")
        
        # 返回副本，避免外部修改
        return dict(bug)
    
    def list_bugs(self, status: Optional[str] = None, order_by: str = "score",
                  limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        self._ensure_loaded()
        results = list(self._bugs.values())
        
        if status:
            results = [b for b in results if b.get('status') == status]
        
        reverse = True
        if order_by == 'created_at':
            results.sort(key=lambda x: x.get('created_at', ''), reverse=reverse)
        else:
            results.sort(key=lambda x: x.get(order_by, 0), reverse=reverse)
        
        return results[offset:offset+limit]
    
    def count_bugs(self) -> int:
        self._ensure_loaded()
        return len(self._bugs)
    
    def increment_score(self, bug_id: int, dimension: str = "occurrences",
                       delta: float = 1.0) -> None:
        self._ensure_loaded()
        bug = self._bugs.get(bug_id)
        if not bug:
            raise ValidationError(f"Bug #{bug_id} 不存在")
        
        scores = bug.get("scores", {})
        scores[dimension] = scores.get(dimension, 0) + delta
        bug["scores"] = scores
        bug["score"] = _calc_score(scores)
        bug["updated_at"] = datetime.now().isoformat()
        
        self._append_bug(bug)
    
    def update_bug_paths(self, bug_id: int, new_paths: list[str]) -> None:
        self._ensure_loaded()
        bug = self._bugs.get(bug_id)
        if not bug:
            raise ValidationError(f"Bug #{bug_id} 不存在")
        
        bug["paths"] = new_paths
        bug["updated_at"] = datetime.now().isoformat()
        self._append_bug(bug)
    
    def update_bug_recalls(self, bug_id: int, new_recalls: list[str]) -> None:
        self._ensure_loaded()
        bug = self._bugs.get(bug_id)
        if not bug:
            raise ValidationError(f"Bug #{bug_id} 不存在")
        
        bug["recalls"] = new_recalls
        bug["updated_at"] = datetime.now().isoformat()
        self._append_bug(bug)
    
    def add_recall(self, bug_id: int, pattern: str) -> None:
        self._ensure_loaded()
        bug = self._bugs.get(bug_id)
        if not bug:
            raise ValidationError(f"Bug #{bug_id} 不存在")
        
        if pattern not in bug.get("recalls", []):
            bug.setdefault("recalls", []).append(pattern)
            bug["updated_at"] = datetime.now().isoformat()
            self._append_bug(bug)
    
    # =========================================================================
    # 搜索功能
    # =========================================================================
    def search_by_keyword(self, keyword: str, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        keywords = [k.strip().lower() for k in keyword.split() if k.strip()]
        if not keywords:
            return []

        matched_ids = set()

        for kw in keywords:
            # 关键词索引（子串匹配）
            for index_kw, ids in self.keyword_index.items():
                if kw in index_kw or index_kw in kw:
                    matched_ids.update(ids)

            # 标签索引（子串匹配）
            for t, ids in self.tag_index.items():
                if kw in t or t in kw:
                    matched_ids.update(ids)

        results = [self._bugs[bid] for bid in matched_ids if bid in self._bugs]
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
    
    def search_by_tag(self, tag: str, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        tag = tag.lower()
        matched_ids = set()
        
        for t, ids in self.tag_index.items():
            if tag in t or t in tag:
                matched_ids.update(ids)
        
        results = [self._bugs[bid] for bid in matched_ids if bid in self._bugs]
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
    
    def search_recent(self, days: int = 7, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        cutoff = datetime.now().timestamp() - (days * 86400)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()
        
        results = [
            b for b in self._bugs.values()
            if b.get('created_at', '') >= cutoff_iso
        ]
        results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return results[:limit]
    
    def search_high_score(self, min_score: float = 30.0, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        results = [
            b for b in self._bugs.values()
            if b.get('score', 0) >= min_score and b.get('status') != 'invalid'
        ]
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
    
    def search_top_critical(self, limit: int = 20) -> list[dict[str, Any]]:
        self._ensure_loaded()
        results = [
            b for b in self._bugs.values()
            if b.get('status') != 'invalid'
        ]
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
    
    def search_recent_unverified(self, days: int = 7, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        cutoff = datetime.now().timestamp() - (days * 86400)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()
        
        results = [
            b for b in self._bugs.values()
            if (b.get('status') != 'invalid' and
                b.get('created_at', '') >= cutoff_iso)
        ]
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
    
    def search_by_status_and_score(
        self, status: str = "active", min_score: float = 0.0,
        max_score: Optional[float] = None, verified: Optional[bool] = None,
        order_by: str = "score", limit: int = SEARCH_LIMIT,
    ) -> list[dict[str, Any]]:
        self._ensure_loaded()
        results = [b for b in self._bugs.values() if b.get('status') == status]
        
        if min_score > 0:
            results = [b for b in results if b.get('score', 0) >= min_score]
        if max_score is not None:
            results = [b for b in results if b.get('score', 0) <= max_score]
        if verified is not None:
            results = [b for b in results if b.get('verified', False) == verified]
        
        reverse = True
        if order_by == 'created_at':
            results.sort(key=lambda x: x.get('created_at', ''), reverse=reverse)
        else:
            results.sort(key=lambda x: x.get(order_by, 0), reverse=reverse)
        
        return results[:limit]
    
    # =========================================================================
    # 召回功能
    # =========================================================================
    def recall_by_path(self, file_path: str, limit: int = RECALL_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        file_path = _normalize_path(file_path)
        matched_ids = set()
        
        # 路径索引匹配
        for path, ids in self.path_index.items():
            if match_path(file_path, path):
                matched_ids.update(ids)
        
        # Recall pattern 匹配
        for pattern, ids in self.recall_index.items():
            if match_path(file_path, pattern):
                matched_ids.update(ids)
        
        results = [
            self._bugs[bid]
            for bid in matched_ids
            if bid in self._bugs and self._bugs[bid].get('status') != 'invalid'
        ]
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # 限制返回数量，只返回需要的字段
        result_list = []
        for bug in results[:limit]:
            result_list.append({
                "id": bug["id"],
                "title": bug["title"],
                "phenomenon": bug["phenomenon"],
                "score": bug["score"],
                "status": bug["status"],
                "verified": bug.get("verified", False),
                "root_cause": bug.get("root_cause"),
                "solution": bug.get("solution"),
                "test_case": bug.get("test_case"),
            })
        return result_list
    
    def recall_by_pattern(self, pattern: str, limit: int = RECALL_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        pattern_norm = _normalize_path(pattern)
        matched_ids = set()
        
        for stored_pattern, ids in self.recall_index.items():
            if (match_path(pattern_norm, stored_pattern) or
                match_path(stored_pattern, pattern_norm)):
                matched_ids.update(ids)
        
        results = [
            self._bugs[bid]
            for bid in matched_ids
            if bid in self._bugs and self._bugs[bid].get('status') != 'invalid'
        ]
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        result_list = []
        for bug in results[:limit]:
            result_list.append({
                "id": bug["id"],
                "title": bug["title"],
                "phenomenon": bug["phenomenon"],
                "score": bug["score"],
                "status": bug["status"],
                "verified": bug.get("verified", False),
                "root_cause": bug.get("root_cause"),
                "solution": bug.get("solution"),
                "test_case": bug.get("test_case"),
            })
        return result_list
    
    def recall_by_path_full(self, file_path: str, limit: int = RECALL_LIMIT) -> dict[str, Any]:
        impacted_by = self.get_impacted_bugs(file_path, limit)
        related_bugs = self.recall_by_path(file_path, limit)
        
        # 批量查询 impacts
        for bug in related_bugs:
            bug["impacts"] = self.get_bug_impacts(bug["id"])
        
        return {"impacted_by": impacted_by, "related_bugs": related_bugs}
    
    # =========================================================================
    # 影响关系
    # =========================================================================
    def add_impact(self, source_bug_id: int,
                   solution_change: str,
                   impact_description: str,
                   impact_type: str = "regression",
                   severity: int = 5,
                   prevention_delta: float = 3.0) -> int:
        if impact_type not in ("regression", "side_effect", "dependency"):
            raise ValidationError(f"无效的影响类型: {impact_type}")
        if not (0 <= severity <= 10):
            raise ValidationError(f"严重程度必须在 0-10 之间: {severity}")

        self._ensure_loaded()
        if source_bug_id not in self._bugs:
            raise ValidationError(f"Bug #{source_bug_id} 不存在")

        impact_id = generate_id()
        impact = {
            "id": impact_id,
            "solution_change": solution_change,
            "impact_description": impact_description,
            "impact_type": impact_type,
            "severity": severity,
            "created_at": datetime.now().isoformat(),
        }

        bug = self._bugs[source_bug_id]
        bug.setdefault("impacts", []).append(impact)
        bug["updated_at"] = datetime.now().isoformat()
        self._append_bug(bug)

        # 自动累加 prevention 分数（delta 由调用方根据 severity 规则计算传入）
        self.increment_score(source_bug_id, "prevention", prevention_delta)

        return impact_id

    def delete_impact(self, impact_id: int, prevention_delta: float) -> None:
        self._ensure_loaded()

        for bug_id, bug in self._bugs.items():
            impacts = bug.get("impacts", [])
            bug["impacts"] = [i for i in impacts if i.get("id") != impact_id]
            if len(bug["impacts"]) < len(impacts):
                bug["updated_at"] = datetime.now().isoformat()
                self._append_bug(bug)
                # 扣减 prevention 分数（delta 为正值，内部取负）
                self.increment_score(bug_id, "prevention", -prevention_delta)
                return
    
    def get_impacted_bugs(self, file_path: str, limit: int = RECALL_LIMIT) -> list[dict[str, Any]]:
        """
        此方法已废弃：impacts 数据结构已改为记录解决方案变更的影响，不再关联路径。
        请使用 recall_by_path() 或 search_bugs(mode='module') 进行路径相关召回。
        """
        return []
    
    def get_bug_impacts(self, bug_id: int) -> list[dict[str, Any]]:
        self._ensure_loaded()
        bug = self._bugs.get(bug_id)
        if not bug:
            return []
        
        impacts = bug.get("impacts", [])
        return [
            {
                "solution_change": imp["solution_change"],
                "impact_description": imp["impact_description"],
                "impact_type": imp["impact_type"],
                "severity": imp["severity"],
            }
            for imp in sorted(impacts, key=lambda x: x["severity"], reverse=True)
        ]
    
    def compact_file(self) -> int:
        """压缩文件：移除 status='invalid' 的记录，相同ID只保留最后一条
        
        Returns:
            清理的记录数量（被移除的旧记录数）
        """
        self._ensure_loaded()
        
        # 统计原始行数
        original_count = 0
        with open(BUGS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    original_count += 1
        
        # 重写文件：只保留每个 bug_id 的最后一条记录（且 status != 'invalid'）
        temp_file = BUGS_FILE.with_suffix('.jsonl.tmp')
        written_count = 0
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            for bug in self._bugs.values():
                # 跳过已失效的
                if bug.get('status') == 'invalid':
                    continue
                f.write(json.dumps(bug, ensure_ascii=False) + '\n')
                written_count += 1
        
        # 原子替换原文件
        temp_file.replace(BUGS_FILE)
        
        # 重新加载（mtime 已变化）
        self._load_data()
        
        removed_count = original_count - written_count
        return max(0, removed_count)

    def update_impacted_paths(self, old_path: str, new_path: str) -> int:
        """此方法已废弃：impacts 不再存储路径信息"""
        return 0

    # =========================================================================
    # 高级功能
    # =========================================================================
    def mark_invalid(self, bug_id: int, reason: Optional[str] = None) -> None:
        self._ensure_loaded()
        bug = self._bugs.get(bug_id)
        if not bug:
            # Bug 不存在时静默返回
            return
        
        if reason:
            existing_solution = bug.get("solution", "") or ""
            bug["solution"] = existing_solution + f"\n[已失效原因] {reason}"
        
        bug["status"] = "invalid"
        bug["updated_at"] = datetime.now().isoformat()
        bug["score"] = _calc_score(bug.get("scores", {}))
        self._append_bug(bug)
    
    def list_unverified_old(self, days: int = THRESHOLD_OLD_BUGS_DAYS, limit: int = 20) -> list[dict[str, Any]]:
        self._ensure_loaded()
        cutoff = datetime.now().timestamp() - (days * 86400)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()
        
        results = [
            b for b in self._bugs.values()
            if (not b.get('verified', False) and
                b.get('status') != 'invalid' and
                b.get('created_at', '') < cutoff_iso)
        ]
        results.sort(key=lambda x: x.get('created_at', ''))
        
        result_list = []
        for bug in results[:limit]:
            result_list.append({
                "id": bug["id"],
                "title": bug["title"],
                "phenomenon": bug["phenomenon"],
                "score": bug["score"],
                "created_at": bug["created_at"],
            })
        return result_list
    
    def check_path_valid(self, path: str, root: Optional[Path] = None) -> bool:
        root = root or find_project_root()
        if path.endswith("/*"):
            # 通配符路径：去掉 /* 检查目录是否存在
            abs_path = root / path[:-2]
            return abs_path.exists() and abs_path.is_dir()
        abs_path = root / path
        return abs_path.exists()
    
    def check_bug_paths(self, bug_id: int) -> list[str]:
        """检查 bug 的 paths/recalls 路径是否有效，返回无效路径列表"""
        self._ensure_loaded()
        bug = self._bugs.get(bug_id)
        if not bug:
            return []

        invalid_paths = []

        # 检查 paths 和 recalls
        for path in bug.get("paths", []) + bug.get("recalls", []):
            # paths 可能是字符串或对象格式
            if isinstance(path, dict):
                path_str = path.get('file', '')
            else:
                path_str = path
            
            if not self.check_path_valid(path_str):
                invalid_paths.append(path_str)

        return invalid_paths

    def migrate_bug_paths_after_refactor(self, old_path: str, new_path: str) -> list[int]:
        """路径迁移：只处理 paths 和 recalls，impacts 不再存储路径"""
        migrated_bugs = []
        
        affected_bugs = self.recall_by_path(old_path)
        
        for bug_summary in affected_bugs:
            bug_id = bug_summary["id"]
            bug = self._bugs.get(bug_id)
            if not bug:
                continue
            
            updated = False
            old_path_norm = _normalize_path(old_path)
            new_path_norm = _normalize_path(new_path)
            
            # 更新 paths（对象格式）
            current_paths = bug.get("paths", [])
            new_paths = []
            for p in current_paths:
                if isinstance(p, dict) and p.get('file') == old_path_norm:
                    # 替换为新路径，保留 functions
                    new_paths.append({
                        'file': new_path_norm,
                        'functions': p.get('functions', [])
                    })
                    updated = True
                else:
                    new_paths.append(p)
            
            if updated:
                bug["paths"] = new_paths
            
            # 更新 recalls
            current_recalls = bug.get("recalls", [])
            matched_recalls = [r for r in current_recalls if match_path(old_path_norm, r)]
            if matched_recalls:
                updated_recalls = []
                for r in current_recalls:
                    if r in matched_recalls:
                        if r.endswith("/*"):
                            base_dir = "/".join(new_path_norm.split("/")[:-1])
                            updated_recalls.append(f"{base_dir}/*")
                        else:
                            updated_recalls.append(new_path_norm)
                    else:
                        updated_recalls.append(r)
                bug["recalls"] = updated_recalls
                updated = True
            
            if updated:
                bug["updated_at"] = datetime.now().isoformat()
                self._append_bug(bug)
                migrated_bugs.append(bug_id)
        
        return list(set(migrated_bugs))
    
    # -------------------- 重构后的新接口实现 --------------------
    
    def save_bugs(self, bugs_data) -> Any:
        """统一保存接口（支持多种 mode，支持批量）"""
        import json

        # 标准化输入：统一为数组格式
        if isinstance(bugs_data, dict):
            if 'bugs' in bugs_data:
                bugs_list = bugs_data['bugs']
            else:
                # 单个 bug 操作（dict 格式）
                bugs_list = [bugs_data]
        elif isinstance(bugs_data, list):
            bugs_list = bugs_data
        else:
            return {'error': '无效的输入格式', 'isError': True}

        results = []
        for bug_data in bugs_list:
            result = self._save_bug(**bug_data)
            if isinstance(result, dict) and result.get('isError'):
                return result  # 直接返回错误
            results.append(result)

        return {
            'content': [{'type': 'text', 'text': json.dumps({'results': results, 'count': len(results)}, ensure_ascii=False)}]
        }

    def _save_bug(self, **kwargs) -> dict:
        """保存单个 bug"""
        import json
        
        try:
            mode = kwargs.get('mode', 'add')
            
            if mode == 'add':
                # === 新增 ===
                # add 模式不能传 id，必须由系统自动生成
                if 'id' in kwargs:
                    return {'error': '新增 bug 时不能传 id，id 由系统自动生成', 'isError': True}

                required_fields = ['title', 'phenomenon']
                for field in required_fields:
                    if field not in kwargs:
                        return {'error': f'新增 bug 时，{field} 为必填字段', 'isError': True}
                
                # 转换 paths 格式（字符串数组 -> 对象数组）
                add_kwargs = {k: v for k, v in kwargs.items()
                              if k not in ('mode', 'id', 'verified_at')}
                if 'paths' in add_kwargs and isinstance(add_kwargs['paths'], list):
                    # 如果 paths 是字符串数组，转换为对象格式
                    if add_kwargs['paths'] and isinstance(add_kwargs['paths'][0], str):
                        add_kwargs['paths'] = [{'file': p, 'functions': []} for p in add_kwargs['paths']]
                
                bug_id, score = self.add_bug(**add_kwargs)
                return {'id': bug_id}
            
            else:
                # === 更新 ===
                bug_id = kwargs.get('id')
                if not bug_id:
                    return {'error': '更新操作必须提供 bug id', 'isError': True}
                
                # 检查 ID 是否存在
                existing = self.get_bug_detail(bug_id)
                if not existing:
                    return {'error': f'Bug #{bug_id} 不存在', 'isError': True}
                
                if mode == 'update_fields':
                    update_data = {k: v for k, v in kwargs.items() if k not in ('id', 'mode') and v is not None}
                    if not update_data:
                        return {'error': "❌ 错误：update_fields 模式至少需要传一个要更新的字段", 'isError': True}
                    self.update_bug(bug_id, **update_data)
                
                elif mode == 'delete':
                    # 软删除：设置 status='invalid'
                    self.update_bug(bug_id, status='invalid')
                
                elif mode == 'add_impacts':
                    if 'impacts' not in kwargs:
                        return {'error': "❌ 错误：add_impacts 模式必须传 impacts", 'isError': True}
                    for impact in kwargs['impacts']:
                        self.add_impact(bug_id, **impact)
                
                elif mode == 'remove_impacts':
                    if 'impact_ids' not in kwargs:
                        return {'error': "❌ 错误：remove_impacts 模式必须传 impact_ids", 'isError': True}
                    # 批量删除
                    for impact_id in kwargs['impact_ids']:
                        self.delete_impact(impact_id, prevention_delta=0)
                
                elif mode == 'replace_impacts':
                    if 'impacts' not in kwargs:
                        return {'error': "❌ 错误：replace_impacts 模式必须传 impacts", 'isError': True}
                    old_bug = self.get_bug_detail(bug_id)
                    for impact in old_bug.get('impacts', []):
                        self.delete_impact(impact['id'], prevention_delta=0)
                    for impact in kwargs['impacts']:
                        self.add_impact(bug_id, **impact)
                
                elif mode == 'add_paths':
                    if 'paths' not in kwargs:
                        return {'error': "❌ 错误：add_paths 模式必须传 paths", 'isError': True}
                    old_bug = self.get_bug_detail(bug_id)
                    
                    # 构建旧 paths 的 file -> path 映射
                    old_paths_map = {}
                    for p in old_bug.get('paths', []):
                        if isinstance(p, dict):
                            old_paths_map[p.get('file')] = p
                        else:
                            old_paths_map[p] = {'file': p, 'functions': []}
                    
                    # 合并新 paths（相同 file 则合并 functions）
                    for new_p in kwargs['paths']:
                        if isinstance(new_p, dict):
                            file = new_p.get('file')
                            if file in old_paths_map:
                                # 合并 functions（去重）
                                old_funcs = set(old_paths_map[file].get('functions', []))
                                new_funcs = set(new_p.get('functions', []))
                                old_paths_map[file]['functions'] = list(old_funcs | new_funcs)
                            else:
                                old_paths_map[file] = new_p
                        else:
                            # 字符串格式，直接添加
                            if new_p not in old_paths_map:
                                old_paths_map[new_p] = {'file': new_p, 'functions': []}
                    
                    merged_paths = list(old_paths_map.values())
                    self.update_bug(bug_id, paths=merged_paths)
                
                elif mode == 'remove_paths':
                    if 'paths' not in kwargs:
                        return {'error': "❌ 错误：remove_paths 模式必须传 paths", 'isError': True}
                    old_bug = self.get_bug_detail(bug_id)
                    remove_paths = kwargs['paths']
                    
                    # 构建要移除的映射: {file: set(functions) or None}
                    remove_map = {}
                    for p in remove_paths:
                        if isinstance(p, dict):
                            file = p.get('file')
                            funcs = p.get('functions', [])
                            if funcs:
                                # 有 functions，只移除这些函数
                                remove_map.setdefault(file, set()).update(funcs)
                            else:
                                # 无 functions，标记删除整个 file
                                remove_map[file] = None
                        else:
                            # 字符串格式，删除整个 file
                            remove_map[p] = None
                    
                    # 执行移除
                    filtered_paths = []
                    for p in old_bug.get('paths', []):
                        if isinstance(p, dict):
                            file = p.get('file')
                            funcs = p.get('functions', [])
                            
                            if file in remove_map:
                                if remove_map[file] is None:
                                    # 删除整个 file
                                    continue
                                else:
                                    # 只移除指定 functions
                                    remaining_funcs = [f for f in funcs if f not in remove_map[file]]
                                    if remaining_funcs:
                                        filtered_paths.append({'file': file, 'functions': remaining_funcs})
                                    # 如果 functions 全被移除，则不添加（相当于删除该 path）
                            else:
                                filtered_paths.append(p)
                        else:
                            # 字符串格式
                            if p not in remove_map:
                                filtered_paths.append(p)
                    
                    self.update_bug(bug_id, paths=filtered_paths)
                
                elif mode == 'replace_paths':
                    if 'paths' not in kwargs:
                        return {'error': "❌ 错误：replace_paths 模式必须传 paths", 'isError': True}
                    self.update_bug(bug_id, paths=kwargs['paths'])
                
                elif mode == 'add_recalls':
                    if 'recalls' not in kwargs:
                        return {'error': "❌ 错误：add_recalls 模式必须传 recalls", 'isError': True}
                    old_bug = self.get_bug_detail(bug_id)
                    merged_recalls = list(set((old_bug.get('recalls') or []) + kwargs['recalls']))
                    self.update_bug(bug_id, recalls=merged_recalls)
                
                elif mode == 'remove_recalls':
                    if 'recalls' not in kwargs:
                        return {'error': "❌ 错误：remove_recalls 模式必须传 recalls", 'isError': True}
                    old_bug = self.get_bug_detail(bug_id)
                    filtered_recalls = [r for r in (old_bug.get('recalls') or []) if r not in kwargs['recalls']]
                    self.update_bug(bug_id, recalls=filtered_recalls)
                
                elif mode == 'replace_recalls':
                    if 'recalls' not in kwargs:
                        return {'error': "❌ 错误：replace_recalls 模式必须传 recalls", 'isError': True}
                    self.update_bug(bug_id, recalls=kwargs['recalls'])
                
                elif mode == 'add_keywords':
                    if 'keywords' not in kwargs:
                        return {'error': "❌ 错误：add_keywords 模式必须传 keywords", 'isError': True}
                    old_bug = self.get_bug_detail(bug_id)
                    merged_keywords = list(set((old_bug.get('keywords') or []) + kwargs['keywords']))
                    self.update_bug(bug_id, **{'keywords': merged_keywords})
                
                elif mode == 'remove_keywords':
                    if 'keywords' not in kwargs:
                        return {'error': "❌ 错误：remove_keywords 模式必须传 keywords", 'isError': True}
                    old_bug = self.get_bug_detail(bug_id)
                    filtered_keywords = [k for k in (old_bug.get('keywords') or []) if k not in kwargs['keywords']]
                    self.update_bug(bug_id, **{'keywords': filtered_keywords})
                
                elif mode == 'replace_keywords':
                    if 'keywords' not in kwargs:
                        return {'error': "❌ 错误：replace_keywords 模式必须传 keywords", 'isError': True}
                    self.update_bug(bug_id, **{'keywords': kwargs['keywords']})
                
                elif mode == 'add_tags':
                    if 'tags' not in kwargs:
                        return {'error': "❌ 错误：add_tags 模式必须传 tags", 'isError': True}
                    old_bug = self.get_bug_detail(bug_id)
                    merged_tags = list(set((old_bug.get('tags') or []) + kwargs['tags']))
                    self.update_bug(bug_id, **{'tags': merged_tags})
                
                elif mode == 'remove_tags':
                    if 'tags' not in kwargs:
                        return {'error': "❌ 错误：remove_tags 模式必须传 tags", 'isError': True}
                    old_bug = self.get_bug_detail(bug_id)
                    filtered_tags = [t for t in (old_bug.get('tags') or []) if t not in kwargs['tags']]
                    self.update_bug(bug_id, **{'tags': filtered_tags})
                
                elif mode == 'replace_tags':
                    if 'tags' not in kwargs:
                        return {'error': "❌ 错误：replace_tags 模式必须传 tags", 'isError': True}
                    self.update_bug(bug_id, **{'tags': kwargs['tags']})
                
                elif mode == 'increment_scores':
                    if 'scores' not in kwargs:
                        return {'error': "❌ 错误：increment_scores 模式必须传 scores", 'isError': True}
                    old_bug = self.get_bug_detail(bug_id)
                    merged_scores = dict(old_bug.get('scores') or {})
                    for dim, delta in kwargs['scores'].items():
                        merged_scores[dim] = merged_scores.get(dim, 0) + delta
                    self.update_bug(bug_id, scores=merged_scores)
                
                elif mode == 'decrement_scores':
                    if 'scores' not in kwargs:
                        return {'error': "❌ 错误：decrement_scores 模式必须传 scores", 'isError': True}
                    old_bug = self.get_bug_detail(bug_id)
                    merged_scores = dict(old_bug.get('scores') or {})
                    for dim, delta in kwargs['scores'].items():
                        merged_scores[dim] = merged_scores.get(dim, 0) - delta
                    self.update_bug(bug_id, scores=merged_scores)
                
                elif mode == 'replace_scores':
                    if 'scores' not in kwargs:
                        return {'error': "❌ 错误：replace_scores 模式必须传 scores", 'isError': True}
                    self.update_bug(bug_id, scores=kwargs['scores'])
                
                return {'id': bug_id}
        
        except Exception as e:
            return {'error': f"❌ 服务器错误：{str(e)}", 'isError': True}
    
    def search_bugs(self, **kwargs) -> dict[str, Any]:
        """统一搜索接口（支持多种模式 + 分页）"""
        mode = kwargs.get('mode')
        limit = kwargs.get('limit', 20)
        offset = kwargs.get('offset', 0)
        
        # 根据 mode 路由到不同的搜索方法
        if mode == 'keyword':
            bugs = self.search_by_keyword(kwargs['keyword'], limit=limit + offset)
        elif mode == 'tag':
            bugs = self.search_by_tag(kwargs['tag'], limit=limit + offset)
        elif mode == 'recent':
            bugs = self.search_recent(kwargs.get('days', 7), limit=limit + offset)
        elif mode == 'high_score':
            bugs = self.search_high_score(kwargs.get('min_score', 30.0), limit=limit + offset)
        elif mode == 'critical':
            bugs = self.search_top_critical(limit=limit + offset)
        elif mode == 'unverified':
            bugs = self.search_recent_unverified(kwargs.get('days', 7), limit=limit + offset)
        elif mode == 'custom':
            bugs = self.search_by_status_and_score(
                status=kwargs.get('status', 'active'),
                min_score=kwargs.get('min_score', 0.0),
                max_score=kwargs.get('max_score'),
                verified=kwargs.get('verified'),
                order_by=kwargs.get('order_by', 'score'),
                limit=limit + offset
            )
        elif mode == 'module':
            bugs = self.recall_by_pattern(kwargs['pattern'], limit=limit + offset)
        else:
            raise ValueError(f"Unknown search mode: {mode}")
        
        # 应用分页
        total = len(bugs)
        paginated_bugs = bugs[offset:offset + limit]
        has_more = offset + limit < total
        
        return {
            'bugs': paginated_bugs,
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': has_more
            }
        }
    

