---
name: Bug Organize
description: 当需要整理错题集时触发。触发条件：用户要求整理错题集、清理失效条目、归类重复问题、按重要性重排、用户要求查看整理建议。
---

# Bug Organize Skill

整理 bug-book 数据库中的错题记录，保持错题集的健康度和可用性。

## 常量定义

以下是 bug-book 中使用的关键阈值常量：

```python
THRESHOLD_HIGH_SCORE = 30       # 高分阈值（需明确确认）
THRESHOLD_AUTO_VERIFY = 20      # 预估分阈值（>=此值需审核）
THRESHOLD_OLD_BUGS_DAYS = 30     # 未验证提醒天数
```

## 何时需要整理

- 用户明确要求整理错题集
- 手动整理周期到了（建议每周一次）
- 用户要求"清理失效条目"
- 用户要求"归类相似问题"

## 整理流程

### 1. 加载数据

使用 `scripts/bug_ops.py` 加载所有记录：

```python
from scripts.bug_ops import list_bugs, get_bug_detail, mark_invalid, delete_bug, list_unverified_old

bugs = list_bugs(status="active", order_by="score", limit=100)
unverified_old = list_unverified_old(days=30)
```

### 2. 检查长期未验证记录

对超过 30 天（`THRESHOLD_OLD_BUGS_DAYS`）未验证的活跃记录，提示用户：

```
## 未验证记录提醒

Bug #N 已记录 45 天仍未验证：
- 标题：session 存储未设置持久化
- 创建时间：YYYY-MM-DD

建议：确认是否已修复？如已修复请验证，如功能已废弃请标记失效。
```

### 3. 检查路径有效性

对每条活跃 bug，检查 `autoRecall` 中的路径是否仍然存在于代码库中：

```python
from scripts.bug_ops import check_path_valid

def check_bug_paths(bug_id):
    """检查 bug 的所有路径是否有效"""
    from scripts.bug_ops import get_conn_ctx, get_bug_detail
    with get_conn_ctx() as conn:
        detail = get_bug_detail(bug_id)
        if not detail:
            return []
        invalid_paths = []
        for path in detail.get("paths", []) + detail.get("recalls", []):
            if not check_path_valid(path):
                invalid_paths.append(path)
        return invalid_paths
```

**路径失效的处理**：
1. 标记该 bug 为"待确认失效"
2. 向用户展示：`Bug #N 的相关路径 [path] 已不存在，是否标记为失效？`

### 4. 归类相似问题

检查是否存在根因相同或现象相似的 bug：

```python
from scripts.bug_ops import get_conn, list_bugs

conn = get_conn()
bugs = list_bugs(status="active", order_by="score", limit=100)

bugs_by_tag = {}
for bug in bugs:
    tags = [r[0] for r in conn.execute(
        "SELECT tag FROM bug_tags WHERE bug_id = ?", (bug["id"],)
    ).fetchall()]
    for tag in tags:
        bugs_by_tag.setdefault(tag, []).append(bug)
conn.close()
```

**合并建议格式**：

```
## 相似问题归类建议

Bug #3 和 Bug #7 可能相关：
- #3: "登录页样式错位"
- #7: "样式问题导致布局崩溃"
根因相似度：高（都涉及 CSS 样式覆盖）

建议：合并为一条记录，保留更高分的作为主记录
```

### 5. 按重要性排序

分数计算公式（参考 bug_ops.py 中的 DEFAULT_WEIGHTS）：

```python
DEFAULT_WEIGHTS = {
    "importance": 2.0,
    "complexity": 1.5,
    "scope": 1.0,
    "difficulty": 1.0,
    "occurrences": 1.0,
    "emotion": 1.5,
    "prevention": 2.0,
}

总分 = importance×2.0 + complexity×1.5 + scope×1.0 + difficulty×1.0
     + occurrences×1.0 + emotion×1.5 + prevention×2.0
```

展示排序结果，标记分数异常高/低的条目供用户参考。

### 6. 执行清理操作

根据整理结果，执行以下操作（需用户确认）：

- **标记失效**：`mark_invalid(bug_id, reason)` — 功能/代码已移除
- **合并重复**：`delete_bug(id)` — 删除冗余记录
- **更新分数**：`increment_score(bug_id, dimension, delta)` — 累加出现次数等维度

### 7. 生成整理报告

```
## 错题集整理报告

统计：
- 总记录数：N
- 活跃记录：M
- 已失效：K

未验证记录：
- 超过 30 天未验证：N 条（详见上方）

路径检查：
- 失效风险：N 条（路径已不存在）
- 有效记录：M 条

归类建议：
- 相似问题：N 组（详见上方）
- 可合并：M 条

排序 TOP 10：
1. #3 - session 存储未设置持久化 - 分数 42.5
2. #7 - 按钮样式错位 - 分数 18.0
...

待确认操作：
- [ ] 标记 #N 为失效（路径已不存在）
- [ ] 合并 #3 和 #7
- [ ] 验证 #5（长期未验证）

是否执行以上操作？
```

## 注意事项

- 每次整理最多处理 50 条记录，避免单次操作过多
- 标记失效前必须向用户确认
- 合并记录前必须向用户确认
- 整理后提示用户关键变更
