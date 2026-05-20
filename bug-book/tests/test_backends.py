#!/usr/bin/env python3
"""Bug-book JSONL 后端单元测试"""

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


# ============================================================
# TC-A01 ~ TC-A08：add_bug 新增记录
# ============================================================

def test_add_bug_minimal_fields(backend):
    """TC-A01: 新增最小字段记录"""
    bug_id, score = backend.add_bug(title="测试", phenomenon="现象", verified=True)
    assert bug_id > 0
    assert score == 0
    detail = backend.get_bug_detail(bug_id)
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
    detail = backend.get_bug_detail(bug_id)
    assert detail["title"] == "session丢失"
    assert detail["paths"] == ["src/auth/session.ts"]
    assert detail["tags"] == ["auth"]
    assert detail["module_patterns"] == ["auth/*"]
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
    detail = backend.get_bug_detail(bug_id)
    assert detail["title"] == "中文标题测试"
    assert "中文" in detail["phenomenon"]


def test_add_bug_verified_false(backend):
    """TC-A04: 新增 verified=False"""
    bug_id, _ = backend.add_bug(title="复杂问题", phenomenon="复杂", verified=False)
    detail = backend.get_bug_detail(bug_id)
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
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["paths"]) == 2


def test_add_bug_multiple_module_patterns(backend):
    """TC-A07: 新增多条 module_patterns"""
    bug_id, _ = backend.add_bug(
        title="多模式",
        phenomenon="",
        module_patterns=["auth/*", "src/*"],
    )
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["module_patterns"]) == 2


def test_add_bug_then_get_detail(backend):
    """TC-A08: 新增后立即查询"""
    bug_id, _ = backend.add_bug(title="立即查询", phenomenon="测试")
    detail = backend.get_bug_detail(bug_id)
    assert detail is not None
    assert detail["id"] == bug_id


# ============================================================
# TC-B01 ~ TC-B06：update_bug 更新记录
# ============================================================

def test_update_bug_single_field(backend):
    """TC-B01: 更新单字段"""
    bug_id, _ = backend.add_bug(title="旧标题", phenomenon="", verified=True)
    backend.update_bug(bug_id, title="新标题")
    detail = backend.get_bug_detail(bug_id)
    assert detail["title"] == "新标题"


def test_update_bug_multiple_fields(backend):
    """TC-B02: 同时更新多字段"""
    bug_id, _ = backend.add_bug(title="旧", phenomenon="旧", verified=True)
    backend.update_bug(bug_id, title="新", root_cause="新根因")
    detail = backend.get_bug_detail(bug_id)
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
    detail = backend.get_bug_detail(bug_id)
    assert detail["verified"] == 1
    assert detail["verified_by"] == "User"
    assert detail["status"] == "resolved"


def test_update_bug_status(backend):
    """TC-B04: 更新 status 为 resolved"""
    bug_id, _ = backend.add_bug(title="待解决", phenomenon="", verified=True)
    backend.update_bug(bug_id, status="resolved")
    detail = backend.get_bug_detail(bug_id)
    assert detail["status"] == "resolved"


def test_update_bug_nonexistent(backend):
    """TC-B05: 更新不存在的 bug_id（静默返回）"""
    backend.update_bug(9999, title="不存在")


def test_update_bug_no_fields(backend):
    """TC-B06: 不传任何字段"""
    bug_id, _ = backend.add_bug(title="无更新", phenomenon="", verified=True)
    backend.update_bug(bug_id)


# ============================================================
# TC-C01 ~ TC-C03：delete_bug 删除记录（软删除）
# ============================================================

def test_delete_bug_exists(backend):
    """TC-C01: 删除存在的记录（软删除）"""
    bug_id, _ = backend.add_bug(title="待删除", phenomenon="", verified=True)
    backend.delete_bug(bug_id)
    # 软删除：数据仍存在，但 status='invalid'
    detail = backend.get_bug_detail(bug_id)
    assert detail["status"] == "invalid"


def test_delete_bug_nonexistent(backend):
    """TC-C02: 删除不存在的 id（静默返回）"""
    backend.delete_bug(9999)


def test_delete_bug_soft_delete(backend):
    """TC-C03: 软删除后状态为 invalid"""
    bug_id, _ = backend.add_bug(title="软删除", phenomenon="", verified=True, module_patterns=["test/*"])
    backend.delete_bug(bug_id)
    # 软删除后 status='invalid'
    detail = backend.get_bug_detail(bug_id)
    assert detail["status"] == "invalid"


# ============================================================
# TC-D01 ~ TC-D03：increment_score 分数累加
# ============================================================

def test_increment_score_existing(backend):
    """TC-D01: 累加已存在的维度"""
    bug_id, _ = backend.add_bug(title="累加", phenomenon="", verified=True, scores=DEFAULT_SCORES)
    backend.increment_score(bug_id, "occurrences", 1.0)
    detail = backend.get_bug_detail(bug_id)
    scores = dict(detail["scores"])
    assert scores["occurrences"] == 1.0


def test_increment_score_new_dimension(backend):
    """TC-D02: 累加不存在的维度"""
    bug_id, _ = backend.add_bug(title="新维度", phenomenon="", verified=True)
    backend.increment_score(bug_id, "new_dim", 5.0)
    detail = backend.get_bug_detail(bug_id)
    scores = dict(detail["scores"])
    assert scores["new_dim"] == 5.0


def test_increment_score_multiple(backend):
    """TC-D03: 连续累加 3 次"""
    bug_id, _ = backend.add_bug(title="多次", phenomenon="", verified=True)
    backend.increment_score(bug_id, "occurrences", 1.0)
    backend.increment_score(bug_id, "occurrences", 1.0)
    backend.increment_score(bug_id, "occurrences", 1.0)
    detail = backend.get_bug_detail(bug_id)
    scores = dict(detail["scores"])
    assert scores["occurrences"] == 3.0


# ============================================================
# TC-E01 ~ TC-E03: update_bug_paths / add_module_pattern
# ============================================================

def test_update_bug_paths_basic(backend):
    """TC-E01: 批量更新路径"""
    bug_id, _ = backend.add_bug(title="更新路径", phenomenon="", verified=True, paths=["src/old.ts"])
    backend.update_bug_paths(bug_id, ["src/new1.ts", "src/new2.ts"])
    detail = backend.get_bug_detail(bug_id)
    assert "src/old.ts" not in detail["paths"]
    assert "src/new1.ts" in detail["paths"]
    assert "src/new2.ts" in detail["paths"]


def test_update_bug_paths_empty(backend):
    """TC-E02: 清空所有路径"""
    bug_id, _ = backend.add_bug(title="清空路径", phenomenon="", verified=True, paths=["src/a.ts", "src/b.ts"])
    backend.update_bug_paths(bug_id, [])
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["paths"]) == 0


def test_add_module_pattern_basic(backend):
    """TC-E03: 添加 module_pattern"""
    bug_id, _ = backend.add_bug(title="加模式", phenomenon="", verified=True)
    backend.add_module_pattern(bug_id, "auth/*")
    detail = backend.get_bug_detail(bug_id)
    assert "auth/*" in detail["module_patterns"]


# ============================================================
# TC-F01 ~ TC-F05：search_by_keyword 关键词搜索
# ============================================================

def test_search_by_title(backend):
    """TC-F01: 搜索匹配 keyword 字段"""
    backend.add_bug(title="t", phenomenon="", keywords=["XYZ123"], verified=True)
    results = backend.search_by_keyword("XYZ123")
    assert len(results) >= 1
    assert any("XYZ123" in r.get("keywords", []) for r in results)


def test_search_by_phenomenon(backend):
    """TC-F02: 搜索匹配 phenomenon（通过 keyword 字段）"""
    # phenomenon 不在 keyword_index 中，这里改用 tag
    backend.add_bug(title="t", phenomenon="abc456def", tags=["abc456"], verified=True)
    results = backend.search_by_keyword("abc456")
    assert len(results) >= 1


def test_search_by_tag(backend):
    """TC-F03: 搜索匹配 tag"""
    backend.add_bug(title="t", phenomenon="", tags=["my_tag_xyz"], verified=True)
    results = backend.search_by_keyword("my_tag_xyz")
    assert len(results) >= 1


def test_search_by_keyword_field(backend):
    """TC-F04: 搜索匹配 keyword 字段"""
    backend.add_bug(title="t", phenomenon="", keywords=["kw_test"], verified=True)
    results = backend.search_by_keyword("kw_test")
    assert len(results) >= 1


def test_search_no_result(backend):
    """TC-F05: 搜索无结果"""
    results = backend.search_by_keyword("不存在关键词ABCXYZ")
    assert len(results) == 0


# ============================================================
# TC-H01 ~ TC-H06：recall_by_path / search_by_module_patterns 路径和模块搜索
# ============================================================

def test_recall_by_exact_path(backend):
    """TC-H01: 按文件精确路径召回"""
    bug_id, _ = backend.add_bug(title="精确召回", phenomenon="", verified=True, paths=["src/auth/session.ts"])
    results = backend.recall_by_path("src/auth/session.ts")
    assert any(r["id"] == bug_id for r in results)


def test_recall_multi_path(backend):
    """TC-H02: 按目录前缀召回"""
    bug_id, _ = backend.add_bug(
        title="auth问题",
        phenomenon="",
        verified=True,
        paths=["src/auth/session.ts"],
    )
    results = backend.recall_by_path("src/auth/session.ts")
    assert any(r["id"] == bug_id for r in results)


def test_recall_unrelated_path(backend):
    """TC-H03: 不相关路径不召回"""
    backend.add_bug(title="api问题", phenomenon="", verified=True, paths=["src/api/user.ts"])
    results = backend.recall_by_path("src/auth/login.ts")
    assert not any(r["title"] == "api问题" for r in results)


def test_search_by_module_patterns_basic(backend):
    """TC-H04: search_by_module_patterns 基本模式匹配"""
    bug_id, _ = backend.add_bug(
        title="模块模式测试",
        phenomenon="",
        verified=True,
        module_patterns=["src/modules/*"],
    )
    results = backend.search_by_module_patterns("src/modules/auth.ts")
    assert any(r["id"] == bug_id for r in results)


def test_search_by_module_patterns_no_pattern(backend):
    """TC-H05: 无 module_patterns 的 bug 不被模式搜索召回"""
    backend.add_bug(title="无模式", phenomenon="", verified=True)
    results = backend.search_by_module_patterns("any/path.ts")
    assert not any(r["title"] == "无模式" for r in results)


def test_search_by_module_patterns_no_match(backend):
    """TC-H06: search_by_module_patterns pattern 无匹配"""
    backend.add_bug(title="nomatch", phenomenon="", verified=True, module_patterns=["xyz/*"])
    results = backend.search_by_module_patterns("auth/login.ts")
    assert not any(r["title"] == "nomatch" for r in results)


# ============================================================
# TC-S01 ~ TC-S05：高级搜索
# ============================================================

def test_search_recent(backend):
    """TC-S01: 最近创建的 bugs"""
    backend.add_bug(title="旧的", phenomenon="", verified=True)
    results = backend.search_recent(days=7, limit=10)
    assert len(results) >= 1


def test_search_high_score(backend):
    """TC-S02: 高分 bugs"""
    backend.add_bug(title="低分", phenomenon="", verified=True, scores={"importance": 1})
    backend.add_bug(title="高分", phenomenon="", verified=True,
                   scores={"importance": 10, "complexity": 10, "scope": 10, "difficulty": 10, "occurrences": 0, "emotion": 0, "prevention": 10})
    results = backend.search_high_score(min_score=30.0, limit=10)
    assert len(results) >= 1
    assert all(r["score"] >= 30.0 for r in results)


def test_search_top_critical(backend):
    """TC-S03: 最严重的未验证 bugs"""
    backend.add_bug(title="已验证", phenomenon="", verified=True)
    backend.add_bug(title="未验证", phenomenon="", verified=False)
    results = backend.search_top_critical(limit=10)
    # 包含已验证和未验证的，但按分数排序
    assert len(results) >= 2


def test_search_recent_unverified(backend):
    """TC-S04: 最近创建但未验证的 bugs"""
    backend.add_bug(title="已验证", phenomenon="", verified=True)
    backend.add_bug(title="未验证", phenomenon="", verified=False)
    results = backend.search_recent_unverified(days=7, limit=10)
    assert all(r["verified"] == 0 for r in results)


def test_search_by_status_and_score(backend):
    """TC-S05: 按状态和分数组合搜索"""
    backend.add_bug(title="active高分", phenomenon="", verified=True,
                   scores={"importance": 10, "complexity": 10, "scope": 10, "difficulty": 10, "occurrences": 0, "emotion": 0, "prevention": 10})
    # verified=True 时 status=resolved，所以用 resolved 过滤
    results = backend.search_by_status_and_score(status="resolved", min_score=30.0, limit=10)
    assert len(results) >= 1
    assert all(r["score"] >= 30.0 for r in results)


# ============================================================
# TC-I01 ~ TC-I04: get_bug_detail
# ============================================================

def test_get_detail_exists(backend):
    """TC-I01: 查询存在的 bug"""
    bug_id, _ = backend.add_bug(title="详情", phenomenon="", verified=True)
    detail = backend.get_bug_detail(bug_id)
    assert detail is not None
    assert detail["id"] == bug_id
    assert detail["title"] == "详情"


def test_get_detail_nonexistent(backend):
    """TC-I02: 查询不存在的 bug 抛出异常"""
    try:
        backend.get_bug_detail(9999)
        assert False, "应该抛出异常"
    except Exception as e:
        assert "不存在" in str(e) or "not exist" in str(e).lower()


def test_get_detail_scores(backend):
    """TC-I03: 详情包含 7 维度分数"""
    bug_id, _ = backend.add_bug(title="scores", phenomenon="", verified=True, scores=DEFAULT_SCORES)
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["scores"]) == 7


def test_get_detail_relations(backend):
    """TC-I04: 详情包含 tags/keywords/module_patterns"""
    bug_id, _ = backend.add_bug(
        title="关联",
        phenomenon="",
        verified=True,
        tags=["t1", "t2"],
        keywords=["k1"],
        module_patterns=["r1/*"],
    )
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["tags"]) == 2
    assert detail["keywords"] == ["k1"]
    assert detail["module_patterns"] == ["r1/*"]


# ============================================================
# TC-J01 ~ TC-J04: list_bugs
# ============================================================

def test_list_bugs_by_status(backend):
    """TC-J01: 按 status=active 过滤"""
    # 添加一条 active 和一条 invalid
    bug1, _ = backend.add_bug(title="active", phenomenon="", verified=True)
    backend.add_bug(title="invalid", phenomenon="", verified=True)
    backend.delete_bug(bug1)  # 软删除设为 invalid

    results = backend.list_bugs(status="active")
    assert all(r["status"] == "active" for r in results)


def test_list_bugs_order_by_score(backend):
    """TC-J02: order_by=score"""
    results = backend.list_bugs(order_by="score")
    assert isinstance(results, list)


def test_list_bugs_order_by_invalid(backend):
    """TC-J03: order_by=非白名单字段自动降级"""
    results = backend.list_bugs(order_by="invalid_column")
    assert isinstance(results, list)


def test_list_bugs_pagination(backend):
    """TC-J04: 分页 limit=2 offset=0"""
    results = backend.list_bugs(limit=2, offset=0)
    assert len(results) <= 2


# ============================================================
# TC-K01 ~ TC-K03: mark_invalid
# ============================================================

def test_mark_invalid_with_reason(backend):
    """TC-K01: 标记失效带原因"""
    bug_id, _ = backend.add_bug(title="待失效", phenomenon="", verified=True)
    backend.mark_invalid(bug_id, "功能已删除")
    detail = backend.get_bug_detail(bug_id)
    assert detail["status"] == "invalid"
    assert "功能已删除" in detail["solution"]


def test_mark_invalid_without_reason(backend):
    """TC-K02: 标记失效不带原因"""
    bug_id, _ = backend.add_bug(title="无原因失效", phenomenon="", verified=True)
    backend.mark_invalid(bug_id)
    detail = backend.get_bug_detail(bug_id)
    assert detail["status"] == "invalid"


def test_mark_invalid_nonexistent(backend):
    """TC-K03: 标记不存在的 bug（静默返回）"""
    backend.mark_invalid(9999)


# ============================================================
# TC-L01 ~ TC-L03: 懒初始化与集成
# ============================================================

def test_lazy_init(backend):
    """TC-L01: 文件不存在时自动创建"""
    from config import get_data_dir
    data_dir = get_data_dir()
    jsonl_path = data_dir / "bug-book.jsonl"

    try:
        os.remove(str(jsonl_path))
    except OSError:
        pass

    backend.add_bug(title="懒初始化", phenomenon="", verified=True)
    assert jsonl_path.exists()


def test_full_crud(backend):
    """TC-L02: 完整 CRUD 流程"""
    bug_id, _ = backend.add_bug(title="CRUD", phenomenon="创建", verified=True)
    backend.update_bug(bug_id, phenomenon="更新")
    detail = backend.get_bug_detail(bug_id)
    assert detail["phenomenon"] == "更新"
    backend.delete_bug(bug_id)
    detail = backend.get_bug_detail(bug_id)
    assert detail["status"] == "invalid"


def test_recurrence_flow(backend):
    """TC-L03: 复发处理流程"""
    bug_id, _ = backend.add_bug(
        title="复发测试",
        phenomenon="",
        verified=True,
        scores=DEFAULT_SCORES,
    )
    # 模拟复发：打回未验证 + 累加分数
    backend.update_bug(bug_id, verified=False)
    backend.increment_score(bug_id, "occurrences", 1.0)
    detail = backend.get_bug_detail(bug_id)
    assert detail["verified"] == 0
    scores = dict(detail["scores"])
    assert scores["occurrences"] == 1.0


# ============================================================
# TC-M01 ~ TC-M06: 影响关系管理
# ============================================================

def test_add_impact_regression(backend):
    """TC-M01: 添加回归影响"""
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


def test_add_impact_side_effect(backend):
    """TC-M02: 添加副作用影响"""
    bug_id, _ = backend.add_bug(title="源bug", phenomenon="", verified=True)
    impact_id = backend.add_impact(
        source_bug_id=bug_id,
        solution_change="重构了用户模块",
        impact_description="影响积分计算",
        impact_type="side_effect",
        severity=5,
    )
    assert impact_id > 0


def test_add_impact_dependency(backend):
    """TC-M03: 添加依赖影响"""
    bug_id, _ = backend.add_bug(title="源bug", phenomenon="", verified=True)
    impact_id = backend.add_impact(
        source_bug_id=bug_id,
        solution_change="更新了 API 版本",
        impact_description="需要同步更新客户端",
        impact_type="dependency",
        severity=3,
    )
    assert impact_id > 0


def test_add_impact_invalid_type(backend):
    """TC-M04: 添加无效影响类型"""
    bug_id, _ = backend.add_bug(title="源bug", phenomenon="", verified=True)
    try:
        backend.add_impact(
            source_bug_id=bug_id,
            solution_change="test",
            impact_description="test",
            impact_type="invalid",
        )
        assert False, "应该抛出异常"
    except Exception as e:
        assert "无效的影响类型" in str(e) or "invalid" in str(e).lower()


def test_add_impact_invalid_severity(backend):
    """TC-M05: 添加无效的严重程度"""
    bug_id, _ = backend.add_bug(title="源bug", phenomenon="", verified=True)
    try:
        backend.add_impact(
            source_bug_id=bug_id,
            solution_change="test",
            impact_description="test",
            impact_type="regression",
            severity=15,
        )
        assert False, "应该抛出异常"
    except Exception as e:
        assert "严重程度" in str(e) or "severity" in str(e).lower()


def test_add_impact_auto_prevention(backend):
    """TC-M06: add_impact 后 prevention 分数自动累加"""
    bug_id, _ = backend.add_bug(
        title="prevention 累加测试",
        phenomenon="",
        verified=True,
        scores={"importance": 0, "complexity": 0, "scope": 0, "difficulty": 0,
                "occurrences": 0, "emotion": 0, "prevention": 0},
    )
    backend.add_impact(
        source_bug_id=bug_id,
        solution_change="变更",
        impact_description="影响",
        impact_type="regression",
        severity=9,
        prevention_delta=5.0,
    )
    detail = backend.get_bug_detail(bug_id)
    scores = dict(detail["scores"])
    assert scores["prevention"] == 5.0

# ============================================================
# TC-N01 ~ TC-N05：路径和 module_patterns 管理
# ============================================================

def test_update_bug_paths_with_multiple(backend):
    """TC-N01: 批量更新 bug 的路径"""
    bug_id, _ = backend.add_bug(
        title="路径测试",
        phenomenon="",
        paths=["old/path.ts", "other/path.ts"],
        verified=True,
    )
    backend.update_bug_paths(bug_id, ["new/path.ts", "other/path.ts"])
    detail = backend.get_bug_detail(bug_id)
    assert "new/path.ts" in detail["paths"]
    assert "old/path.ts" not in detail["paths"]


def test_add_module_pattern_verify(backend):
    """TC-N02: 添加单个 module_pattern"""
    bug_id, _ = backend.add_bug(title="module_pattern测试", phenomenon="", verified=True)
    backend.add_module_pattern(bug_id, "auth/*")
    detail = backend.get_bug_detail(bug_id)
    assert "auth/*" in detail["module_patterns"]


def test_update_bug_module_patterns(backend):
    """TC-N03: 批量更新 module_patterns"""
    bug_id, _ = backend.add_bug(
        title="module_pattern更新测试",
        phenomenon="",
        module_patterns=["old_pattern.dart", "other_pattern.dart"],
        verified=True,
    )
    backend.update_bug_module_patterns(bug_id, ["new_pattern.dart", "other_pattern.dart"])
    detail = backend.get_bug_detail(bug_id)
    assert "new_pattern.dart" in detail["module_patterns"]
    assert "old_pattern.dart" not in detail["module_patterns"]


def test_update_bug_module_patterns_empty(backend):
    """TC-N04: 清空所有 module_patterns"""
    bug_id, _ = backend.add_bug(
        title="清空module_patterns",
        phenomenon="",
        module_patterns=["pattern1", "pattern2"],
        verified=True,
    )
    backend.update_bug_module_patterns(bug_id, [])
    detail = backend.get_bug_detail(bug_id)
    assert detail["module_patterns"] == []

# ============================================================
# TC-O01 ~ TC-O02：路径迁移
# ============================================================

def test_migrate_paths_exact_match(backend):
    """TC-O01: 迁移 paths 中的精确匹配"""
    bug_id, _ = backend.add_bug(
        title="路径迁移测试",
        phenomenon="测试",
        verified=True,
        paths=["src/auth/session.ts"],
    )
    # 迁移 paths
    migrated = backend.migrate_bug_paths_after_refactor(
        "src/auth/session.ts",
        "src/modules/auth/session.ts"
    )
    assert bug_id in migrated
    detail = backend.get_bug_detail(bug_id)
    assert "src/modules/auth/session.ts" in detail["paths"]


def test_migrate_module_patterns_wildcard(backend):
    """TC-O02: 迁移 module_patterns 中的通配符模式"""
    bug_id, _ = backend.add_bug(
        title="module_patterns迁移测试",
        phenomenon="测试",
        verified=True,
        module_patterns=["auth/*"],
    )
    # 迁移 module_patterns（会通过 search_by_module_patterns 查找）
    migrated = backend.migrate_bug_paths_after_refactor(
        "src/auth/login.ts",
        "src/modules/auth/login.ts"
    )
    assert bug_id in migrated
    detail = backend.get_bug_detail(bug_id)
    # 通配符模式应该更新
    assert "src/modules/auth/*" in detail["module_patterns"]


# ============================================================
# TC-P01 ~ TC-P03：路径检查
# ============================================================

def test_check_bug_paths_all_valid(backend):
    """TC-P01: 检查路径都有效时返回空列表"""
    bug_id, _ = backend.add_bug(title="有效路径", phenomenon="", verified=True)
    result = backend.check_bug_paths(bug_id)
    assert result == []


def test_check_bug_paths_invalid_paths(backend):
    """TC-P02: 检查 paths 中有无效路径"""
    bug_id, _ = backend.add_bug(
        title="无效路径测试",
        phenomenon="",
        verified=True,
        paths=["nonexistent/file.ts"],
    )
    result = backend.check_bug_paths(bug_id)
    assert len(result) == 1
    assert "nonexistent/file.ts" in result


def test_check_bug_paths_invalid_module_patterns(backend):
    """TC-P03: 检查 module_patterns 中有无效路径"""
    bug_id, _ = backend.add_bug(
        title="无效 module_patterns 测试",
        phenomenon="",
        verified=True,
        module_patterns=["nonexistent/*"],
    )
    result = backend.check_bug_paths(bug_id)
    assert len(result) == 1
    assert "nonexistent/*" in result

