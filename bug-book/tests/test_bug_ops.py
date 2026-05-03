#!/usr/bin/env python3
"""bug-book 数据库操作测试"""

import os
import sys
import pytest
from pathlib import Path

# 确保 scripts/ 在 Python path 中
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from bug_ops import (
    add_bug,
    update_bug,
    delete_bug,
    increment_score,
    add_path,
    add_recall,
    search_by_keyword,
    recall_by_path,
    recall_by_pattern,
    get_bug_detail,
    list_bugs,
    mark_invalid,
    list_unverified_old,
    _match_path,
    _normalize_path,
    get_conn,
    DB_PATH,
    ValidationError,
    # 影响关系管理
    add_impact,
    get_impacted_bugs,
    get_bug_impacts,
    analyze_impact_patterns,
)

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


def setup_module():
    """测试开始前清理数据库"""
    for f in [
        str(DB_PATH),
        str(DB_PATH) + "-journal",
        str(DB_PATH) + "-wal",
        str(DB_PATH) + "-shm",
    ]:
        try:
            os.remove(f)
        except OSError:
            pass


def teardown_module():
    """测试结束后清理数据库"""
    setup_module()


# ============================================================
# TC-A01 ~ TC-A08：add_bug 新增记录
# ============================================================

def test_add_bug_minimal_fields():
    """TC-A01: 新增最小字段记录"""
    bug_id, score = add_bug(title="测试", phenomenon="现象", verified=True)
    assert bug_id == 1
    assert score == 0
    detail = get_bug_detail(bug_id)
    assert detail["title"] == "测试"
    assert detail["verified"] == 1


def test_add_bug_full_fields():
    """TC-A02: 新增完整字段记录"""
    bug_id, score = add_bug(
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
    detail = get_bug_detail(bug_id)
    assert detail["title"] == "session丢失"
    assert detail["paths"] == ["src/auth/session.ts"]
    assert detail["tags"] == ["auth"]
    assert detail["recalls"] == ["auth/*"]
    assert len(detail["scores"]) == 7


def test_add_bug_chinese():
    """TC-A03: 新增记录含中文"""
    bug_id, _ = add_bug(
        title="中文标题测试",
        phenomenon="中文现象描述",
        root_cause="中文根因分析",
        solution="中文解决方案",
        verified=True,
    )
    detail = get_bug_detail(bug_id)
    assert detail["title"] == "中文标题测试"
    assert "中文" in detail["phenomenon"]


def test_add_bug_verified_false():
    """TC-A04: 新增 verified=False（复杂问题）"""
    bug_id, _ = add_bug(title="复杂问题", phenomenon="复杂", verified=False)
    detail = get_bug_detail(bug_id)
    assert detail["verified"] == 0


def test_add_bug_empty_scores():
    """TC-A05: 新增空 scores dict"""
    bug_id, score = add_bug(title="空分数", phenomenon="无分数", scores={})
    assert score == 0


def test_add_bug_multiple_paths():
    """TC-A06: 新增多条 paths"""
    bug_id, _ = add_bug(
        title="多路径",
        phenomenon="",
        paths=["src/a.ts", "src/b.ts"],
    )
    detail = get_bug_detail(bug_id)
    assert len(detail["paths"]) == 2


def test_add_bug_multiple_recalls():
    """TC-A07: 新增多条 recalls"""
    bug_id, _ = add_bug(
        title="多模式",
        phenomenon="",
        recalls=["auth/*", "src/*"],
    )
    detail = get_bug_detail(bug_id)
    assert len(detail["recalls"]) == 2


def test_add_bug_then_get_detail():
    """TC-A08: 新增后立即查询"""
    bug_id, _ = add_bug(title="立即查询", phenomenon="测试")
    detail = get_bug_detail(bug_id)
    assert detail is not None
    assert detail["id"] == bug_id


# ============================================================
# TC-B01 ~ TC-B06：update_bug 更新记录
# ============================================================

def test_update_bug_single_field():
    """TC-B01: 更新单字段"""
    bug_id, _ = add_bug(title="旧标题", phenomenon="", verified=True)
    update_bug(bug_id, title="新标题")
    detail = get_bug_detail(bug_id)
    assert detail["title"] == "新标题"


def test_update_bug_multiple_fields():
    """TC-B02: 同时更新多字段"""
    bug_id, _ = add_bug(title="旧", phenomenon="旧", verified=True)
    update_bug(bug_id, title="新", root_cause="新根因")
    detail = get_bug_detail(bug_id)
    assert detail["title"] == "新"
    assert detail["root_cause"] == "新根因"


def test_update_bug_verified_fields():
    """TC-B03: 更新 verified 相关字段"""
    bug_id, _ = add_bug(title="待验证", phenomenon="", verified=False)
    update_bug(
        bug_id,
        verified=True,
        verified_at="CURRENT_TIMESTAMP",
        verified_by="User",
        status="resolved",
    )
    detail = get_bug_detail(bug_id)
    assert detail["verified"] == 1
    assert detail["verified_by"] == "User"
    assert detail["status"] == "resolved"


def test_update_bug_status():
    """TC-B04: 更新 status 为 resolved"""
    bug_id, _ = add_bug(title="待解决", phenomenon="", verified=True)
    update_bug(bug_id, status="resolved")
    detail = get_bug_detail(bug_id)
    assert detail["status"] == "resolved"


def test_update_bug_nonexistent():
    """TC-B05: 更新不存在的 bug_id"""
    update_bug(9999, title="不存在")


def test_update_bug_no_fields():
    """TC-B06: 不传任何字段"""
    bug_id, _ = add_bug(title="无更新", phenomenon="", verified=True)
    update_bug(bug_id)


# ============================================================
# TC-C01 ~ TC-C03：delete_bug 删除记录
# ============================================================

def test_delete_bug_exists():
    """TC-C01: 删除存在的记录"""
    bug_id, _ = add_bug(title="待删除", phenomenon="", verified=True)
    delete_bug(bug_id)
    assert get_bug_detail(bug_id) is None


def test_delete_bug_nonexistent():
    """TC-C02: 删除不存在的 id"""
    delete_bug(9999)


def test_delete_bug_cascade():
    """TC-C03: 删除后关联数据也被删除"""
    bug_id, _ = add_bug(
        title="级联删除",
        phenomenon="",
        verified=True,
        paths=["a.ts"],
        tags=["t"],
        keywords=["k"],
        recalls=["p/*"],
    )
    delete_bug(bug_id)
    assert get_bug_detail(bug_id) is None
    conn = get_conn()
    assert conn.execute("SELECT COUNT(*) FROM bug_scores WHERE bug_id=?", (bug_id,)).fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM bug_paths WHERE bug_id=?", (bug_id,)).fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM bug_tags WHERE bug_id=?", (bug_id,)).fetchone()[0] == 0
    # 无报错即通过


# ============================================================
# TC-D01 ~ TC-D03：increment_score 分数累加
# ============================================================

def test_increment_score_existing():
    """TC-D01: 累加已存在的维度"""
    bug_id, _ = add_bug(title="累加", phenomenon="", verified=True, scores=DEFAULT_SCORES)
    increment_score(bug_id, "occurrences", 1.0)
    detail = get_bug_detail(bug_id)
    scores = dict(detail["scores"])
    assert scores["occurrences"] == 1.0


def test_increment_score_new_dimension():
    """TC-D02: 累加不存在的维度"""
    bug_id, _ = add_bug(title="新维度", phenomenon="", verified=True)
    increment_score(bug_id, "new_dim", 5.0)
    detail = get_bug_detail(bug_id)
    scores = dict(detail["scores"])
    assert scores["new_dim"] == 5.0


def test_increment_score_multiple():
    """TC-D03: 连续累加 3 次"""
    bug_id, _ = add_bug(title="多次", phenomenon="", verified=True)
    increment_score(bug_id, "occurrences", 1.0)
    increment_score(bug_id, "occurrences", 1.0)
    increment_score(bug_id, "occurrences", 1.0)
    detail = get_bug_detail(bug_id)
    scores = dict(detail["scores"])
    assert scores["occurrences"] == 3.0


# ============================================================
# TC-E01 ~ TC-E03: add_path / add_recall
# ============================================================

def test_add_path():
    """TC-E01: 添加路径"""
    bug_id, _ = add_bug(title="加路径", phenomenon="", verified=True)
    add_path(bug_id, "src/auth.ts")
    detail = get_bug_detail(bug_id)
    assert "src/auth.ts" in detail["paths"]


def test_add_path_old():
    """TC-E02: 添加 is_old=True 路径"""
    bug_id, _ = add_bug(title="旧路径", phenomenon="", verified=True)
    add_path(bug_id, "old/Auth.ts", is_old=True)
    detail = get_bug_detail(bug_id)
    assert "old/Auth.ts" in detail["old_paths"]


def test_add_recall():
    """TC-E03: 添加 autoRecall 模式"""
    bug_id, _ = add_bug(title="加模式", phenomenon="", verified=True)
    add_recall(bug_id, "auth/*")
    detail = get_bug_detail(bug_id)
    assert "auth/*" in detail["recalls"]


# ============================================================
# TC-F01 ~ TC-F07：search_by_keyword 关键词搜索
# ============================================================

def test_search_by_title():
    """TC-F01: 搜索匹配 title"""
    add_bug(title="唯一标题ABC123", phenomenon="", verified=True)
    results = search_by_keyword("ABC123")
    assert len(results) >= 1
    assert any(r["title"] == "唯一标题ABC123" for r in results)


def test_search_by_phenomenon():
    """TC-F02: 搜索匹配 phenomenon"""
    add_bug(title="t", phenomenon="p_abc456", verified=True)
    results = search_by_keyword("abc456")
    assert len(results) >= 1
    assert any("abc456" in r["phenomenon"] for r in results)


def test_search_by_tag():
    """TC-F03: 搜索匹配 tag"""
    add_bug(title="t", phenomenon="", tags=["my_tag_xyz"], verified=True)
    results = search_by_keyword("my_tag_xyz")
    assert len(results) >= 1


def test_search_by_keyword_field():
    """TC-F04: 搜索匹配 keyword"""
    add_bug(title="t", phenomenon="", keywords=["kw_test"], verified=True)
    results = search_by_keyword("kw_test")
    assert len(results) >= 1


def test_search_no_result():
    """TC-F05: 搜索无结果"""
    results = search_by_keyword("不存在关键词XYZABC")
    assert len(results) == 0


def test_search_order_by_score():
    """TC-F06: 结果按分数 DESC 排序"""
    add_bug(title="高分", phenomenon="", verified=True, scores={"importance": 10, "complexity": 10, "scope": 10, "difficulty": 10, "occurrences": 0, "emotion": 0, "prevention": 10})
    add_bug(title="低分", phenomenon="", verified=True, scores={"importance": 1, "complexity": 1, "scope": 1, "difficulty": 1, "occurrences": 0, "emotion": 0, "prevention": 1})
    results = search_by_keyword("", limit=10)
    assert results[0]["title"] == "高分"


def test_search_pagination():
    """TC-F07: 分页 limit=2"""
    for i in range(5):
        add_bug(title=f"分页{i}", phenomenon="", verified=True)
    results = search_by_keyword("", limit=2)
    assert len(results) == 2


# ============================================================
# TC-G01 ~ TC-G15：_match_path 路径匹配
# ============================================================

def test_match_single_wildcard():
    """TC-G01: 单段通配符匹配子目录"""
    assert _match_path("src/auth/session.ts", "auth/*") is True


def test_match_single_wildcard_false():
    """TC-G02: 单段通配符不匹配 authority"""
    assert _match_path("src/authority/index.ts", "auth/*") is False


def test_match_multi_prefix():
    """TC-G03: 多段前缀匹配子路径"""
    assert _match_path("src/auth/login.ts", "src/auth/*") is True


def test_match_multi_prefix_false():
    """TC-G04: 多段前缀不匹配"""
    assert _match_path("src/api/user.ts", "src/auth/*") is False


def test_match_single_exact():
    """TC-G05: 单段精确任意位置"""
    assert _match_path("src/auth/file.ts", "auth") is True


def test_match_single_exact_false():
    """TC-G06: 单段精确不匹配"""
    assert _match_path("authz/login.ts", "auth") is False


def test_match_multi_exact_prefix():
    """TC-G07: 多段精确前缀"""
    assert _match_path("src/auth/file.ts", "src/auth") is True


def test_match_exact_file():
    """TC-G08: 精确匹配文件"""
    assert _match_path("src/auth/session.ts", "src/auth/session.ts") is True


def test_match_windows_path():
    """TC-G09: Windows 路径兼容"""
    assert _match_path("src\\auth\\session.ts", "auth/*") is True


def test_match_dir_not_match_wildcard():
    """TC-G10: 目录不匹配通配符"""
    assert _match_path("src/auth", "src/auth/*") is False


def test_match_path_too_long():
    """TC-G11: 路径长度不足"""
    assert _match_path("a/b", "a/b/c/d") is False


def test_match_makefile():
    """TC-G12: 根目录文件不匹配"""
    assert _match_path("Makefile", "auth/*") is False


def test_match_trailing_slash():
    """TC-G13: 末尾斜杠去除"""
    assert _match_path("src/auth/", "src/auth") is True


def test_match_empty_path():
    """TC-G14: 空文件路径"""
    assert _match_path("", "auth/*") is False


def test_match_single_to_single():
    """TC-G15: 单段路径匹配单段模式"""
    assert _match_path("auth/login.ts", "auth") is True


# ============================================================
# TC-H01 ~ TC-H07：recall_by_path / recall_by_pattern 路径召回
# ============================================================

def test_recall_by_exact_path():
    """TC-H01: 按文件精确路径召回"""
    bug_id, _ = add_bug(title="精确召回", phenomenon="", verified=True, paths=["src/auth/session.ts"])
    results = recall_by_path("src/auth/session.ts")
    assert any(r["id"] == bug_id for r in results)


def test_recall_multi_path():
    """TC-H02: 按目录前缀召回"""
    bug_id, _ = add_bug(
        title="auth问题",
        phenomenon="",
        verified=True,
        paths=["src/auth/session.ts"],
        recalls=["auth/*"],
    )
    results = recall_by_path("src/auth/login.ts")
    assert any(r["id"] == bug_id for r in results)


def test_recall_unrelated_path():
    """TC-H03: 不相关路径不召回"""
    add_bug(title="api问题", phenomenon="", verified=True, paths=["src/api/user.ts"])
    results = recall_by_path("src/auth/login.ts")
    assert not any(r["title"] == "api问题" for r in results)


def test_recall_by_recalls_only():
    """TC-H04: 只有 recalls 无 paths"""
    bug_id, _ = add_bug(
        title="仅recall",
        phenomenon="",
        verified=True,
        paths=[],
        recalls=["auth/*"],
    )
    results = recall_by_path("src/auth/login.ts")
    assert any(r["id"] == bug_id for r in results)


def test_recall_order_by_score():
    """TC-H05: 结果按分数排序"""
    add_bug(title="低分bug", phenomenon="", verified=True, scores={"importance": 1, "complexity": 1, "scope": 1, "difficulty": 1, "occurrences": 0, "emotion": 0, "prevention": 1}, paths=["src/x.ts"], recalls=["x/*"])
    add_bug(title="高分bug", phenomenon="", verified=True, scores={"importance": 10, "complexity": 10, "scope": 10, "difficulty": 10, "occurrences": 0, "emotion": 0, "prevention": 10}, paths=["src/x.ts"], recalls=["x/*"])
    results = recall_by_path("src/x/file.ts")
    assert results[0]["title"] == "高分bug"


def test_recall_by_pattern():
    """TC-H06: recall_by_pattern 模式匹配"""
    bug_id, _ = add_bug(
        title="auth模式",
        phenomenon="",
        verified=True,
        recalls=["auth/*"],
    )
    results = recall_by_pattern("auth")
    assert any(r["id"] == bug_id for r in results)


def test_recall_by_pattern_no_match():
    """TC-H07: recall_by_pattern 无匹配"""
    add_bug(title="nomatch", phenomenon="", verified=True, recalls=["xyz/*"])
    results = recall_by_pattern("auth")
    assert not any(r["title"] == "nomatch" for r in results)


# ============================================================
# TC-I01 ~ TC-I05: get_bug_detail
# ============================================================

def test_get_detail_exists():
    """TC-I01: 查询存在的 bug"""
    bug_id, _ = add_bug(title="详情", phenomenon="", verified=True)
    detail = get_bug_detail(bug_id)
    assert detail is not None
    assert detail["id"] == bug_id
    assert detail["title"] == "详情"


def test_get_detail_nonexistent():
    """TC-I02: 查询不存在的 bug"""
    assert get_bug_detail(9999) is None


def test_get_detail_scores():
    """TC-I03: 详情包含 7 维度分数"""
    bug_id, _ = add_bug(title="scores", phenomenon="", verified=True, scores=DEFAULT_SCORES)
    detail = get_bug_detail(bug_id)
    assert len(detail["scores"]) == 7


def test_get_detail_paths_separation():
    """TC-I04: 详情包含 paths 和 old_paths"""
    bug_id, _ = add_bug(title="分离", phenomenon="", verified=True, paths=["src/a.ts"])
    add_path(bug_id, "old/b.ts", is_old=True)
    detail = get_bug_detail(bug_id)
    assert "src/a.ts" in detail["paths"]
    assert "old/b.ts" in detail["old_paths"]


def test_get_detail_relations():
    """TC-I05: 详情包含 tags/keywords/recalls"""
    bug_id, _ = add_bug(
        title="关联",
        phenomenon="",
        verified=True,
        tags=["t1", "t2"],
        keywords=["k1"],
        recalls=["r1/*"],
    )
    detail = get_bug_detail(bug_id)
    assert len(detail["tags"]) == 2
    assert detail["keywords"] == ["k1"]
    assert detail["recalls"] == ["r1/*"]


# ============================================================
# TC-J01 ~ TC-J04: list_bugs
# ============================================================

def test_list_bugs_by_status():
    """TC-J01: 按 status=active 过滤"""
    mark_invalid(1)
    results = list_bugs(status="active")
    assert all(r["status"] == "active" for r in results)


def test_list_bugs_order_by_whitelist():
    """TC-J02: order_by=score（白名单）校验"""
    results = list_bugs(order_by="score")
    assert isinstance(results, list)


def test_list_bugs_order_by_invalid():
    """TC-J03: order_by=invalid_col（非白名单）自动降级"""
    results = list_bugs(order_by="invalid_column")
    # 不应报错，自动降级为 score
    assert isinstance(results, list)


def test_list_bugs_pagination():
    """TC-J04: 分页 limit=2 offset=1"""
    results = list_bugs(limit=2, offset=0)
    assert len(results) <= 2


# ============================================================
# TC-K01 ~ TC-K03: mark_invalid
# ============================================================

def test_mark_invalid_with_reason():
    """TC-K01: 标记失效带原因"""
    bug_id, _ = add_bug(title="待失效", phenomenon="", verified=True)
    mark_invalid(bug_id, "功能已删除")
    detail = get_bug_detail(bug_id)
    assert detail["status"] == "invalid"
    assert "功能已删除" in detail["solution"]


def test_mark_invalid_without_reason():
    """TC-K02: 标记失效不带原因"""
    bug_id, _ = add_bug(title="无原因失效", phenomenon="", verified=True)
    mark_invalid(bug_id)
    detail = get_bug_detail(bug_id)
    assert detail["status"] == "invalid"


def test_mark_invalid_nonexistent():
    """TC-K03: 标记不存在的 bug"""
    mark_invalid(9999)  # 不应报错


# ============================================================
# TC-L01 ~ TC-L03: 懒初始化与集成
# ============================================================

def test_lazy_init():
    """TC-L01: 数据库不存在时自动创建"""
    for f in [str(DB_PATH), str(DB_PATH) + "-journal", str(DB_PATH) + "-wal", str(DB_PATH) + "-shm"]:
        try:
            os.remove(f)
        except OSError:
            pass
    add_bug(title="懒初始化", phenomenon="", verified=True)
    assert DB_PATH.exists()


def test_full_crud():
    """TC-L02: 完整 CRUD 流程"""
    bug_id, _ = add_bug(title="CRUD", phenomenon="创建", verified=True)
    update_bug(bug_id, phenomenon="更新")
    detail = get_bug_detail(bug_id)
    assert detail["phenomenon"] == "更新"
    delete_bug(bug_id)
    assert get_bug_detail(bug_id) is None


def test_recurrence_flow():
    """TC-L03: 复发处理流程"""
    bug_id, _ = add_bug(
        title="复发测试",
        phenomenon="",
        verified=True,
        scores=DEFAULT_SCORES,
    )
    # 模拟复发：打回未验证 + 累加分数
    update_bug(bug_id, verified=False)
    increment_score(bug_id, "occurrences", 1.0)
    detail = get_bug_detail(bug_id)
    assert detail["verified"] == 0
    scores = dict(detail["scores"])
    assert scores["occurrences"] == 1.0


# ============================================================
# TC-M01 ~ TC-M08: 影响关系管理
# ============================================================

def test_add_impact_regression():
    """TC-M01: 添加回归影响"""
    bug_id, _ = add_bug(title="源bug", phenomenon="", verified=True)
    impact_id = add_impact(
        source_bug_id=bug_id,
        impacted_path="src/cart/add_to_cart.ts",
        impact_type="regression",
        description="修改 session 导致购物车失效",
        severity=8,
    )
    assert impact_id > 0
    impacts = get_bug_impacts(bug_id)
    assert len(impacts) == 1
    assert impacts[0]["impact_type"] == "regression"
    assert impacts[0]["severity"] == 8


def test_add_impact_side_effect():
    """TC-M02: 添加副作用影响"""
    bug_id, _ = add_bug(title="源bug2", phenomenon="", verified=True)
    impact_id = add_impact(
        source_bug_id=bug_id,
        impacted_path="src/user/profile.ts",
        impact_type="side_effect",
        severity=5,
    )
    assert impact_id > 0
    impacts = get_bug_impacts(bug_id)
    assert impacts[0]["impact_type"] == "side_effect"


def test_add_impact_dependency():
    """TC-M03: 添加依赖影响"""
    bug_id, _ = add_bug(title="源bug3", phenomenon="", verified=True)
    impact_id = add_impact(
        source_bug_id=bug_id,
        impacted_path="src/api/client.ts",
        impact_type="dependency",
        severity=3,
    )
    assert impact_id > 0
    impacts = get_bug_impacts(bug_id)
    assert impacts[0]["impact_type"] == "dependency"


def test_add_impact_invalid_type():
    """TC-M04: 添加无效影响类型"""
    bug_id, _ = add_bug(title="源bug4", phenomenon="", verified=True)
    try:
        add_impact(
            source_bug_id=bug_id,
            impacted_path="src/test.ts",
            impact_type="invalid",
        )
        assert False, "应该抛出 ValidationError"
    except ValidationError:
        pass  # 预期行为


def test_add_impact_invalid_severity():
    """TC-M05: 添加无效的严重程度"""
    bug_id, _ = add_bug(title="源bug5", phenomenon="", verified=True)
    try:
        add_impact(
            source_bug_id=bug_id,
            impacted_path="src/test.ts",
            impact_type="regression",
            severity=15,  # 超出范围
        )
        assert False, "应该抛出 ValidationError"
    except ValidationError:
        pass  # 预期行为


def test_get_impacted_bugs():
    """TC-M06: 查询会影响指定文件的 bug"""
    bug_id, _ = add_bug(title="影响测试", phenomenon="", verified=True)
    add_impact(
        source_bug_id=bug_id,
        impacted_path="src/cart/add_to_cart.ts",
        impact_type="regression",
        description="测试描述",
        severity=8,
    )
    
    impacted = get_impacted_bugs("src/cart/add_to_cart.ts")
    assert len(impacted) >= 1
    # 检查返回的数据包含影响信息
    found = False
    for item in impacted:
        if item["id"] == bug_id:
            found = True
            assert item["impact_type"] == "regression"
            assert item["severity"] == 8
            assert item["description"] == "测试描述"
            break
    assert found


def test_get_bug_impacts():
    """TC-M07: 查询某个 bug 的所有影响"""
    bug_id, _ = add_bug(title="多影响测试", phenomenon="", verified=True)
    add_impact(source_bug_id=bug_id, impacted_path="src/a.ts", severity=8)
    add_impact(source_bug_id=bug_id, impacted_path="src/b.ts", severity=5)
    add_impact(source_bug_id=bug_id, impacted_path="src/c.ts", severity=3)
    
    impacts = get_bug_impacts(bug_id)
    assert len(impacts) == 3
    # 按 severity DESC 排序
    assert impacts[0]["severity"] >= impacts[1]["severity"]
    assert impacts[1]["severity"] >= impacts[2]["severity"]


def test_analyze_impact_patterns():
    """TC-M08: 分析高频回归模式"""
    # 创建多个影响记录，集中在某些路径
    bug_id1, _ = add_bug(title="bug1", phenomenon="", verified=True)
    bug_id2, _ = add_bug(title="bug2", phenomenon="", verified=True)
    
    add_impact(source_bug_id=bug_id1, impacted_path="src/cart/", severity=8)
    add_impact(source_bug_id=bug_id2, impacted_path="src/cart/", severity=7)
    add_impact(source_bug_id=bug_id1, impacted_path="src/auth/", severity=9)
    
    patterns = analyze_impact_patterns()
    assert len(patterns) >= 2
    # src/cart/ 应该有 2 次影响
    cart_pattern = next((p for p in patterns if p["path"] == "src/cart/"), None)
    assert cart_pattern is not None
    assert cart_pattern["impact_count"] == 2
