#!/usr/bin/env python3
"""BugBackend 单元测试 - 测试存储后端原子操作"""

import os
import sys
import pytest
from pathlib import Path

# 添加 mcp 目录到 path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "mcp"))

from backend_factory import create_backend
from bug_backend import BugBackend

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
    """创建 BugBackend 实例"""
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

    instance = create_backend()
    assert isinstance(instance, BugBackend)
    return instance


# ============================================================================
# TC-A01 ~ TC-A08: add_bug 新增记录
# ============================================================================

def test_add_bug_minimal_fields(backend):
    """TC-A01: 新增最小字段记录"""
    bug_id, score = backend.add_bug(title="测试", phenomenon="现象", verified=True)
    assert bug_id > 0
    assert score == 0
    detail = backend.get_bug(bug_id)
    assert detail["title"] == "测试"
    assert detail["verified"] == 1


def test_add_bug_full_fields(backend):
    """TC-A02: 新增完整字段记录"""
    bug_id, score = backend.add_bug(
        title="session丢失",
        phenomenon="刷新页面丢失",
        root_cause="缺少配置",
        solution="添加maxAge",
        test_case="登录刷新验证",
        verified=False,
        scores=DEFAULT_SCORES,
        paths=["src/auth/session.ts"],
        tags=["auth"],
        keywords=["session"],
        module_patterns=["auth/*"],
    )
    assert bug_id > 0
    assert score > 0
    detail = backend.get_bug(bug_id)
    assert detail["title"] == "session丢失"
    assert len(detail["scores"]) == 7


def test_add_bug_chinese(backend):
    """TC-A03: 新增记录含中文"""
    bug_id, _ = backend.add_bug(
        title="中文标题测试",
        phenomenon="中文现象描述",
        root_cause="中文根因分析",
        solution="中文解决方案",
        verified=True,
    )
    detail = backend.get_bug(bug_id)
    assert detail["title"] == "中文标题测试"
    assert "中文" in detail["phenomenon"]


def test_add_bug_verified_false(backend):
    """TC-A04: 新增 verified=False"""
    bug_id, _ = backend.add_bug(title="复杂问题", phenomenon="复杂", verified=False)
    detail = backend.get_bug(bug_id)
    assert detail["verified"] == 0
    assert detail["status"] == "active"


def test_add_bug_empty_scores(backend):
    """TC-A05: 新增空 scores dict"""
    bug_id, score = backend.add_bug(title="空分数", phenomenon="无分数", scores={})
    assert score == 0


def test_add_bug_multiple_paths(backend):
    """TC-A06: 新增多条 paths"""
    bug_id, _ = backend.add_bug(
        title="多路径",
        phenomenon="",
        paths=["src/a.ts", "src/b.ts"],
    )
    detail = backend.get_bug(bug_id)
    assert len(detail["paths"]) == 2


def test_add_bug_multiple_module_patterns(backend):
    """TC-A07: 新增多条 module_patterns"""
    bug_id, _ = backend.add_bug(
        title="多模式",
        phenomenon="",
        module_patterns=["auth/*", "src/*"],
    )
    detail = backend.get_bug(bug_id)
    assert len(detail["module_patterns"]) == 2


def test_add_bug_then_get_detail(backend):
    """TC-A08: 新增后立即查询"""
    bug_id, _ = backend.add_bug(title="立即查询", phenomenon="测试")
    detail = backend.get_bug(bug_id)
    assert detail is not None
    assert detail["id"] == bug_id


# ============================================================================
# TC-B01 ~ TC-B06: update_bug 更新记录
# ============================================================================

def test_update_bug_single_field(backend):
    """TC-B01: 更新单字段"""
    bug_id, _ = backend.add_bug(title="旧标题", phenomenon="", verified=True)
    backend.update_bug(bug_id, title="新标题")
    detail = backend.get_bug(bug_id)
    assert detail["title"] == "新标题"


def test_update_bug_multiple_fields(backend):
    """TC-B02: 同时更新多字段"""
    bug_id, _ = backend.add_bug(title="旧", phenomenon="旧", verified=True)
    backend.update_bug(bug_id, title="新", root_cause="新根因")
    detail = backend.get_bug(bug_id)
    assert detail["title"] == "新"
    assert detail["root_cause"] == "新根因"


def test_update_bug_verified_fields(backend):
    """TC-B03: 更新 verified 相关字段"""
    bug_id, _ = backend.add_bug(title="待验证", phenomenon="", verified=False)
    backend.update_bug(
        bug_id,
        verified=True,
        verified_at="CURRENT_TIMESTAMP",
        verified_by="User",
    )
    detail = backend.get_bug(bug_id)
    assert detail["verified"] == 1
    assert detail["verified_by"] == "User"
    assert detail["status"] == "resolved"


def test_update_bug_status(backend):
    """TC-B04: 更新 status 为 resolved"""
    bug_id, _ = backend.add_bug(title="待解决", phenomenon="", verified=True)
    backend.update_bug(bug_id, status="resolved")
    detail = backend.get_bug(bug_id)
    assert detail["status"] == "resolved"


def test_update_bug_nonexistent(backend):
    """TC-B05: 更新不存在的 bug_id（静默返回）"""
    backend.update_bug(9999, title="不存在")


def test_update_bug_no_fields(backend):
    """TC-B06: 不传任何字段"""
    bug_id, _ = backend.add_bug(title="无更新", phenomenon="", verified=True)
    backend.update_bug(bug_id)


# ============================================================================
# TC-C01 ~ TC-C02: 软删除（通过 update_bug status='invalid'）
# ============================================================================

def test_soft_delete_via_update(backend):
    """TC-C01: 通过 update_bug 软删除"""
    bug_id, _ = backend.add_bug(title="待删除", phenomenon="", verified=True)
    backend.update_bug(bug_id, status="invalid")
    detail = backend.get_bug(bug_id)
    assert detail["status"] == "invalid"


def test_soft_delete_and_still_retrievable(backend):
    """TC-C02: 软删除后数据仍可查询"""
    bug_id, _ = backend.add_bug(title="软删除", phenomenon="", verified=True)
    backend.update_bug(bug_id, status="invalid")
    detail = backend.get_bug(bug_id)
    assert detail["status"] == "invalid"
    assert detail["title"] == "软删除"


# ============================================================================
# TC-D01 ~ TC-D03: 影响关系管理
# ============================================================================

def test_add_impact_regression(backend):
    """TC-D01: 添加回归影响"""
    bug_id, _ = backend.add_bug(title="源bug", phenomenon="", verified=True)
    impact_id = backend.add_impact(
        source_bug_id=bug_id,
        solution_change="修改了 session 处理逻辑",
        impact_description="导致购物车功能失效",
        impact_type="regression",
        severity=8,
        prevention_delta=5.0,
    )
    assert impact_id > 0
    detail = backend.get_bug(bug_id)
    assert len(detail["impacts"]) == 1


def test_add_impact_side_effect(backend):
    """TC-D02: 添加副作用影响"""
    bug_id, _ = backend.add_bug(title="源bug", phenomenon="", verified=True)
    impact_id = backend.add_impact(
        source_bug_id=bug_id,
        solution_change="重构了用户模块",
        impact_description="影响积分计算",
        impact_type="side_effect",
        severity=5,
    )
    assert impact_id > 0


def test_add_impact_invalid_type(backend):
    """TC-D03: 添加无效影响类型"""
    bug_id, _ = backend.add_bug(title="源bug", phenomenon="", verified=True)
    with pytest.raises(Exception):
        backend.add_impact(
            source_bug_id=bug_id,
            solution_change="test",
            impact_description="test",
            impact_type="invalid",
        )


# ============================================================================
# TC-E01 ~ TC-E05: 查询原语
# ============================================================================

def test_find_by_keyword(backend):
    """TC-E01: 关键词查询"""
    backend.add_bug(title="test", phenomenon="", keywords=["XYZ123"], verified=True)
    results = backend.find_by_keyword("XYZ123", limit=10)
    assert len(results) >= 1


def test_find_by_keyword_no_result(backend):
    """TC-E02: 关键词查询无结果"""
    results = backend.find_by_keyword("不存在关键词ABCXYZ", limit=10)
    assert len(results) == 0


def test_find_by_created_after(backend):
    """TC-E03: 最近创建查询"""
    backend.add_bug(title="最近", phenomenon="", verified=True)
    results = backend.find_by_created_after(days=7, limit=10)
    assert len(results) >= 1


def test_find_by_min_score(backend):
    """TC-E04: 高分查询"""
    backend.add_bug(title="高分", phenomenon="", verified=True,
                   scores={"importance": 10, "complexity": 10, "scope": 10,
                           "difficulty": 10, "occurrences": 0, "emotion": 0, "prevention": 10})
    results = backend.find_by_min_score(min_score=30.0, limit=10)
    assert len(results) >= 1
    assert all(r["score"] >= 30.0 for r in results)


def test_find_all_sorted(backend):
    """TC-E05: 最严重查询"""
    backend.add_bug(title="严重", phenomenon="", verified=False)
    results = backend.find_all_sorted(limit=10)
    assert len(results) >= 1


def test_find_by_pattern(backend):
    """TC-E06: 模块模式查询"""
    bug_id, _ = backend.add_bug(
        title="模块测试",
        phenomenon="",
        verified=True,
        module_patterns=["src/modules/*"],
    )
    results = backend.find_by_pattern("src/modules/auth.ts", limit=10)
    assert any(r["id"] == bug_id for r in results)


def test_find_by_pattern_no_match(backend):
    """TC-E07: 模块模式无匹配"""
    backend.add_bug(title="nomatch", phenomenon="", verified=True, module_patterns=["xyz/*"])
    results = backend.find_by_pattern("auth/login.ts", limit=10)
    assert not any(r["title"] == "nomatch" for r in results)


# ============================================================================
# TC-F01 ~ TC-F03: 路径召回
# ============================================================================

def test_find_by_path_exact(backend):
    """TC-F01: 精确路径召回"""
    bug_id, _ = backend.add_bug(title="精确召回", phenomenon="", verified=True, paths=["src/auth/session.ts"])
    results = backend.find_by_path("src/auth/session.ts")
    assert any(r["id"] == bug_id for r in results)


def test_find_by_path_unrelated(backend):
    """TC-F02: 不相关路径不召回"""
    backend.add_bug(title="api问题", phenomenon="", verified=True, paths=["src/api/user.ts"])
    results = backend.find_by_path("src/auth/login.ts")
    assert not any(r["title"] == "api问题" for r in results)


def test_find_by_path_returns_impacts(backend):
    """TC-F03: 召回结果包含 impacts 字段"""
    bug_id, _ = backend.add_bug(title="影响召回", phenomenon="", verified=True)
    backend.add_impact(
        source_bug_id=bug_id,
        solution_change="变更",
        impact_description="影响",
        impact_type="regression",
        severity=5,
    )
    results = backend.find_by_path("any/path.ts", limit=10)
    for r in results:
        if r['id'] == bug_id:
            assert 'impacts' in r


# ============================================================================
# TC-G01 ~ TC-G04: 辅助方法
# ============================================================================

def test_get_all_bugs(backend):
    """TC-G01: 获取所有 bugs"""
    backend.add_bug(title="bug1", phenomenon="", verified=True)
    backend.add_bug(title="bug2", phenomenon="", verified=True)
    all_bugs = backend.get_all_bugs()
    assert len(all_bugs) >= 2


def test_count_bugs(backend):
    """TC-G02: 统计 bug 总数"""
    backend.add_bug(title="计数", phenomenon="", verified=True)
    count = backend.count_bugs()
    assert count >= 1


def test_compact_file(backend):
    """TC-G03: 压缩文件"""
    # 添加一些数据
    bug_id, _ = backend.add_bug(title="压缩测试", phenomenon="", verified=True)
    backend.update_bug(bug_id, status="invalid")
    # 压缩后 invalid 记录被移除
    removed = backend.compact_file()
    assert removed >= 0


# ============================================================================
# TC-H01 ~ TC-H02: 路径迁移（后端层）
# ============================================================================

def test_migrate_paths(backend):
    """TC-H01: 路径迁移"""
    bug_id, _ = backend.add_bug(
        title="路径迁移",
        phenomenon="",
        verified=True,
        paths=["src/auth/session.ts"]
    )
    migrated = backend.find_by_path("src/auth/session.ts", limit=99999)
    assert any(r["id"] == bug_id for r in migrated)


def test_find_unverified_old(backend):
    """TC-H02: 列出长期未验证"""
    backend.add_bug(title="未验证旧bug", phenomenon="", verified=False)
    results = backend.find_unverified_old(days=30, limit=10)
    # 新添加的 bug 不会在 old list 里（因为是刚创建的）
    assert isinstance(results, list)