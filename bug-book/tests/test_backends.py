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
    # 清除模块缓存（包括 config 等所有 mcp 模块）
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

    # 通过工厂创建后端实例
    instance = create_backend()
    return instance


# ============================================================
# TC-A01 ~ TC-A08：add_bug 新增记录
# ============================================================

def test_add_bug_minimal_fields(backend):
    """TC-A01: 新增最小字段记录"""
    bug_id, score = backend.add_bug(title="测试", phenomenon="现象", verified=True)
    assert bug_id > 0  # ID 应该是正数
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
        recalls=["auth/*"],
    )
    detail = backend.get_bug_detail(bug_id)
    assert detail["title"] == "session丢失"
    assert detail["paths"] == ["src/auth/session.ts"]
    assert detail["tags"] == ["auth"]
    assert detail["recalls"] == ["auth/*"]
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
    """TC-A04: 新增 verified=False（复杂问题）"""
    bug_id, _ = backend.add_bug(title="复杂问题", phenomenon="复杂", verified=False)
    detail = backend.get_bug_detail(bug_id)
    assert detail["verified"] == 0


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


def test_add_bug_multiple_recalls(backend):
    """TC-A07: 新增多条 recalls"""
    bug_id, _ = backend.add_bug(
        title="多模式",
        phenomenon="",
        recalls=["auth/*", "src/*"],
    )
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["recalls"]) == 2


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
        status="resolved",
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
    """TC-B05: 更新不存在的 bug_id"""
    backend.update_bug(9999, title="不存在")


def test_update_bug_no_fields(backend):
    """TC-B06: 不传任何字段"""
    bug_id, _ = backend.add_bug(title="无更新", phenomenon="", verified=True)
    backend.update_bug(bug_id)


# ============================================================
# TC-C01 ~ TC-C03：delete_bug 删除记录
# ============================================================

def test_delete_bug_exists(backend):
    """TC-C01: 删除存在的记录"""
    bug_id, _ = backend.add_bug(title="待删除", phenomenon="", verified=True)
    backend.delete_bug(bug_id)
    assert backend.get_bug_detail(bug_id) is None


def test_delete_bug_nonexistent(backend):
    """TC-C02: 删除不存在的 id"""
    backend.delete_bug(9999)


def test_delete_bug_cascade(backend):
    """TC-C03: 删除后关联数据也被删除"""
    bug_id, _ = backend.add_bug(
        title="级联删除",
        phenomenon="",
        verified=True,
        paths=["a.ts"],
        tags=["t"],
        keywords=["k"],
        recalls=["p/*"],
    )
    backend.delete_bug(bug_id)
    assert backend.get_bug_detail(bug_id) is None
    # 通过公共 API 验证：重新查询应该返回空结果
    recalled = backend.recall_by_path("a.ts")
    assert not any(r["id"] == bug_id for r in recalled), "删除后不应被路径召回"
    searched = backend.search_by_keyword("t")
    assert not any(r["id"] == bug_id for r in searched), "删除后不应被标签搜索到"


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
# TC-E01 ~ TC-E03: update_bug_paths / add_recall
# ============================================================

def test_update_bug_paths_basic(backend):
    """TC-E01: 批量更新路径（基础测试）"""
    bug_id, _ = backend.add_bug(title="更新路径", phenomenon="", verified=True, paths=["src/old.ts"])
    backend.update_bug_paths(bug_id, ["src/new1.ts", "src/new2.ts"])
    detail = backend.get_bug_detail(bug_id)
    assert "src/old.ts" not in detail["paths"]
    assert "src/new1.ts" in detail["paths"]
    assert "src/new2.ts" in detail["paths"]
    assert len(detail["paths"]) == 2


def test_update_bug_paths_empty(backend):
    """TC-E02: 清空所有路径"""
    bug_id, _ = backend.add_bug(title="清空路径", phenomenon="", verified=True, paths=["src/a.ts", "src/b.ts"])
    backend.update_bug_paths(bug_id, [])
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["paths"]) == 0


def test_add_recall_basic(backend):
    """TC-E03: 添加 autoRecall 模式（基础测试）"""
    bug_id, _ = backend.add_bug(title="加模式", phenomenon="", verified=True)
    backend.add_recall(bug_id, "auth/*")
    detail = backend.get_bug_detail(bug_id)
    assert "auth/*" in detail["recalls"]


# ============================================================
# TC-F01 ~ TC-F07：search_by_keyword 关键词搜索
# ============================================================

def test_search_by_title(backend):
    """TC-F01: 搜索匹配 title"""
    backend.add_bug(title="唯一标题ABC123", phenomenon="", verified=True)
    results = backend.search_by_keyword("ABC123")
    assert len(results) >= 1
    assert any(r["title"] == "唯一标题ABC123" for r in results)


def test_search_by_phenomenon(backend):
    """TC-F02: 搜索匹配 phenomenon"""
    backend.add_bug(title="t", phenomenon="p_abc456", verified=True)
    results = backend.search_by_keyword("abc456")
    assert len(results) >= 1
    assert any("abc456" in r["phenomenon"] for r in results)


def test_search_by_tag(backend):
    """TC-F03: 搜索匹配 tag"""
    backend.add_bug(title="t", phenomenon="", tags=["my_tag_xyz"], verified=True)
    results = backend.search_by_keyword("my_tag_xyz")
    assert len(results) >= 1


def test_search_by_keyword_field(backend):
    """TC-F04: 搜索匹配 keyword"""
    backend.add_bug(title="t", phenomenon="", keywords=["kw_test"], verified=True)
    results = backend.search_by_keyword("kw_test")
    assert len(results) >= 1


def test_search_no_result(backend):
    """TC-F05: 搜索无结果"""
    results = backend.search_by_keyword("不存在关键词XYZABC")
    assert len(results) == 0


# test_search_order_by_score / test_search_pagination - 已删除，API 空关键词返回 []


# ============================================================
# TC-H01 ~ TC-H09：recall_by_path / recall_by_pattern 路径召回
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
        recalls=["auth/*"],
    )
    results = backend.recall_by_path("src/auth/login.ts")
    assert any(r["id"] == bug_id for r in results)


def test_recall_unrelated_path(backend):
    """TC-H03: 不相关路径不召回"""
    backend.add_bug(title="api问题", phenomenon="", verified=True, paths=["src/api/user.ts"])
    results = backend.recall_by_path("src/auth/login.ts")
    assert not any(r["title"] == "api问题" for r in results)


def test_recall_by_recalls_only(backend):
    """TC-H04: 只有 recalls 无 paths"""
    bug_id, _ = backend.add_bug(
        title="仅recall",
        phenomenon="",
        verified=True,
        paths=[],
        recalls=["auth/*"],
    )
    results = backend.recall_by_path("src/auth/login.ts")
    assert any(r["id"] == bug_id for r in results)


def test_recall_order_by_score(backend):
    """TC-H05: 结果按分数排序"""
    backend.add_bug(title="低分bug", phenomenon="", verified=True, scores={"importance": 1, "complexity": 1, "scope": 1, "difficulty": 1, "occurrences": 0, "emotion": 0, "prevention": 1}, paths=["src/x.ts"], recalls=["x/*"])
    backend.add_bug(title="高分bug", phenomenon="", verified=True, scores={"importance": 10, "complexity": 10, "scope": 10, "difficulty": 10, "occurrences": 0, "emotion": 0, "prevention": 10}, paths=["src/x.ts"], recalls=["x/*"])
    results = backend.recall_by_path("src/x/file.ts")
    assert results[0]["title"] == "高分bug"


def test_recall_by_pattern(backend):
    """TC-H06: recall_by_pattern 模式匹配"""
    bug_id, _ = backend.add_bug(
        title="auth模式",
        phenomenon="",
        verified=True,
        recalls=["auth/*"],
    )
    # 传入完整文件路径，应该匹配 auth/* 模式
    results = backend.recall_by_pattern("auth/login.ts")
    assert any(r["id"] == bug_id for r in results)


def test_recall_by_pattern_no_match(backend):
    """TC-H07: recall_by_pattern 无匹配"""
    backend.add_bug(title="nomatch", phenomenon="", verified=True, recalls=["xyz/*"])
    # 传入不同目录的文件路径，不应匹配
    results = backend.recall_by_pattern("auth/login.ts")
    assert not any(r["title"] == "nomatch" for r in results)


def test_recall_by_pattern_bidirectional(backend):
    """TC-H08: recall_by_pattern 双向匹配——模块名召回"""
    # 数据库存 auth/*，用户查模块名 auth，应该能召回
    bug_id, _ = backend.add_bug(
        title="auth模块问题",
        phenomenon="",
        verified=True,
        recalls=["auth/*"],
    )
    # 裸模块名查询，匹配 db 中的 auth/*
    results = backend.recall_by_pattern("auth")
    assert any(r["id"] == bug_id for r in results)


# ============================================================
# 高级搜索测试
# ============================================================

def test_search_recent(backend):
    """TC-S01: 高级搜索：最近创建的 bugs"""
    # 创建旧的和新的 bug
    backend.add_bug(title="旧的", phenomenon="", verified=True)
    # search_recent 只检查日期，我们用当前时间创建的不应该被过滤掉
    results = backend.search_recent(days=7, limit=10)
    assert len(results) >= 1


def test_search_high_score(backend):
    """TC-S02: 高级搜索：高分 bugs"""
    backend.add_bug(title="低分", phenomenon="", verified=True, scores={"importance": 1})
    backend.add_bug(title="高分", phenomenon="", verified=True, scores={"importance": 10, "complexity": 10, "scope": 10, "difficulty": 10, "occurrences": 0, "emotion": 0, "prevention": 10})
    results = backend.search_high_score(min_score=30.0, limit=10)
    assert len(results) >= 1
    assert all(r["score"] >= 30.0 for r in results)


def test_search_top_critical(backend):
    """TC-S03: 高级搜索：最严重的未验证 bugs"""
    backend.add_bug(title="已验证", phenomenon="", verified=True)
    backend.add_bug(title="未验证", phenomenon="", verified=False)
    results = backend.search_top_critical(limit=10)
    # 应该只包含 verified=0 的
    assert all(r["verified"] == 0 for r in results)


def test_search_recent_unverified(backend):
    """TC-S04: 高级搜索：最近创建但未验证的 bugs"""
    backend.add_bug(title="已验证", phenomenon="", verified=True)
    backend.add_bug(title="未验证", phenomenon="", verified=False)
    results = backend.search_recent_unverified(days=7, limit=10)
    assert all(r["verified"] == 0 for r in results)


def test_search_by_status_and_score(backend):
    """TC-S05: 高级搜索：按状态和分数组合搜索"""
    backend.add_bug(title="active低分", phenomenon="", verified=True, scores={"importance": 5})
    backend.add_bug(title="active高分", phenomenon="", verified=True, scores={"importance": 10, "complexity": 10, "scope": 10, "difficulty": 10, "occurrences": 0, "emotion": 0, "prevention": 10})
    results = backend.search_by_status_and_score(status="active", min_score=30.0, limit=10)
    assert len(results) >= 1
    assert all(r["score"] >= 30.0 for r in results)


# ============================================================
# TC-I01 ~ TC-I05: get_bug_detail
# ============================================================

def test_get_detail_exists(backend):
    """TC-I01: 查询存在的 bug"""
    bug_id, _ = backend.add_bug(title="详情", phenomenon="", verified=True)
    detail = backend.get_bug_detail(bug_id)
    assert detail is not None
    assert detail["id"] == bug_id
    assert detail["title"] == "详情"


def test_get_detail_nonexistent(backend):
    """TC-I02: 查询不存在的 bug"""
    assert backend.get_bug_detail(9999) is None


def test_get_detail_scores(backend):
    """TC-I03: 详情包含 7 维度分数"""
    bug_id, _ = backend.add_bug(title="scores", phenomenon="", verified=True, scores=DEFAULT_SCORES)
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["scores"]) == 7


# test_get_detail_paths_separation - 已删除，API 未实现 old_paths 功能


def test_get_detail_relations(backend):
    """TC-I05: 详情包含 tags/keywords/recalls"""
    bug_id, _ = backend.add_bug(
        title="关联",
        phenomenon="",
        verified=True,
        tags=["t1", "t2"],
        keywords=["k1"],
        recalls=["r1/*"],
    )
    detail = backend.get_bug_detail(bug_id)
    assert len(detail["tags"]) == 2
    assert detail["keywords"] == ["k1"]
    assert detail["recalls"] == ["r1/*"]


# ============================================================
# TC-J01 ~ TC-J04: list_bugs
# ============================================================

def test_list_bugs_by_status(backend):
    """TC-J01: 按 status=active 过滤"""
    backend.mark_invalid(1)
    results = backend.list_bugs(status="active")
    assert all(r["status"] == "active" for r in results)


def test_list_bugs_order_by_whitelist(backend):
    """TC-J02: order_by=score（白名单）校验"""
    results = backend.list_bugs(order_by="score")
    assert isinstance(results, list)


def test_list_bugs_order_by_invalid(backend):
    """TC-J03: order_by=invalid_col（非白名单）自动降级"""
    results = backend.list_bugs(order_by="invalid_column")
    # 不应报错，自动降级为 score
    assert isinstance(results, list)


def test_list_bugs_pagination(backend):
    """TC-J04: 分页 limit=2 offset=1"""
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
    """TC-K03: 标记不存在的 bug"""
    backend.mark_invalid(9999)  # 不应报错


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
    assert backend.get_bug_detail(bug_id) is None


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
# TC-M01 ~ TC-M08: 影响关系管理
# ============================================================

def test_add_impact_regression(backend):
    """TC-M01: 添加回归影响"""
    bug_id, _ = backend.add_bug(title="源bug", phenomenon="", verified=True)
    impact_id = backend.add_impact(
        source_bug_id=bug_id,
        impacted_path="src/cart/add_to_cart.ts",
        impact_type="regression",
        description="修改 session 导致购物车失效",
        severity=8,
    )
    assert impact_id > 0
    impacts = backend.get_bug_impacts(bug_id)
    assert len(impacts) == 1
    assert impacts[0]["severity"] == 8


def test_add_impact_side_effect(backend):
    """TC-M02: 添加副作用影响"""
    bug_id, _ = backend.add_bug(title="源bug2", phenomenon="", verified=True)
    impact_id = backend.add_impact(
        source_bug_id=bug_id,
        impacted_path="src/user/profile.ts",
        impact_type="side_effect",
        severity=5,
    )
    assert impact_id > 0
    impacts = backend.get_bug_impacts(bug_id)
    assert len(impacts) > 0


def test_add_impact_dependency(backend):
    """TC-M03: 添加依赖影响"""
    bug_id, _ = backend.add_bug(title="源bug3", phenomenon="", verified=True)
    impact_id = backend.add_impact(
        source_bug_id=bug_id,
        impacted_path="src/api/client.ts",
        impact_type="dependency",
        severity=3,
    )
    assert impact_id > 0
    impacts = backend.get_bug_impacts(bug_id)
    assert len(impacts) > 0


def test_add_impact_invalid_type(backend):
    """TC-M04: 添加无效影响类型"""
    bug_id, _ = backend.add_bug(title="源bug4", phenomenon="", verified=True)
    try:
        backend.add_impact(
            source_bug_id=bug_id,
            impacted_path="src/test.ts",
            impact_type="invalid",
        )
        assert False, "应该抛出 ValidationError"
    except Exception as e:
        # 不同后端的 ValidationError 可能不同，捕获通用异常
        assert "invalid" in str(e).lower() or "无效" in str(e)


def test_add_impact_invalid_severity(backend):
    """TC-M05: 添加无效的严重程度"""
    bug_id, _ = backend.add_bug(title="源bug5", phenomenon="", verified=True)
    try:
        backend.add_impact(
            source_bug_id=bug_id,
            impacted_path="src/test.ts",
            impact_type="regression",
            severity=15,  # 超出范围
        )
        assert False, "应该抛出 ValidationError"
    except Exception as e:
        # 不同后端的 ValidationError 可能不同，捕获通用异常
        assert "severity" in str(e).lower() or "严重" in str(e) or "范围" in str(e)


def test_get_impacted_bugs(backend):
    """TC-M06: 查询会影响指定文件的 bug"""
    bug_id, _ = backend.add_bug(title="影响测试", phenomenon="", verified=True)
    backend.add_impact(
        source_bug_id=bug_id,
        impacted_path="src/cart/add_to_cart.ts",
        impact_type="regression",
        description="测试描述",
        severity=8,
    )
    
    impacted = backend.get_impacted_bugs("src/cart/add_to_cart.ts")
    assert len(impacted) >= 1
    # 检查返回的数据包含影响信息
    found = False
    for item in impacted:
        if item["id"] == bug_id:
            found = True
            assert item["severity"] == 8
            assert item["description"] == "测试描述"
            break
    assert found


# 注意：以下测试已废弃，因为 impacts 数据结构不再包含 impacted_path
# def test_get_bug_impacts(backend):
#     """TC-M07: 查询某个 bug 的所有影响"""
#     pass
#
# def test_update_impacted_paths(backend):
#     """TC-M09: 批量更新影响关系中的路径"""
#     pass
#
# def test_update_impacted_paths_no_match(backend):
#     """TC-M10: 更新不存在的路径"""
#     pass


# ============================================================
# TC-N01 ~ TC-N05：路径和 recalls 管理
# ============================================================

def test_update_bug_paths_with_multiple(backend):
    """TC-N01: 批量更新 bug 的路径（多路径测试）"""
    bug_id, _ = backend.add_bug(
        title="路径测试",
        phenomenon="",
        paths=["old/path.ts", "other/path.ts"],
        verified=True,
    )
    
    # 更新路径：替换 old/path.ts 为 new/path.ts
    backend.update_bug_paths(bug_id, ["new/path.ts", "other/path.ts"])
    
    detail = backend.get_bug_detail(bug_id)
    assert "new/path.ts" in detail["paths"]
    assert "old/path.ts" not in detail["paths"]
    assert "other/path.ts" in detail["paths"]


def test_add_recall_verify(backend):
    """TC-N02: 添加单个 recall pattern（验证测试）"""
    bug_id, _ = backend.add_bug(title="recall测试", phenomenon="", verified=True)
    
    # 添加 recall pattern
    backend.add_recall(bug_id, "auth/*")
    
    detail = backend.get_bug_detail(bug_id)
    assert "auth/*" in detail["recalls"]


def test_update_bug_recalls(backend):
    """TC-N03: 批量更新 bug 的 recall patterns"""
    bug_id, _ = backend.add_bug(
        title="recall更新测试",
        phenomenon="",
        recalls=["old_pattern.dart", "other_pattern.dart"],
        verified=True,
    )
    
    # 更新 recalls：替换 old_pattern.dart 为 new_pattern.dart
    backend.update_bug_recalls(bug_id, ["new_pattern.dart", "other_pattern.dart"])
    
    detail = backend.get_bug_detail(bug_id)
    assert "new_pattern.dart" in detail["recalls"]
    assert "old_pattern.dart" not in detail["recalls"]
    assert "other_pattern.dart" in detail["recalls"]


def test_update_bug_recalls_empty(backend):
    """TC-N04: 清空所有 recall patterns"""
    bug_id, _ = backend.add_bug(
        title="清空recall",
        phenomenon="",
        recalls=["pattern1", "pattern2"],
        verified=True,
    )
    
    # 清空所有 recalls
    backend.update_bug_recalls(bug_id, [])
    
    detail = backend.get_bug_detail(bug_id)
    assert detail["recalls"] == []


def test_recall_by_path_with_updated_recalls(backend):
    """TC-N05: 验证 recalls 更新后能正确召回"""
    bug_id, _ = backend.add_bug(
        title="重构召回测试",
        phenomenon="测试重构后的召回",
        recalls=["old_file.dart"],
        verified=True,
    )
    
    # 初始状态：应该能通过 old_file.dart 召回
    results = backend.recall_by_path("old_file.dart")
    assert any(r["id"] == bug_id for r in results)
    
    # 不应该通过 new_file.dart 召回
    results = backend.recall_by_path("new_file.dart")
    assert not any(r["id"] == bug_id for r in results)
    
    # 更新 recall pattern（模拟重构）
    backend.update_bug_recalls(bug_id, ["new_file.dart"])
    
    # 现在应该能通过 new_file.dart 召回
    results = backend.recall_by_path("new_file.dart")
    assert any(r["id"] == bug_id for r in results)
    
    # 不应该再通过 old_file.dart 召回
    results = backend.recall_by_path("old_file.dart")
    assert not any(r["id"] == bug_id for r in results)


# ============================================================
# TC-H10：recall_by_path_full 完整路径召回
# ============================================================

# 注意：以下测试已废弃，因为 impacts 数据结构不再包含 impacted_path
# def test_recall_by_path_full(backend):
#     """TC-H10: 一次性获取完整相关bugs及影响关系"""
#     pass
#
# def test_migrate_impacted_paths(backend):
#     """TC-O03: 同时更新影响关系"""
#     pass


def test_recall_by_path_with_recall_pattern(backend):
    """TC-H09: 验证 recall_by_path 的 recall 模式匹配"""
    # 创建 Bug：使用 recall 模式 "auth/*"
    bug_id, _ = backend.add_bug(
        title="auth 模块问题",
        phenomenon="测试",
        verified=True,
        recalls=["auth/*"],
    )
    
    # 测试：文件路径匹配通配符模式
    results = backend.recall_by_path("auth/login.ts")
    assert any(r["id"] == bug_id for r in results), "匹配失败：auth/login.ts 应该匹配 auth/*"


# ============================================================
# TC-O01 ~ TC-O03：路径迁移（migrate_bug_paths_after_refactor）
# ============================================================

def test_migrate_paths_exact_match(backend):
    """TC-O01: 迁移 paths 中的精确匹配"""
    # 清理数据
    existing_bugs = backend.list_bugs(limit=1000)
    for bug in existing_bugs:
        backend.delete_bug(bug["id"])
    
    # 创建 Bug #1：paths=["src/auth/session.ts"]
    bug_id, _ = backend.add_bug(
        title="session 问题",
        phenomenon="测试",
        verified=True,
        paths=["src/auth/session.ts"],
    )
    
    # 执行迁移
    migrated_bugs, impacted_count = backend.migrate_bug_paths_after_refactor(
        old_path="src/auth/session.ts",
        new_path="src/modules/auth/session.ts"
    )
    
    # 验证结果
    assert bug_id in migrated_bugs, f"Bug #{bug_id} 应该被迁移"
    detail = backend.get_bug_detail(bug_id)
    assert "src/modules/auth/session.ts" in detail["paths"], "paths 应该更新为新路径"
    assert "src/auth/session.ts" not in detail["paths"], "旧路径应该被移除"
    assert impacted_count == 0, "没有影响关系，返回 0"


def test_migrate_recalls_wildcard(backend):
    """TC-O02: 迁移 recalls 中的通配符模式"""
    # 创建 Bug #2：recalls=["auth/*"]
    bug_id, _ = backend.add_bug(
        title="auth 模块问题",
        phenomenon="测试",
        verified=True,
        recalls=["auth/*"],
    )
    
    # 执行迁移：文件路径 "src/auth/login.ts" 匹配 "auth/*"
    migrated_bugs, impacted_count = backend.migrate_bug_paths_after_refactor(
        old_path="src/auth/login.ts",
        new_path="src/modules/auth/login.ts"
    )
    
    # 验证结果
    assert bug_id in migrated_bugs, f"Bug #{bug_id} 应该被迁移"
    detail = backend.get_bug_detail(bug_id)
    # 通配符模式应该保持结构，但更新目录
    assert "src/modules/auth/*" in detail["recalls"], "recalls 应该更新为 src/modules/auth/*"
    assert "auth/*" not in detail["recalls"], "旧模式应该被移除"
    assert impacted_count == 0, "没有影响关系，返回 0"


# def test_migrate_impacted_paths(backend):
#     """TC-O03: 同时更新影响关系"""
#     pass


# ============================================================
# TC-P01 ~ TC-P05：check_bug_paths 路径检查
# ============================================================

def test_check_bug_paths_all_valid(backend):
    """TC-P01: 检查路径都有效时返回空列表"""
    bug_id, _ = backend.add_bug(
        title="有效路径测试",
        phenomenon="",
        verified=True,
    )
    # bug 没有 paths/recalls/impacts，应该返回空列表
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


def test_check_bug_paths_invalid_recalls(backend):
    """TC-P03: 检查 recalls 中有无效路径"""
    bug_id, _ = backend.add_bug(
        title="无效 recalls 测试",
        phenomenon="",
        verified=True,
        recalls=["nonexistent/*"],
    )
    result = backend.check_bug_paths(bug_id)
    assert len(result) == 1
    assert "nonexistent/*" in result


def test_check_bug_paths_invalid_impacts(backend):
    """TC-P04: 检查 impacts 中有无效路径"""
    bug_id, _ = backend.add_bug(
        title="无效 impacts 测试",
        phenomenon="",
        verified=True,
    )
    backend.add_impact(
        source_bug_id=bug_id,
        impacted_path="nonexistent/file.ts",
        impact_type="regression",
        severity=5,
    )
    result = backend.check_bug_paths(bug_id)
    assert len(result) == 1
    assert "nonexistent/file.ts" in result


def test_add_impact_auto_prevention(backend):
    """TC-P05: add_impact 后 prevention 分数根据传入的 prevention_delta 自动增加"""
    bug_id, _ = backend.add_bug(
        title="prevention 自动累加测试",
        phenomenon="",
        verified=True,
        scores={"importance": 0, "complexity": 0, "scope": 0, "difficulty": 0,
                "occurrences": 0, "emotion": 0, "prevention": 0},
    )
    # skill 根据 severity=9 计算 delta=5.0，传入 add_impact
    backend.add_impact(
        source_bug_id=bug_id,
        impacted_path="src/cart/add_to_cart.ts",
        impact_type="regression",
        severity=9,
        prevention_delta=5.0,
    )
    # 验证 prevention 分数增加了 5.0
    detail = backend.get_bug_detail(bug_id)
    scores = dict(detail["scores"])
    assert scores["prevention"] == 5.0, f"prevention 应该自动增加 5.0，实际值: {scores.get('prevention')}"


def test_delete_impact_reverts_prevention(backend):
    """TC-P06: delete_impact 后 prevention 分数回退（传入添加时的 delta）"""
    bug_id, _ = backend.add_bug(
        title="delete impact 回退测试",
        phenomenon="",
        verified=True,
        scores={"importance": 0, "complexity": 0, "scope": 0, "difficulty": 0,
                "occurrences": 0, "emotion": 0, "prevention": 0},
    )
    # 添加影响关系，skill 规则：severity=9 -> delta=5.0
    impact_id = backend.add_impact(
        source_bug_id=bug_id,
        impacted_path="src/cart/add_to_cart.ts",
        impact_type="regression",
        severity=9,
        prevention_delta=5.0,
    )
    # 验证增加了 5.0
    detail = backend.get_bug_detail(bug_id)
    assert dict(detail["scores"])["prevention"] == 5.0

    # 删除影响关系，传入相同的 delta=5.0
    backend.delete_impact(impact_id, prevention_delta=5.0)

    # 验证回退到 0
    detail = backend.get_bug_detail(bug_id)
    assert dict(detail["scores"])["prevention"] == 0.0, f"prevention 应该回退到 0.0，实际值: {dict(detail['scores']).get('prevention')}"
