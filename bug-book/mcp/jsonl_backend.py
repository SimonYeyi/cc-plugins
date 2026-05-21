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

from bug_backend import BugBackend
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


class ValidationError(Exception):
    """校验失败"""
    pass


class JSONLBackend(BugBackend):
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
        self.module_pattern_index = defaultdict(list)
        self.impacts_index = defaultdict(list)

        # 反向索引：bug_id → {index_type: [keys...]}，用于 O(1) 清除索引
        self._bug_index_refs = {}          # bug_id → {type: [keys...]}

        # 初始化数据
        self._ensure_loaded()

    # =========================================================================
    # 公共接口（10个）- 按 bug_backend.py 声明顺序
    # =========================================================================
    
    def get_bug(self, bug_id: int) -> Optional[dict[str, Any]]:
        self._ensure_loaded()
        bug = self._bugs.get(bug_id)
        if not bug:
            raise ValidationError(f"Bug #{bug_id} 不存在")
        
        # 返回副本，避免外部修改
        return dict(bug)
    
    def get_all_bugs(self) -> dict[int, dict[str, Any]]:
        """获取所有 bugs（用于遍历）"""
        self._ensure_loaded()
        return dict(self._bugs)
    
    def find_by_path(self, file_path: str, limit: int = RECALL_LIMIT) -> list[dict[str, Any]]:
        """按路径查询（利用索引）"""
        self._ensure_loaded()
        file_path = normalize_path(file_path)
        matched_ids = set()
        
        # 路径索引匹配
        for path, ids in self.path_index.items():
            if match_path(file_path, path):
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
                "paths": bug.get("paths", []),
                "impacts": bug.get("impacts", []),
            })
        return result_list
    
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
        self.module_pattern_index.clear()
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

        # Module pattern 索引
        for pattern in bug.get('module_patterns', []):
            self.module_pattern_index[pattern].append(bug_id)
            refs.setdefault('module_pattern', []).append(pattern)

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
    # CRUD 操作（私有方法）
    # =========================================================================
    def add_bug(self, title: str, phenomenon: str, root_cause: Optional[str] = None,
                solution: Optional[str] = None, test_case: Optional[str] = None,
                verified: bool = False, scores: Optional[dict[str, float]] = None,
                paths: Optional[list[str]] = None, tags: Optional[list[str]] = None,
                keywords: Optional[list[str]] = None, module_patterns: Optional[list[str]] = None,
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
            "module_patterns": list(module_patterns) if module_patterns else [],
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
                   paths: Optional[list] = None, module_patterns: Optional[list] = None,
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
        
        # 更新 paths、module_patterns、scores、keywords、tags
        if paths is not None:
            bug["paths"] = paths
        if module_patterns is not None:
            bug["module_patterns"] = module_patterns
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
    
    def count_bugs(self) -> int:
        self._ensure_loaded()
        return len(self._bugs)
    
    def _increment_score(self, bug_id: int, dimension: str = "occurrences",
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
    
    # =========================================================================
    # 查询功能（私有方法）
    # =========================================================================
    def find_by_keyword(self, keyword: str, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
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
    
    def find_by_tag(self, tag: str, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        tag = tag.lower()
        matched_ids = set()
        
        for t, ids in self.tag_index.items():
            if tag in t or t in tag:
                matched_ids.update(ids)
        
        results = [self._bugs[bid] for bid in matched_ids if bid in self._bugs]
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
    
    def find_by_created_after(self, days: int = 7, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        cutoff = datetime.now().timestamp() - (days * 86400)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()
        
        results = [
            b for b in self._bugs.values()
            if b.get('created_at', '') >= cutoff_iso
        ]
        results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return results[:limit]
    
    def find_by_min_score(self, min_score: float = 30.0, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        results = [
            b for b in self._bugs.values()
            if b.get('score', 0) >= min_score and b.get('status') != 'invalid'
        ]
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
    
    def find_all_sorted(self, limit: int = 20) -> list[dict[str, Any]]:
        self._ensure_loaded()
        results = [
            b for b in self._bugs.values()
            if b.get('status') != 'invalid'
        ]
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
    
    def find_unverified_since(self, days: int = SEARCH_LIMIT, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        cutoff = datetime.now().timestamp() - (days * 86400)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()

        results = [
            b for b in self._bugs.values()
            if (b.get('status') != 'invalid' and
                not b.get('verified', False) and
                b.get('created_at', '') >= cutoff_iso)
        ]
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
    
    def query(
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
    
    def find_by_pattern(self, pattern: str, limit: int = RECALL_LIMIT) -> list[dict[str, Any]]:
        self._ensure_loaded()
        pattern_norm = normalize_path(pattern)
        matched_ids = set()
        
        for stored_pattern, ids in self.module_pattern_index.items():
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
                "paths": bug.get("paths", []),
                "impacts": bug.get("impacts", []),
            })
        return result_list

    # =========================================================================
    # 影响关系（私有方法）
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
        self._increment_score(source_bug_id, "prevention", prevention_delta)

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
                self._increment_score(bug_id, "prevention", -prevention_delta)
                return

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

    # =========================================================================
    # 高级功能（私有方法）
    # =========================================================================
    def find_unverified_old(self, days: int = THRESHOLD_OLD_BUGS_DAYS, limit: int = 20) -> list[dict[str, Any]]:
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
    
