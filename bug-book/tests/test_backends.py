#!/usr/bin/env python3
"""Bug-book 6个公共接口的单元测试"""

import os
import sys
import pytest
from pathlib import Path

# 添加 mcp 目录到 path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "mcp"))

from backend_factory import create_backend
from storage_backend import BugStorageBackend

# 测试数据
DEFAULT_SCORES = {
    "importance": 7,
    "complexity": 5,
    "scope": 4,
    "difficulty": 3,
    "occurrences": 0,
    "emotion": 2,
    "prevention": 6,
}


@pytest.fixture
def backend():
    """创建 JSONL 后端实例"""
    # 清除模块缓存
    modules_to_clear = [m for m in list(sys.modules.keys()) if m.startswith(('mcp.', 'backend_factory', 'jsonl_backend', 'config', 'storage_backend', 'path_utils'))]
    for mod in modules_to_clear:
        del sys.modules[mod]

    # 清理 JSONL 文件
    from config import get_data_dir
    data_dir = get_data_dir()
    jsonl_path = data_dir / "bug-book.jsonl"

    try:
        if jsonl_path.exists():
            jsonl_path.unlink()
    except OSError:
        pass

    instance = create_backend()
    return instance


# ============================================================================
# 1. save_bugs 接口测试 - add 模式
# ============================================================================

def test_save_bugs_add_minimal_fields(backend):
    """TC-S01: save_bugs add 模式 - 最小字段"""
    result = backend.save_bugs([{
        'mode': 'add',
        'title': '测试Bug',
        'phenomenon': '测试现象'
    }])
    assert 'results' in result
    assert result['count'] == 1
    bug_id = result['results'][0]['id']
    assert bug_id > 0

    detail = backend.get_bug_detail(bug_id)
    assert detail["title"] == "测试Bug"
    assert detail["verified"] == 0
    assert detail["status"] == "active"


def test_save_bugs_add_full_fields(backend):
    """TC-S02: save_bugs add 模式 - 完整字段"""
    result = backend.save_bugs([{
        'mode': 'add',
        'title': 'session丢失',
        'phenomenon': '刷新页面丢失',
        'root_cause': '缺少配置',
        'solution': '添加maxAge',
        'test_case': '登录刷新验证',
        'verified': True,
        'scores': DEFAULT_SCORES,
        'paths': ['src/auth/session.ts'],
        'tags': ['auth'],
        'keywords': ['session'],
        'module_patterns': ['auth/*'],
    }])
    bug_id = result['results'][0]['id']
    detail = backend.get_bug_detail(bug_id)
    assert detail["title"] == "session丢失"
    assert detail["paths"] == [{'file': 'src/auth/session.ts', 'functions': []}]
    assert detail["tags"] == ["auth"]
    assert detail["module_patterns"] == ["auth/*"]
    assert detail["status"] == "resolved"


def test_save_bugs_add_chinese(backend):
    """TC-S03: save_bugs add 模式 - 含中文"""
    result = backend.save_bugs([{
        'mode': 'add',
        'title': '中文标题',
        'phenomenon': '中文现象描述',
    }])
    bug_id = result['results'][0]['id']
    detail = backend.get_bug_detail(bug_id)
    assert detail["title"] == "中文标题"
    assert "中文" in detail["phenomenon"]


def test_save_bugs_add_multiple_in_one_call(backend):
    """TC-S04: save_bugs add 模式 - 批量新增"""
    result = backend.save_bugs([
        {'mode': 'add', 'title': 'Bug1', 'phenomenon': '现象1'},
        {'mode': 'add', 'title': 'Bug2', 'phenomenon': '现象2'},
    ])
    assert result['count'] == 2
    assert all(r['id'] > 0 for r in result['results'])


# ============================================================================
# 2. save_bugs 接口测试 - update_fields 模式
# ============================================================================

def test_save_bugs_update_fields_single(backend):
    """TC-U01: save_bugs update_fields 模式 - 更新单字段"""
    # 先添加
    add_result = backend.save_bugs([{'mode': 'add', 'title': '旧标题', 'phenomenon': '旧现象'}])
    bug_id = add_result['results'][0]['id']

    # 再更新
    backend.save_bugs([{
        'mode': 'update_fields',
        'id': bug_id,
        'title': '新标题'
    }])
    detail = backend.get_bug_detail(bug_id)
    assert detail["title"] == "新标题"
    assert detail["phenomenon"] == "旧现象"  # 未更新的字段保持不变


def test_save_bugs_update_fields_multiple(backend):
    """TC-U02: save_bugs update_fields 模式 - 更新多字段"""
    add_result = backend.save_bugs([{'mode': 'add', 'title': '旧', 'phenomenon': '旧', 'verified': True}])
    bug_id = add_result['results'][0]['id']

    backend.save_bugs([{
        'mode': 'update_fields',
        'id': bug_id,
        'title': '新',
        'root_cause': '新根因'
    }])
    detail = backend.get_bug_detail(bug_id)
    assert detail["title"] == "新"
    assert detail["root_cause"] == "新根因"


def test_save_bugs_update_fields_verified(backend):
    """TC-U03: save_bugs update_fields 模式 - 更新 verified 字段"""
    add_result = backend.save_bugs([{'mode': 'add', 'title': '待验证', 'phenomenon': '', 'verified': False}])
    bug_id = add_result['results'][0]['id']

    backend.save_bugs([{
        'mode': 'update_fields',
        'id': bug_id,
        'verified': True,
        'verified_by': 'User',
    }])
    detail = backend.get_bug_detail(bug_id)
    assert detail["verified"] == 1
    assert detail["verified_by"] == "User"
    assert detail["status"] == "resolved"


# ============================================================================
# 3. save_bugs 接口测试 - delete 模式（软删除）
# ============================================================================

def test_save_bugs_delete_exists(backend):
    """TC-D01: save_bugs delete 模式 - 删除存在的记录"""
    add_result = backend.save_bugs([{'mode': 'add', 'title': '待删除', 'phenomenon': ''}])
    bug_id = add_result['results'][0]['id']

    backend.save_bugs([{'mode': 'delete', 'id': bug_id}])

    detail = backend.get_bug_detail(bug_id)
    assert detail["status"] == "invalid"


def test_save_bugs_delete_nonexistent(backend):
    """TC-D02: save_bugs delete 模式 - 删除不存在的 id 抛出异常"""
    with pytest.raises(Exception):
        backend.save_bugs([{'mode': 'delete', 'id': 9999}])


# ============================================================================
# 4. save_bugs 接口测试 - add_paths 模式
# ============================================================================

def test_save_bugs_add_paths(backend):
    """TC-P01: save_bugs add_paths 模式 - 添加路径"""
    add_result = backend.save_bugs([{'mode': 'add', 'title': '路径测试', 'phenomenon': ''}])
    bug_id = add_result['results'][0]['id']

    backend.save_bugs([{
        'mode': 'add_paths',
        'id': bug_id,
        'paths': [{'file': 'src/a.ts', 'functions': ['f1', 'f2']}]
    }])
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["paths"]) == 1
    assert detail["paths"][0]["file"] == "src/a.ts"


def test_save_bugs_add_paths_merge(backend):
    """TC-P02: save_bugs add_paths 模式 - 合并函数"""
    add_result = backend.save_bugs([{
        'mode': 'add',
        'title': '路径合并',
        'phenomenon': '',
        'paths': [{'file': 'src/a.ts', 'functions': ['f1']}]
    }])
    bug_id = add_result['results'][0]['id']

    backend.save_bugs([{
        'mode': 'add_paths',
        'id': bug_id,
        'paths': [{'file': 'src/a.ts', 'functions': ['f2']}]
    }])
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["paths"]) == 1
    assert set(detail["paths"][0]["functions"]) == {"f1", "f2"}


# ============================================================================
# 5. save_bugs 接口测试 - increment_scores 模式
# ============================================================================

def test_save_bugs_increment_scores(backend):
    """TC-INC01: save_bugs increment_scores 模式 - 累加分数"""
    add_result = backend.save_bugs([{'mode': 'add', 'title': '分数测试', 'phenomenon': '', 'scores': {'occurrences': 0}}])
    bug_id = add_result['results'][0]['id']

    backend.save_bugs([{'mode': 'increment_scores', 'id': bug_id, 'scores': {'occurrences': 1.0}}])
    backend.save_bugs([{'mode': 'increment_scores', 'id': bug_id, 'scores': {'occurrences': 1.0}}])
    backend.save_bugs([{'mode': 'increment_scores', 'id': bug_id, 'scores': {'occurrences': 1.0}}])

    detail = backend.get_bug_detail(bug_id)
    assert detail["scores"]["occurrences"] == 3.0


# ============================================================================
# 6. save_bugs 接口测试 - add_impacts 模式
# ============================================================================

def test_save_bugs_add_impacts(backend):
    """TC-IMP01: save_bugs add_impacts 模式 - 添加影响"""
    add_result = backend.save_bugs([{'mode': 'add', 'title': '影响测试', 'phenomenon': ''}])
    bug_id = add_result['results'][0]['id']

    backend.save_bugs([{
        'mode': 'add_impacts',
        'id': bug_id,
        'impacts': [{
            'solution_change': '修改了session处理',
            'impact_description': '导致购物车失效',
            'impact_type': 'regression',
            'severity': 8
        }]
    }])
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["impacts"]) == 1
    assert detail["impacts"][0]["impact_type"] == "regression"


# ============================================================================
# 7. search_bugs 接口测试
# ============================================================================

def test_search_bugs_keyword(backend):
    """TC-SE01: search_bugs keyword 模式 - 关键词搜索"""
    backend.save_bugs([{'mode': 'add', 'title': '测试', 'phenomenon': '现象', 'keywords': ['XYZ123']}])

    result = backend.search_bugs(mode='keyword', keyword='XYZ123')
    assert result['pagination']['total'] >= 1
    assert any('XYZ123' in b.get('keywords', []) for b in result['bugs'])


def test_search_bugs_recent(backend):
    """TC-SE02: search_bugs recent 模式 - 最近创建"""
    backend.save_bugs([{'mode': 'add', 'title': '最近', 'phenomenon': ''}])

    result = backend.search_bugs(mode='recent', days=7)
    assert result['pagination']['total'] >= 1


def test_search_bugs_high_score(backend):
    """TC-SE03: search_bugs high_score 模式 - 高分搜索"""
    backend.save_bugs([{'mode': 'add', 'title': '高分', 'phenomenon': '', 'scores': {
        'importance': 10, 'complexity': 10, 'scope': 10, 'difficulty': 10,
        'occurrences': 0, 'emotion': 0, 'prevention': 10
    }}])

    result = backend.search_bugs(mode='high_score', min_score=30.0)
    assert result['pagination']['total'] >= 1
    assert all(b['score'] >= 30.0 for b in result['bugs'])


def test_search_bugs_critical(backend):
    """TC-SE04: search_bugs critical 模式 - 最严重"""
    backend.save_bugs([{'mode': 'add', 'title': '严重', 'phenomenon': ''}])

    result = backend.search_bugs(mode='critical', limit=5)
    assert len(result['bugs']) <= 5


def test_search_bugs_custom(backend):
    """TC-SE05: search_bugs custom 模式 - 自定义条件"""
    backend.save_bugs([{
        'mode': 'add',
        'title': '自定义',
        'phenomenon': '',
        'verified': True,
        'scores': {
            'importance': 10, 'complexity': 10, 'scope': 10, 'difficulty': 10,
            'occurrences': 0, 'emotion': 0, 'prevention': 10
        }
    }])

    # verified=True 时 status='resolved'
    result = backend.search_bugs(mode='custom', status='resolved', min_score=30.0)
    assert result['pagination']['total'] >= 1


def test_search_bugs_no_result(backend):
    """TC-SE06: search_bugs - 无结果"""
    result = backend.search_bugs(mode='keyword', keyword='不存在的关键词XYZABC')
    assert result['pagination']['total'] == 0


# ============================================================================
# 8. get_bug_detail 接口测试
# ============================================================================

def test_get_bug_detail_exists(backend):
    """TC-G01: get_bug_detail - 查询存在的 bug"""
    add_result = backend.save_bugs([{'mode': 'add', 'title': '详情测试', 'phenomenon': ''}])
    bug_id = add_result['results'][0]['id']

    detail = backend.get_bug_detail(bug_id)
    assert detail["id"] == bug_id
    assert detail["title"] == "详情测试"


def test_get_bug_detail_nonexistent(backend):
    """TC-G02: get_bug_detail - 查询不存在的 bug 抛出异常"""
    with pytest.raises(Exception):
        backend.get_bug_detail(9999)


def test_get_bug_detail_full(backend):
    """TC-G03: get_bug_detail - 完整字段"""
    add_result = backend.save_bugs([{
        'mode': 'add',
        'title': '完整详情',
        'phenomenon': '现象',
        'root_cause': '根因',
        'solution': '解决方案',
        'scores': DEFAULT_SCORES,
        'paths': ['src/a.ts'],
        'tags': ['t1'],
        'keywords': ['k1'],
        'module_patterns': ['m1/*'],
    }])
    bug_id = add_result['results'][0]['id']

    detail = backend.get_bug_detail(bug_id)

    assert len(detail["scores"]) == 7
    assert detail["paths"] == [{'file': 'src/a.ts', 'functions': []}]
    assert detail["tags"] == ["t1"]
    assert detail["keywords"] == ["k1"]
    assert detail["module_patterns"] == ["m1/*"]


# ============================================================================
# 9. recall_by_path 接口测试
# ============================================================================

def test_recall_by_path_exact(backend):
    """TC-R01: recall_by_path - 精确路径召回"""
    add_result = backend.save_bugs([{
        'mode': 'add',
        'title': '精确召回',
        'phenomenon': '',
        'paths': ['src/auth/session.ts']
    }])
    bug_id = add_result['results'][0]['id']

    results = backend.recall_by_path('src/auth/session.ts')
    assert any(r["id"] == bug_id for r in results)


def test_recall_by_path_unrelated(backend):
    """TC-R02: recall_by_path - 不相关路径不召回"""
    backend.save_bugs([{
        'mode': 'add',
        'title': 'api问题',
        'phenomenon': '',
        'paths': ['src/api/user.ts']
    }])

    results = backend.recall_by_path('src/auth/login.ts')
    assert not any(r["title"] == "api问题" for r in results)


def test_recall_by_path_returns_impacts(backend):
    """TC-R03: recall_by_path - 返回 impacts 字段"""
    add_result = backend.save_bugs([{
        'mode': 'add',
        'title': '影响召回',
        'phenomenon': '',
    }])
    bug_id = add_result['results'][0]['id']

    backend.save_bugs([{
        'mode': 'add_impacts',
        'id': bug_id,
        'impacts': [{
            'solution_change': '变更',
            'impact_description': '影响',
            'impact_type': 'regression',
            'severity': 5
        }]
    }])

    results = backend.recall_by_path('any/path.ts', limit=10)
    for r in results:
        if r['id'] == bug_id:
            assert 'impacts' in r


# ============================================================================
# 10. migrate_bug_paths_after_refactor 接口测试
# ============================================================================

def test_migrate_paths_exact_match(backend):
    """TC-M01: migrate_bug_paths_after_refactor - 精确路径迁移"""
    add_result = backend.save_bugs([{
        'mode': 'add',
        'title': '路径迁移',
        'phenomenon': '',
        'paths': ['src/auth/session.ts']
    }])
    bug_id = add_result['results'][0]['id']

    migrated = backend.migrate_bug_paths_after_refactor(
        'src/auth/session.ts',
        'src/modules/auth/session.ts'
    )
    assert bug_id in migrated

    detail = backend.get_bug_detail(bug_id)
    path_files = [p.get('file') if isinstance(p, dict) else p for p in detail['paths']]
    assert 'src/modules/auth/session.ts' in path_files


def test_migrate_paths_no_match(backend):
    """TC-M02: migrate_bug_paths_after_refactor - 无匹配时返回空"""
    migrated = backend.migrate_bug_paths_after_refactor(
        'nonexistent/path.ts',
        'new/path.ts'
    )
    assert migrated == []


def test_migrate_paths_with_module_pattern(backend):
    """TC-M03: migrate_bug_paths_after_refactor - 同时迁移 module_patterns"""
    add_result = backend.save_bugs([{
        'mode': 'add',
        'title': '模块迁移',
        'phenomenon': '',
        'module_patterns': ['auth/*']
    }])
    bug_id = add_result['results'][0]['id']

    # 通过路径触发 module_pattern 匹配
    migrated = backend.migrate_bug_paths_after_refactor(
        'src/auth/login.ts',
        'src/modules/auth/login.ts'
    )
    assert bug_id in migrated

    detail = backend.get_bug_detail(bug_id)
    assert 'src/modules/auth/*' in detail['module_patterns']


# ============================================================================
# 11. organize_bugs 接口测试
# ============================================================================

def test_organize_bugs_returns_structure(backend):
    """TC-O01: organize_bugs - 返回结构化数据"""
    # 添加一些测试数据
    backend.save_bugs([{'mode': 'add', 'title': '测试', 'phenomenon': ''}])

    result = backend.organize_bugs()

    assert 'invalid_candidates' in result
    assert 'unverified_old' in result
    assert 'statistics' in result
    assert 'last_organize_time' in result
    assert 'total' in result['statistics']
    assert 'active' in result['statistics']
    assert 'resolved' in result['statistics']


# ============================================================================
# 12. 完整 CRUD 流程测试
# ============================================================================

def test_full_crud_through_save_bugs(backend):
    """TC-CRUD01: 完整 CRUD 流程通过 save_bugs"""
    # Create
    add_result = backend.save_bugs([{'mode': 'add', 'title': 'CRUD', 'phenomenon': '创建'}])
    bug_id = add_result['results'][0]['id']

    # Read
    detail = backend.get_bug_detail(bug_id)
    assert detail['phenomenon'] == '创建'

    # Update
    backend.save_bugs([{'mode': 'update_fields', 'id': bug_id, 'phenomenon': '更新'}])
    detail = backend.get_bug_detail(bug_id)
    assert detail['phenomenon'] == '更新'

    # Delete
    backend.save_bugs([{'mode': 'delete', 'id': bug_id}])
    detail = backend.get_bug_detail(bug_id)
    assert detail['status'] == 'invalid'