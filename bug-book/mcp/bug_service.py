#!/usr/bin/env python3
"""Bug Service - 业务编排层，为 MCP Server 提供门面接口"""

from typing import Any, Optional
from backend_factory import create_backend
from config import find_project_root


class BugService:
    """Bug 业务服务层
    
    职责：
    - 参数校验
    - Mode 路由（save_bugs 的多 mode 分发）
    - 批量操作编排
    - 业务规则（如 verified→resolved 自动同步）
    
    不负责：
    - MCP 协议格式封装
    - 数据存储实现（内部使用 JSONLBackend）
    """
    
    def __init__(self):
        self.backend = create_backend()
    
    # ==================== 统一保存（带 mode 路由）====================
    
    def save_bugs(self, bugs_data) -> dict:
        """统一保存接口，支持多种 mode
        
        Args:
            bugs_data: 单个 bug dict、数组或 {'bugs': [...]} 格式
            
        Returns:
            {'results': [...], 'count': N}
        """
        # 标准化输入为数组
        if isinstance(bugs_data, dict):
            if 'bugs' in bugs_data:
                bugs_list = bugs_data['bugs']
            else:
                bugs_list = [bugs_data]
        elif isinstance(bugs_data, list):
            bugs_list = bugs_data
        else:
            raise ValueError('无效的输入格式')
        
        results = []
        for bug_data in bugs_list:
            result = self._save_single_bug(**bug_data)
            results.append(result)
        
        return {'results': results, 'count': len(results)}
    
    def _save_single_bug(self, **kwargs) -> dict:
        """保存单个 bug（mode 路由）"""
        mode = kwargs.get('mode', 'add')
        
        if mode == 'add':
            return self._handle_add(kwargs)
        else:
            return self._handle_update(mode, kwargs)
    
    def _handle_add(self, kwargs: dict) -> dict:
        """处理 add mode"""
        # add 模式不能传 id
        if 'id' in kwargs:
            raise ValueError('新增 bug 时不能传 id，id 由系统自动生成')
        
        # 必填字段校验
        required_fields = ['title', 'phenomenon']
        for field in required_fields:
            if field not in kwargs:
                raise ValueError(f'新增 bug 时，{field} 为必填字段')
        
        # 转换 paths 格式（字符串数组 → 对象数组）
        add_kwargs = {k: v for k, v in kwargs.items() 
                      if k not in ('mode', 'id', 'verified_at')}
        if 'paths' in add_kwargs and isinstance(add_kwargs['paths'], list):
            if add_kwargs['paths'] and isinstance(add_kwargs['paths'][0], str):
                add_kwargs['paths'] = [{'file': p, 'functions': []} for p in add_kwargs['paths']]
        
        bug_id, score = self.backend.add_bug(**add_kwargs)
        return {'id': bug_id}
    
    def _handle_update(self, mode: str, kwargs: dict) -> dict:
        """处理更新类 mode"""
        bug_id = kwargs.get('id')
        if not bug_id:
            raise ValueError('更新操作必须提供 bug id')
        
        # 检查 ID 是否存在
        existing = self.backend.get_bug(bug_id)
        if not existing:
            raise ValueError(f'Bug #{bug_id} 不存在')
        
        # Mode 路由
        handlers = {
            'update_fields': self._update_fields,
            'delete': self._delete_bug,
            'add_impacts': self._add_impacts,
            'remove_impacts': self._remove_impacts,
            'replace_impacts': self._replace_impacts,
            'add_paths': self._add_paths,
            'remove_paths': self._remove_paths,
            'replace_paths': self._replace_paths,
            'add_module_patterns': self._add_module_patterns,
            'remove_module_patterns': self._remove_module_patterns,
            'replace_module_patterns': self._replace_module_patterns,
            'add_keywords': self._add_keywords,
            'remove_keywords': self._remove_keywords,
            'replace_keywords': self._replace_keywords,
            'add_tags': self._add_tags,
            'remove_tags': self._remove_tags,
            'replace_tags': self._replace_tags,
            'increment_scores': self._increment_scores,
            'decrement_scores': self._decrement_scores,
            'replace_scores': self._replace_scores,
        }
        
        handler = handlers.get(mode)
        if not handler:
            raise ValueError(f'未知的 mode: {mode}')
        
        handler(bug_id, kwargs)
        return {'id': bug_id}
    
    # ==================== 更新类 mode 处理器 ====================
    
    def _update_fields(self, bug_id: int, kwargs: dict):
        update_data = {k: v for k, v in kwargs.items() 
                       if k not in ('id', 'mode') and v is not None}
        if not update_data:
            raise ValueError("update_fields 模式至少需要传一个要更新的字段")
        self.backend.update_bug(bug_id, **update_data)
    
    def _delete_bug(self, bug_id: int, kwargs: dict):
        self.backend.update_bug(bug_id, status='invalid')
    
    def _add_impacts(self, bug_id: int, kwargs: dict):
        if 'impacts' not in kwargs:
            raise ValueError("add_impacts 模式必须传 impacts")
        for impact in kwargs['impacts']:
            self.backend.add_impact(bug_id, **impact)
    
    def _remove_impacts(self, bug_id: int, kwargs: dict):
        if 'impact_ids' not in kwargs:
            raise ValueError("remove_impacts 模式必须传 impact_ids")
        for impact_id in kwargs['impact_ids']:
            self.backend.delete_impact(impact_id, prevention_delta=0)
    
    def _replace_impacts(self, bug_id: int, kwargs: dict):
        if 'impacts' not in kwargs:
            raise ValueError("replace_impacts 模式必须传 impacts")
        old_bug = self.backend.get_bug(bug_id)
        for impact in old_bug.get('impacts', []):
            self.backend.delete_impact(impact['id'], prevention_delta=0)
        for impact in kwargs['impacts']:
            self.backend.add_impact(bug_id, **impact)
    
    def _add_paths(self, bug_id: int, kwargs: dict):
        if 'paths' not in kwargs:
            raise ValueError("add_paths 模式必须传 paths")
        old_bug = self.backend.get_bug(bug_id)
        
        # 构建旧 paths 映射
        old_paths_map = {}
        for p in old_bug.get('paths', []):
            if isinstance(p, dict):
                old_paths_map[p.get('file')] = p
            else:
                old_paths_map[p] = {'file': p, 'functions': []}
        
        # 合并新 paths
        for new_p in kwargs['paths']:
            if isinstance(new_p, dict):
                file = new_p.get('file')
                if file in old_paths_map:
                    old_funcs = set(old_paths_map[file].get('functions', []))
                    new_funcs = set(new_p.get('functions', []))
                    old_paths_map[file]['functions'] = list(old_funcs | new_funcs)
                else:
                    old_paths_map[file] = new_p
            else:
                if new_p not in old_paths_map:
                    old_paths_map[new_p] = {'file': new_p, 'functions': []}
        
        merged_paths = list(old_paths_map.values())
        self.backend.update_bug(bug_id, paths=merged_paths)
    
    def _remove_paths(self, bug_id: int, kwargs: dict):
        if 'paths' not in kwargs:
            raise ValueError("remove_paths 模式必须传 paths")
        old_bug = self.backend.get_bug(bug_id)
        remove_paths = kwargs['paths']
        
        # 构建移除映射
        remove_map = {}
        for p in remove_paths:
            if isinstance(p, dict):
                file = p.get('file')
                funcs = p.get('functions', [])
                if funcs:
                    remove_map.setdefault(file, set()).update(funcs)
                else:
                    remove_map[file] = None
            else:
                remove_map[p] = None
        
        # 执行移除
        filtered_paths = []
        for p in old_bug.get('paths', []):
            if isinstance(p, dict):
                file = p.get('file')
                funcs = p.get('functions', [])
                
                if file in remove_map:
                    if remove_map[file] is None:
                        continue
                    else:
                        remaining_funcs = [f for f in funcs if f not in remove_map[file]]
                        if remaining_funcs:
                            filtered_paths.append({'file': file, 'functions': remaining_funcs})
                else:
                    filtered_paths.append(p)
            else:
                if p not in remove_map:
                    filtered_paths.append(p)
        
        self.backend.update_bug(bug_id, paths=filtered_paths)
    
    def _replace_paths(self, bug_id: int, kwargs: dict):
        if 'paths' not in kwargs:
            raise ValueError("replace_paths 模式必须传 paths")
        self.backend.update_bug(bug_id, paths=kwargs['paths'])
    
    def _add_module_patterns(self, bug_id: int, kwargs: dict):
        if 'module_patterns' not in kwargs:
            raise ValueError("add_module_patterns 模式必须传 module_patterns")
        old_bug = self.backend.get_bug(bug_id)
        merged = list(set((old_bug.get('module_patterns') or []) + kwargs['module_patterns']))
        self.backend.update_bug(bug_id, module_patterns=merged)
    
    def _remove_module_patterns(self, bug_id: int, kwargs: dict):
        if 'module_patterns' not in kwargs:
            raise ValueError("remove_module_patterns 模式必须传 module_patterns")
        old_bug = self.backend.get_bug(bug_id)
        filtered = [r for r in (old_bug.get('module_patterns') or []) 
                    if r not in kwargs['module_patterns']]
        self.backend.update_bug(bug_id, module_patterns=filtered)
    
    def _replace_module_patterns(self, bug_id: int, kwargs: dict):
        if 'module_patterns' not in kwargs:
            raise ValueError("replace_module_patterns 模式必须传 module_patterns")
        self.backend.update_bug(bug_id, module_patterns=kwargs['module_patterns'])
    
    def _add_keywords(self, bug_id: int, kwargs: dict):
        if 'keywords' not in kwargs:
            raise ValueError("add_keywords 模式必须传 keywords")
        old_bug = self.backend.get_bug(bug_id)
        merged = list(set((old_bug.get('keywords') or []) + kwargs['keywords']))
        self.backend.update_bug(bug_id, keywords=merged)
    
    def _remove_keywords(self, bug_id: int, kwargs: dict):
        if 'keywords' not in kwargs:
            raise ValueError("remove_keywords 模式必须传 keywords")
        old_bug = self.backend.get_bug(bug_id)
        filtered = [k for k in (old_bug.get('keywords') or []) 
                    if k not in kwargs['keywords']]
        self.backend.update_bug(bug_id, keywords=filtered)
    
    def _replace_keywords(self, bug_id: int, kwargs: dict):
        if 'keywords' not in kwargs:
            raise ValueError("replace_keywords 模式必须传 keywords")
        self.backend.update_bug(bug_id, keywords=kwargs['keywords'])
    
    def _add_tags(self, bug_id: int, kwargs: dict):
        if 'tags' not in kwargs:
            raise ValueError("add_tags 模式必须传 tags")
        old_bug = self.backend.get_bug(bug_id)
        merged = list(set((old_bug.get('tags') or []) + kwargs['tags']))
        self.backend.update_bug(bug_id, tags=merged)
    
    def _remove_tags(self, bug_id: int, kwargs: dict):
        if 'tags' not in kwargs:
            raise ValueError("remove_tags 模式必须传 tags")
        old_bug = self.backend.get_bug(bug_id)
        filtered = [t for t in (old_bug.get('tags') or []) 
                    if t not in kwargs['tags']]
        self.backend.update_bug(bug_id, tags=filtered)
    
    def _replace_tags(self, bug_id: int, kwargs: dict):
        if 'tags' not in kwargs:
            raise ValueError("replace_tags 模式必须传 tags")
        self.backend.update_bug(bug_id, tags=kwargs['tags'])
    
    def _increment_scores(self, bug_id: int, kwargs: dict):
        if 'scores' not in kwargs:
            raise ValueError("increment_scores 模式必须传 scores")
        old_bug = self.backend.get_bug(bug_id)
        merged_scores = dict(old_bug.get('scores') or {})
        for dim, delta in kwargs['scores'].items():
            merged_scores[dim] = merged_scores.get(dim, 0) + delta
        self.backend.update_bug(bug_id, scores=merged_scores)
    
    def _decrement_scores(self, bug_id: int, kwargs: dict):
        if 'scores' not in kwargs:
            raise ValueError("decrement_scores 模式必须传 scores")
        old_bug = self.backend.get_bug(bug_id)
        merged_scores = dict(old_bug.get('scores') or {})
        for dim, delta in kwargs['scores'].items():
            merged_scores[dim] = merged_scores.get(dim, 0) - delta
        self.backend.update_bug(bug_id, scores=merged_scores)
    
    def _replace_scores(self, bug_id: int, kwargs: dict):
        if 'scores' not in kwargs:
            raise ValueError("replace_scores 模式必须传 scores")
        self.backend.update_bug(bug_id, scores=kwargs['scores'])
    
    # ==================== 搜索（委托给 backend）====================
    
    def search_bugs(self, **kwargs) -> dict:
        """统一搜索接口"""
        mode = kwargs.get('mode')
        limit = kwargs.get('limit', 20)
        offset = kwargs.get('offset', 0)
        
        if mode == 'keyword':
            bugs = self.backend.find_by_keyword(kwargs['keyword'], limit=limit + offset)
        elif mode == 'tag':
            bugs = self.backend.find_by_tag(kwargs['tag'], limit=limit + offset)
        elif mode == 'recent':
            bugs = self.backend.find_by_created_after(kwargs.get('days', 7), limit=limit + offset)
        elif mode == 'high_score':
            bugs = self.backend.find_by_min_score(kwargs.get('min_score', 30.0), limit=limit + offset)
        elif mode == 'critical':
            bugs = self.backend.find_all_sorted(limit=limit + offset)
        elif mode == 'unverified':
            bugs = self.backend.find_unverified_since(kwargs.get('days', 7), limit=limit + offset)
        elif mode == 'custom':
            bugs = self.backend.query(
                status=kwargs.get('status', 'active'),
                min_score=kwargs.get('min_score', 0.0),
                max_score=kwargs.get('max_score'),
                verified=kwargs.get('verified'),
                order_by=kwargs.get('order_by', 'score'),
                limit=limit + offset
            )
        elif mode == 'module':
            bugs = self.backend.find_by_pattern(kwargs['pattern'], limit=limit + offset)
        else:
            raise ValueError(f"Unknown search mode: {mode}")
        
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
    
    # ==================== 整理（委托给 backend）====================
    
    def organize_bugs(self) -> dict:
        """整理 bug-book"""
        from metadata_store import metadata_store
        
        # 1. 压缩文件（移除 invalid 记录）
        compacted_count = self.backend.compact_file()
        
        all_bugs = self.backend.get_all_bugs()
        
        # 2. 检查路径无效的 bug
        invalid_candidates = []
        for bug_id, bug in all_bugs.items():
            if bug.get('status') == 'invalid':
                continue
            invalid_paths = self._check_bug_paths(bug)
            if invalid_paths:
                invalid_candidates.append({
                    'id': bug_id,
                    'title': bug.get('title', ''),
                    'status': bug.get('status', 'active'),
                    'invalid_paths': invalid_paths,
                })
        
        # 3. 检查长期未验证的记录
        unverified_old = self.backend.find_unverified_old(days=30, limit=99999)
        
        # 4. 统计信息
        total_count = self.backend.count_bugs()
        active_bugs = [b for b in all_bugs.values() if b.get('status') == 'active']
        resolved_bugs = [b for b in all_bugs.values() if b.get('status') == 'resolved']
        
        statistics = {
            'total': total_count,
            'active': len(active_bugs),
            'resolved': len(resolved_bugs),
            'compacted': compacted_count,
        }
        
        # 5. 更新最后整理时间
        metadata_store.set_last_organize_time()
        last_organize_time = metadata_store.get_last_organize_time()
        
        return {
            'invalid_candidates': invalid_candidates,
            'unverified_old': unverified_old,
            'statistics': statistics,
            'last_organize_time': last_organize_time,
        }
    
    def _check_bug_paths(self, bug: dict) -> list[str]:
        """检查 bug 的 paths/module_patterns 是否有效，返回无效路径列表"""
        root = find_project_root()
        invalid_paths = []
        
        for path in bug.get("paths", []) + bug.get("module_patterns", []):
            if isinstance(path, dict):
                path_str = path.get('file', '')
            else:
                path_str = path
            
            # 检查路径是否存在
            if path_str.endswith("/*"):
                abs_path = root / path_str[:-2]
                is_valid = abs_path.exists() and abs_path.is_dir()
            else:
                abs_path = root / path_str
                is_valid = abs_path.exists()
            
            if not is_valid:
                invalid_paths.append(path_str)
        
        return invalid_paths
    
    # ==================== 详情（委托给 backend）====================
    
    def get_bug_detail(self, bug_id: int) -> Optional[dict]:
        """获取 bug 详情"""
        return self.backend.get_bug(bug_id)
    
    # ==================== Hook 相关（业务逻辑在 Service 层）====================
    
    def recall_by_path(self, file_path: str, limit: int = 10) -> list:
        """按路径召回"""
        return self.backend.find_by_path(file_path, limit)
    
    def migrate_paths(self, old_path: str, new_path: str) -> list:
        """路径迁移"""
        from path_utils import normalize_path, match_path
        
        old_path_norm = normalize_path(old_path)
        new_path_norm = normalize_path(new_path)
        
        # 通过 paths 查询
        affected_bugs = self.backend.find_by_path(old_path, limit=99999)
        # 通过 pattern 查询
        pattern_bugs = self.backend.find_by_pattern(old_path, limit=99999)
        
        # 合并去重
        seen_ids = set()
        migrated_bugs = []
        
        for bug_summary in affected_bugs + pattern_bugs:
            bug_id = bug_summary["id"]
            if bug_id in seen_ids:
                continue
            seen_ids.add(bug_id)
            
            bug = self.backend.get_bug(bug_id)
            if not bug:
                continue
            
            updated = False
            
            # 更新 paths
            current_paths = bug.get("paths", [])
            new_paths = []
            for p in current_paths:
                if isinstance(p, dict):
                    path_file = p.get('file', '')
                else:
                    path_file = p
                
                if path_file == old_path_norm:
                    if isinstance(p, dict):
                        new_paths.append({
                            'file': new_path_norm,
                            'functions': p.get('functions', [])
                        })
                    else:
                        new_paths.append(new_path_norm)
                    updated = True
                else:
                    new_paths.append(p)
            
            if updated:
                bug["paths"] = new_paths
            
            # 更新 module_patterns
            current_module_patterns = bug.get("module_patterns", [])
            matched_patterns = [r for r in current_module_patterns if match_path(old_path_norm, r)]
            if matched_patterns:
                updated_module_patterns = []
                for r in current_module_patterns:
                    if r in matched_patterns:
                        if r.endswith("/*"):
                            base_dir = "/".join(new_path_norm.split("/")[:-1])
                            updated_module_patterns.append(f"{base_dir}/*")
                        else:
                            updated_module_patterns.append(new_path_norm)
                    else:
                        updated_module_patterns.append(r)
                bug["module_patterns"] = updated_module_patterns
                updated = True
            
            if updated:
                from datetime import datetime
                bug["updated_at"] = datetime.now().isoformat()
                self.backend.update_bug(bug_id, paths=bug["paths"], module_patterns=bug["module_patterns"], updated_at=bug["updated_at"])
                migrated_bugs.append(bug_id)
        
        return list(set(migrated_bugs))
