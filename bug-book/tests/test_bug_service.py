#!/usr/bin/env python3
"""BugService 单元测试 - 测试业务编排层的 6 个公共接口"""

import os
import sys
import pytest
from pathlib import Path

# 添加 mcp 目录到 path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "mcp"))

from bug_service import BugService

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
def service():
    """创建 BugService 实例"""
    # 清除模块缓存
    modules_to_clear = [m for m in list(sys.modules.keys()) if m.startswith(('mcp.', 'backend_factory', 'jsonl_backend', 'config', 'bug_backend', 'path_utils', 'bug_service'))]
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

    return BugService()


# ============================================================================
# TC-S01 ~ TC-S04: save_bugs - add 模式
# ============================================================================

def test_save_bugs_add_minimal(service):
    """TC-S01: save_bugs add 模式 - 最小字段"""
    result = service.save_bugs([{
        'mode': 'add',
        'title': '测试Bug',
        'phenomenon': '测试现象'
    }])
    assert 'results' in result
    assert result['count'] == 1
    bug_id = result['results'][0]['id']
    assert bug_id > 0

    detail = service.get_bug_detail(bug_id)
    assert detail["title"] == "测试Bug"
    assert detail["verified"] == 0
    assert detail["status"] == "active"


def test_save_bugs_add_full_fields(service):
    """TC-S02: save_bugs add 模式 - 完整字段"""
    result = service.save_bugs([{
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
    detail = service.get_bug_detail(bug_id)
    assert detail["title"] == "session丢失"
    assert detail["paths"] == [{'file': 'src/auth/session.ts', 'functions': []}]
    assert detail["tags"] == ["auth"]
    assert detail["module_patterns"] == ["auth/*"]
    assert detail["status"] == "resolved"


def test_save_bugs_add_chinese(service):
    """TC-S03: save_bugs add 模式 - 含中文"""
    result = service.save_bugs([{
        'mode': 'add',
        'title': '中文标题',
        'phenomenon': '中文现象描述',
    }])
    bug_id = result['results'][0]['id']
    detail = service.get_bug_detail(bug_id)
    assert detail["title"] == "中文标题"
    assert "中文" in detail["phenomenon"]


def test_save_bugs_add_multiple_in_one_call(service):
    """TC-S04: save_bugs add 模式 - 批量新增"""
    result = service.save_bugs([
        {'mode': 'add', 'title': 'Bug1', 'phenomenon': '现象1'},
        {'mode': 'add', 'title': 'Bug2', 'phenomenon': '现象2'},
    ])
    assert result['count'] == 2
    assert all(r['id'] > 0 for r in result['results'])


# ============================================================================
# TC-U01 ~ TC-U03: save_bugs - update_fields 模式
# ============================================================================

def test_save_bugs_update_fields_single(service):
    """TC-U01: save_bugs update_fields 模式 - 更新单字段"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '旧标题', 'phenomenon': '旧现象'}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{
        'mode': 'update_fields',
        'id': bug_id,
        'title': '新标题'
    }])
    detail = service.get_bug_detail(bug_id)
    assert detail["title"] == "新标题"
    assert detail["phenomenon"] == "旧现象"


def test_save_bugs_update_fields_multiple(service):
    """TC-U02: save_bugs update_fields 模式 - 更新多字段"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '旧', 'phenomenon': '旧', 'verified': True}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{
        'mode': 'update_fields',
        'id': bug_id,
        'title': '新',
        'root_cause': '新根因'
    }])
    detail = service.get_bug_detail(bug_id)
    assert detail["title"] == "新"
    assert detail["root_cause"] == "新根因"


def test_save_bugs_update_fields_verified(service):
    """TC-U03: save_bugs update_fields 模式 - 更新 verified 字段"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '待验证', 'phenomenon': '', 'verified': False}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{
        'mode': 'update_fields',
        'id': bug_id,
        'verified': True,
        'verified_by': 'User',
    }])
    detail = service.get_bug_detail(bug_id)
    assert detail["verified"] == 1
    assert detail["verified_by"] == "User"
    assert detail["status"] == "resolved"


# ============================================================================
# TC-D01 ~ TC-D02: save_bugs - delete 模式
# ============================================================================

def test_save_bugs_delete_exists(service):
    """TC-D01: save_bugs delete 模式 - 删除存在的记录"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '待删除', 'phenomenon': ''}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'delete', 'id': bug_id}])

    detail = service.get_bug_detail(bug_id)
    assert detail["status"] == "invalid"


def test_save_bugs_delete_nonexistent(service):
    """TC-D02: save_bugs delete 模式 - 删除不存在的 id 抛出异常"""
    with pytest.raises(Exception):
        service.save_bugs([{'mode': 'delete', 'id': 9999}])


# ============================================================================
# TC-P01 ~ TC-P02: save_bugs - add_paths 模式
# ============================================================================

def test_save_bugs_add_paths(service):
    """TC-P01: save_bugs add_paths 模式 - 添加路径"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '路径测试', 'phenomenon': ''}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{
        'mode': 'add_paths',
        'id': bug_id,
        'paths': [{'file': 'src/a.ts', 'functions': ['f1', 'f2']}]
    }])
    detail = service.get_bug_detail(bug_id)
    assert len(detail["paths"]) == 1
    assert detail["paths"][0]["file"] == "src/a.ts"


def test_save_bugs_add_paths_merge(service):
    """TC-P02: save_bugs add_paths 模式 - 合并函数"""
    add_result = service.save_bugs([{
        'mode': 'add',
        'title': '路径合并',
        'phenomenon': '',
        'paths': [{'file': 'src/a.ts', 'functions': ['f1']}]
    }])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{
        'mode': 'add_paths',
        'id': bug_id,
        'paths': [{'file': 'src/a.ts', 'functions': ['f2']}]
    }])
    detail = service.get_bug_detail(bug_id)
    assert len(detail["paths"]) == 1
    assert set(detail["paths"][0]["functions"]) == {"f1", "f2"}


# ============================================================================
# TC-P03 ~ TC-P05: save_bugs - remove_paths / replace_paths 模式
# ============================================================================

def test_save_bugs_remove_paths_entire_file(service):
    """TC-P03: save_bugs remove_paths 模式 - 移除整个 file"""
    add_result = service.save_bugs([{
        'mode': 'add',
        'title': '路径移除测试',
        'phenomenon': '',
        'paths': [{'file': 'src/a.ts', 'functions': ['f1', 'f2']}, {'file': 'src/b.ts', 'functions': []}]
    }])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{
        'mode': 'remove_paths',
        'id': bug_id,
        'paths': [{'file': 'src/a.ts'}]
    }])
    detail = service.get_bug_detail(bug_id)
    path_files = [p.get('file') if isinstance(p, dict) else p for p in detail['paths']]
    assert 'src/a.ts' not in path_files
    assert 'src/b.ts' in path_files


def test_save_bugs_remove_paths_partial_functions(service):
    """TC-P04: save_bugs remove_paths 模式 - 只移除部分 functions"""
    add_result = service.save_bugs([{
        'mode': 'add',
        'title': '函数移除测试',
        'phenomenon': '',
        'paths': [{'file': 'src/a.ts', 'functions': ['f1', 'f2', 'f3']}]
    }])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{
        'mode': 'remove_paths',
        'id': bug_id,
        'paths': [{'file': 'src/a.ts', 'functions': ['f1']}]
    }])
    detail = service.get_bug_detail(bug_id)
    assert detail['paths'][0]['functions'] == ['f2', 'f3']


def test_save_bugs_replace_paths(service):
    """TC-P05: save_bugs replace_paths 模式 - 替换整个 paths 列表"""
    add_result = service.save_bugs([{
        'mode': 'add',
        'title': '路径替换测试',
        'phenomenon': '',
        'paths': ['src/old/a.ts', 'src/old/b.ts']
    }])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{
        'mode': 'replace_paths',
        'id': bug_id,
        'paths': [{'file': 'src/new/c.ts', 'functions': ['main']}]
    }])
    detail = service.get_bug_detail(bug_id)
    assert len(detail['paths']) == 1
    assert detail['paths'][0]['file'] == 'src/new/c.ts'


# ============================================================================
# TC-INC01 ~ TC-INC03: save_bugs - increment/decrement_scores 模式
# ============================================================================

def test_save_bugs_increment_scores(service):
    """TC-INC01: save_bugs increment_scores 模式 - 累加分数"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '分数累加测试', 'phenomenon': '', 'scores': {'occurrences': 0}}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'increment_scores', 'id': bug_id, 'scores': {'occurrences': 1.0}}])
    service.save_bugs([{'mode': 'increment_scores', 'id': bug_id, 'scores': {'occurrences': 1.0}}])
    service.save_bugs([{'mode': 'increment_scores', 'id': bug_id, 'scores': {'occurrences': 1.0}}])

    detail = service.get_bug_detail(bug_id)
    assert detail["scores"]["occurrences"] == 3.0


def test_save_bugs_decrement_scores(service):
    """TC-INC02: save_bugs decrement_scores 模式 - 分数递减"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '分数扣减测试', 'phenomenon': '', 'scores': {'occurrences': 5.0}}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'decrement_scores', 'id': bug_id, 'scores': {'occurrences': 2.0}}])
    detail = service.get_bug_detail(bug_id)
    assert detail["scores"]["occurrences"] == 3.0


def test_save_bugs_decrement_scores_to_negative(service):
    """TC-INC03: save_bugs decrement_scores 模式 - 扣减为负数"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '分数负数测试', 'phenomenon': '', 'scores': {'occurrences': 1.0}}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'decrement_scores', 'id': bug_id, 'scores': {'occurrences': 5.0}}])
    detail = service.get_bug_detail(bug_id)
    assert detail["scores"]["occurrences"] == -4.0


# ============================================================================
# TC-EDGE01 ~ TC-EDGE08: 边界情况测试
# ============================================================================

def test_save_bugs_add_paths_empty_list(service):
    """TC-EDGE01: add_paths 传空列表，保留原 paths"""
    add_result = service.save_bugs([{
        'mode': 'add',
        'title': '空列表测试',
        'phenomenon': '',
        'paths': [{'file': 'src/a.ts', 'functions': ['f1']}]
    }])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'add_paths', 'id': bug_id, 'paths': []}])
    detail = service.get_bug_detail(bug_id)
    assert len(detail['paths']) == 1


def test_save_bugs_remove_paths_nonexistent(service):
    """TC-EDGE02: remove_paths 传不存在的 path，无效果"""
    add_result = service.save_bugs([{
        'mode': 'add',
        'title': '不存在路径测试',
        'phenomenon': '',
        'paths': [{'file': 'src/a.ts', 'functions': ['f1']}]
    }])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'remove_paths', 'id': bug_id, 'paths': [{'file': 'src/nonexistent.ts'}]}])
    detail = service.get_bug_detail(bug_id)
    assert len(detail['paths']) == 1
    assert detail['paths'][0]['file'] == 'src/a.ts'


def test_save_bugs_update_fields_empty_raises(service):
    """TC-EDGE03: update_fields 传空数据，抛出异常"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '空更新测试', 'phenomenon': ''}])
    bug_id = add_result['results'][0]['id']

    with pytest.raises(Exception):
        service.save_bugs([{'mode': 'update_fields', 'id': bug_id}])


def test_save_bugs_add_impacts_empty_list(service):
    """TC-EDGE04: add_impacts 传空列表，静默跳过"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '空影响测试', 'phenomenon': ''}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'add_impacts', 'id': bug_id, 'impacts': []}])
    detail = service.get_bug_detail(bug_id)
    assert len(detail.get('impacts', [])) == 0


def test_save_bugs_increment_scores_new_dimension(service):
    """TC-EDGE05: increment_scores 新增维度，从 0 开始"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '新维度测试', 'phenomenon': '', 'scores': {'importance': 5}}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'increment_scores', 'id': bug_id, 'scores': {'new_dim': 3.0}}])
    detail = service.get_bug_detail(bug_id)
    assert detail['scores'].get('new_dim') == 3.0


def test_save_bugs_remove_keywords_nonexistent(service):
    """TC-EDGE06: remove_keywords 传不存在项，无效果"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '不存在关键词测试', 'phenomenon': '', 'keywords': ['k1', 'k2']}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'remove_keywords', 'id': bug_id, 'keywords': ['k999']}])
    detail = service.get_bug_detail(bug_id)
    assert set(detail['keywords']) == {'k1', 'k2'}


def test_save_bugs_remove_module_patterns_nonexistent(service):
    """TC-EDGE07: remove_module_patterns 传不存在项，无效果"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '不存在模块测试', 'phenomenon': '', 'module_patterns': ['auth/*', 'api/*']}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'remove_module_patterns', 'id': bug_id, 'module_patterns': ['nonexistent/*']}])
    detail = service.get_bug_detail(bug_id)
    assert set(detail['module_patterns']) == {'auth/*', 'api/*'}


def test_save_bugs_replace_module_patterns(service):
    """TC-EDGE08: replace_module_patterns 完全替换"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '模块替换测试', 'phenomenon': '', 'module_patterns': ['old/*']}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'replace_module_patterns', 'id': bug_id, 'module_patterns': ['new/*', 'other/*']}])
    detail = service.get_bug_detail(bug_id)
    assert set(detail['module_patterns']) == {'new/*', 'other/*'}


# ============================================================================
# TC-IMP01 ~ TC-IMP02: save_bugs - add/remove_impacts 模式
# ============================================================================

def test_save_bugs_add_impacts(service):
    """TC-IMP01: save_bugs add_impacts 模式 - 添加影响"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '影响测试', 'phenomenon': ''}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{
        'mode': 'add_impacts',
        'id': bug_id,
        'impacts': [{
            'solution_change': '修改了session处理',
            'impact_description': '导致购物车失效',
            'impact_type': 'regression',
            'severity': 8
        }]
    }])
    detail = service.get_bug_detail(bug_id)
    assert len(detail["impacts"]) == 1
    assert detail["impacts"][0]["impact_type"] == "regression"


def test_save_bugs_remove_impacts(service):
    """TC-IMP02: save_bugs remove_impacts 模式 - 移除影响"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '移除影响测试', 'phenomenon': ''}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{
        'mode': 'add_impacts',
        'id': bug_id,
        'impacts': [
            {'solution_change': 's1', 'impact_description': 'd1', 'impact_type': 'regression', 'severity': 5},
            {'solution_change': 's2', 'impact_description': 'd2', 'impact_type': 'side_effect', 'severity': 3}
        ]
    }])
    detail = service.get_bug_detail(bug_id)
    impact_id = detail['impacts'][0]['id']

    service.save_bugs([{'mode': 'remove_impacts', 'id': bug_id, 'impact_ids': [impact_id]}])
    detail = service.get_bug_detail(bug_id)
    assert len(detail['impacts']) == 1


# ============================================================================
# TC-DEDUP01 ~ TC-DEDUP03: save_bugs - 去重测试
# ============================================================================

def test_save_bugs_add_keywords_duplicate(service):
    """TC-DEDUP01: add_keywords 重复关键词自动去重"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '关键词去重测试', 'phenomenon': '', 'keywords': ['k1']}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'add_keywords', 'id': bug_id, 'keywords': ['k2', 'k1', 'k3']}])
    detail = service.get_bug_detail(bug_id)
    assert set(detail['keywords']) == {'k1', 'k2', 'k3'}


def test_save_bugs_add_tags_duplicate(service):
    """TC-DEDUP02: add_tags 重复标签自动去重"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '标签去重测试', 'phenomenon': '', 'tags': ['t1']}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'add_tags', 'id': bug_id, 'tags': ['t2', 't1', 't3']}])
    detail = service.get_bug_detail(bug_id)
    assert set(detail['tags']) == {'t1', 't2', 't3'}


def test_save_bugs_add_module_patterns_duplicate(service):
    """TC-DEDUP03: add_module_patterns 重复模式自动去重"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '模式去重测试', 'phenomenon': '', 'module_patterns': ['auth/*']}])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{'mode': 'add_module_patterns', 'id': bug_id, 'module_patterns': ['api/*', 'auth/*', 'src/*']}])
    detail = service.get_bug_detail(bug_id)
    assert set(detail['module_patterns']) == {'auth/*', 'api/*', 'src/*'}


# ============================================================================
# TC-SE01 ~ TC-SE06: search_bugs 接口
# ============================================================================

def test_search_bugs_keyword(service):
    """TC-SE01: search_bugs keyword 模式 - 关键词搜索"""
    service.save_bugs([{'mode': 'add', 'title': '测试', 'phenomenon': '现象', 'keywords': ['XYZ123']}])

    result = service.search_bugs(mode='keyword', keyword='XYZ123')
    assert result['pagination']['total'] >= 1


def test_search_bugs_recent(service):
    """TC-SE02: search_bugs recent 模式 - 最近创建"""
    service.save_bugs([{'mode': 'add', 'title': '最近', 'phenomenon': ''}])

    result = service.search_bugs(mode='recent', days=7)
    assert result['pagination']['total'] >= 1


def test_search_bugs_high_score(service):
    """TC-SE03: search_bugs high_score 模式 - 高分搜索"""
    service.save_bugs([{'mode': 'add', 'title': '高分', 'phenomenon': '', 'scores': {
        'importance': 10, 'complexity': 10, 'scope': 10, 'difficulty': 10,
        'occurrences': 0, 'emotion': 0, 'prevention': 10
    }}])

    result = service.search_bugs(mode='high_score', min_score=30.0)
    assert result['pagination']['total'] >= 1
    assert all(b['score'] >= 30.0 for b in result['bugs'])


def test_search_bugs_critical(service):
    """TC-SE04: search_bugs critical 模式 - 最严重"""
    service.save_bugs([{'mode': 'add', 'title': '严重', 'phenomenon': ''}])

    result = service.search_bugs(mode='critical', limit=5)
    assert len(result['bugs']) <= 5


def test_search_bugs_custom(service):
    """TC-SE05: search_bugs custom 模式 - 自定义条件"""
    service.save_bugs([{
        'mode': 'add',
        'title': '自定义',
        'phenomenon': '',
        'verified': True,
        'scores': {
            'importance': 10, 'complexity': 10, 'scope': 10, 'difficulty': 10,
            'occurrences': 0, 'emotion': 0, 'prevention': 10
        }
    }])

    result = service.search_bugs(mode='custom', status='resolved', min_score=30.0)
    assert result['pagination']['total'] >= 1


def test_search_bugs_no_result(service):
    """TC-SE06: search_bugs - 无结果"""
    result = service.search_bugs(mode='keyword', keyword='不存在的关键词XYZABC')
    assert result['pagination']['total'] == 0


# ============================================================================
# TC-G01 ~ TC-G03: get_bug_detail 接口
# ============================================================================

def test_get_bug_detail_exists(service):
    """TC-G01: get_bug_detail - 查询存在的 bug"""
    add_result = service.save_bugs([{'mode': 'add', 'title': '详情测试', 'phenomenon': ''}])
    bug_id = add_result['results'][0]['id']

    detail = service.get_bug_detail(bug_id)
    assert detail["id"] == bug_id
    assert detail["title"] == "详情测试"


def test_get_bug_detail_nonexistent(service):
    """TC-G02: get_bug_detail - 查询不存在的 bug 抛出异常"""
    with pytest.raises(Exception):
        service.get_bug_detail(9999)


def test_get_bug_detail_full(service):
    """TC-G03: get_bug_detail - 完整字段"""
    add_result = service.save_bugs([{
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

    detail = service.get_bug_detail(bug_id)

    assert len(detail["scores"]) == 7
    assert detail["paths"] == [{'file': 'src/a.ts', 'functions': []}]
    assert detail["tags"] == ["t1"]
    assert detail["keywords"] == ["k1"]
    assert detail["module_patterns"] == ["m1/*"]


# ============================================================================
# TC-R01 ~ TC-R03: recall_by_path 接口
# ============================================================================

def test_recall_by_path_exact(service):
    """TC-R01: recall_by_path - 精确路径召回"""
    add_result = service.save_bugs([{
        'mode': 'add',
        'title': '精确召回',
        'phenomenon': '',
        'paths': ['src/auth/session.ts']
    }])
    bug_id = add_result['results'][0]['id']

    results = service.recall_by_path('src/auth/session.ts')
    assert any(r["id"] == bug_id for r in results)


def test_recall_by_path_unrelated(service):
    """TC-R02: recall_by_path - 不相关路径不召回"""
    service.save_bugs([{
        'mode': 'add',
        'title': 'api问题',
        'phenomenon': '',
        'paths': ['src/api/user.ts']
    }])

    results = service.recall_by_path('src/auth/login.ts')
    assert not any(r["title"] == "api问题" for r in results)


def test_recall_by_path_returns_impacts(service):
    """TC-R03: recall_by_path - 返回 impacts 字段"""
    add_result = service.save_bugs([{
        'mode': 'add',
        'title': '影响召回',
        'phenomenon': '',
    }])
    bug_id = add_result['results'][0]['id']

    service.save_bugs([{
        'mode': 'add_impacts',
        'id': bug_id,
        'impacts': [{
            'solution_change': '变更',
            'impact_description': '影响',
            'impact_type': 'regression',
            'severity': 5
        }]
    }])

    results = service.recall_by_path('any/path.ts', limit=10)
    for r in results:
        if r['id'] == bug_id:
            assert 'impacts' in r


# ============================================================================
# TC-M01 ~ TC-M03: migrate_paths 接口
# ============================================================================

def test_migrate_paths_exact_match(service):
    """TC-M01: migrate_paths - 精确路径迁移"""
    add_result = service.save_bugs([{
        'mode': 'add',
        'title': '路径迁移',
        'phenomenon': '',
        'paths': ['src/auth/session.ts']
    }])
    bug_id = add_result['results'][0]['id']

    migrated = service.migrate_paths(
        'src/auth/session.ts',
        'src/modules/auth/session.ts'
    )
    assert bug_id in migrated

    detail = service.get_bug_detail(bug_id)
    path_files = [p.get('file') if isinstance(p, dict) else p for p in detail['paths']]
    assert 'src/modules/auth/session.ts' in path_files


def test_migrate_paths_no_match(service):
    """TC-M02: migrate_paths - 无匹配时返回空"""
    migrated = service.migrate_paths(
        'nonexistent/path.ts',
        'new/path.ts'
    )
    assert migrated == []


def test_migrate_paths_with_module_pattern(service):
    """TC-M03: migrate_paths - 同时迁移 module_patterns"""
    add_result = service.save_bugs([{
        'mode': 'add',
        'title': '模块迁移',
        'phenomenon': '',
        'module_patterns': ['auth/*']
    }])
    bug_id = add_result['results'][0]['id']

    migrated = service.migrate_paths(
        'src/auth/login.ts',
        'src/modules/auth/login.ts'
    )
    assert bug_id in migrated

    detail = service.get_bug_detail(bug_id)
    assert 'src/modules/auth/*' in detail['module_patterns']


# ============================================================================
# TC-O01: organize_bugs 接口
# ============================================================================

def test_organize_bugs_returns_structure(service):
    """TC-O01: organize_bugs - 返回结构化数据"""
    service.save_bugs([{'mode': 'add', 'title': '测试', 'phenomenon': ''}])

    result = service.organize_bugs()

    assert 'invalid_candidates' in result
    assert 'unverified_old' in result
    assert 'statistics' in result
    assert 'last_organize_time' in result
    assert 'total' in result['statistics']
    assert 'active' in result['statistics']
    assert 'resolved' in result['statistics']


# ============================================================================
# TC-CRUD01: 完整 CRUD 流程测试
# ============================================================================

def test_full_crud_through_save_bugs(service):
    """TC-CRUD01: 完整 CRUD 流程通过 save_bugs"""
    # Create
    add_result = service.save_bugs([{'mode': 'add', 'title': 'CRUD', 'phenomenon': '创建'}])
    bug_id = add_result['results'][0]['id']

    # Read
    detail = service.get_bug_detail(bug_id)
    assert detail['phenomenon'] == '创建'

    # Update
    service.save_bugs([{'mode': 'update_fields', 'id': bug_id, 'phenomenon': '更新'}])
    detail = service.get_bug_detail(bug_id)
    assert detail['phenomenon'] == '更新'

    # Delete
    service.save_bugs([{'mode': 'delete', 'id': bug_id}])
    detail = service.get_bug_detail(bug_id)
    assert detail['status'] == 'invalid'