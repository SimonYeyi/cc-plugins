---
name: Bug Organize
description: 当需要整理错题集时触发。触发条件：用户要求整理错题集、清理失效条目、归类重复问题、按重要性重排、用户要求查看整理建议。
---

# Bug Organize Skill

整理 bug-book 数据库中的错题记录，保持错题集的健康度和可用性。

## Python 脚本执行规则

**【强制要求】禁止 cd 到插件目录！必须在当前项目目录执行 Python 代码。**

- ✅ 正确：保持在项目目录（如 `/home/user/my-project`）执行
- ❌ 错误：cd 到插件目录（如 `~/.claude/plugins/bug-book/scripts`）

如果需要使用插件脚本，使用绝对路径导入：
```python
import sys
sys.path.insert(0, "{CLAUDE_PLUGIN_DIR}/bug-book")
from scripts.bug_ops import list_bugs, get_bug_detail, mark_invalid, delete_bug, list_unverified_old, analyze_impact_patterns
```

## 常量定义

以下是 bug-book 中使用的关键阈值常量：

```python
THRESHOLD_HIGH_SCORE = 30       # 高分阈值（需明确确认）
THRESHOLD_AUTO_VERIFY = 30      # 自动验证阈值（<此值可自动验证，>=此值需审核）
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
from scripts.bug_ops import list_bugs, get_bug_detail

# 获取所有活跃 bugs
bugs = list_bugs(status="active", order_by="score", limit=100)

# 按标签分组
bugs_by_tag = {}
for bug in bugs:
    detail = get_bug_detail(bug["id"])
    if detail and "tags" in detail:
        for tag in detail["tags"]:
            bugs_by_tag.setdefault(tag, []).append(bug)
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

### 5.5. 分析影响模式（新功能）

**调用 `analyze_impact_patterns()` 分析高频回归模块：**

```python
from scripts.bug_ops import analyze_impact_patterns

# 获取受影响最频繁的 Top 10 模块
patterns = analyze_impact_patterns(limit=10)
```

**返回示例：**
```python
[
    {
        "path": "src/cart/",
        "impact_count": 5,           # 被影响了 5 次
        "avg_severity": 7.2,         # 平均严重度 7.2
        "max_severity": 9,           # 最高严重度 9
    },
    {
        "path": "src/auth/",
        "impact_count": 3,
        "avg_severity": 8.0,
        "max_severity": 9,
    }
]
```

**在整理报告中添加影响分析章节：**

```markdown
### 📊 影响分析报告

#### 高风险模块 Top 5
1. **src/cart/** - 被影响 5 次，平均严重度 7.2
   - Bug #42 → cart/add_to_cart.ts (回归，严重度 8)
   - Bug #38 → cart/checkout.ts (副作用，严重度 7)
   - ...

2. **src/auth/** - 被影响 3 次，平均严重度 8.0
   - Bug #45 → auth/middleware.ts (回归，严重度 9)
   - ...

#### 💡 洞察与建议
- **auth 和 cart 模块耦合度高**，修改其中一个容易影响另一个
- 建议在 auth/cart 之间增加接口层，降低直接依赖
- 可以考虑为这两个模块编写集成测试
```

### 6. 执行清理操作

根据整理结果，执行以下操作（需用户确认）：

- **标记失效**：`mark_invalid(bug_id, reason)` — 功能/代码已移除
- **合并重复**：`delete_bug(id)` — 删除冗余记录
- **更新分数**：`increment_score(bug_id, dimension, delta)` — 累加出现次数等维度
- **验证 bug**：`update_bug(bug_id, verified=True, verified_at="CURRENT_TIMESTAMP", verified_by="User")`

**重要：整理完成后，必须记录整理时间！**

```python
from scripts.bug_ops import set_last_organize_time

# 在所有整理操作执行完毕后
set_last_organize_time()
print("✅ 整理完成！已更新最后整理时间。")
```

**用户确认后的执行示例：**

```python
from scripts.bug_ops import mark_invalid, delete_bug, update_bug, increment_score

# 假设用户确认执行以下操作：
# 1. 标记 #5 为失效
# 2. 合并 #3 和 #7（删除 #7）
# 3. 验证 #8

# 执行操作 1：标记失效
mark_invalid(5, reason="路径 src/old/auth.ts 已不存在")

# 执行操作 2：合并重复（删除低分的 #7）
delete_bug(7)

# 执行操作 3：验证长期未验证的 bug
update_bug(8, verified=True, verified_at="CURRENT_TIMESTAMP", verified_by="User")

# 可选：累加出现次数
increment_score(3, "occurrences", 1.0)

print("✅ 整理完成！共执行 4 项操作")
```

**执行后提示：**

```
## 整理完成

已执行以下操作：
- ✅ 标记 Bug #5 为失效
- ✅ 删除 Bug #7（与 #3 合并）
- ✅ 验证 Bug #8
- ✅ 累加 Bug #3 出现次数
- ✅ **记录最后整理时间**

当前状态：
- 总记录数：14（减少 1 条）
- 活跃记录：11
- 已失效：4（增加 1 条）
- 已验证：8（增加 1 条）
```

### 7. 生成整理报告

```
## 错题集整理报告

### 统计
- 总记录数：15
- 活跃记录：12
- 已失效：3

### 未验证记录（超过 30 天）
1. Bug #5 - session 存储未设置持久化 - 创建于 2024-01-15（45 天前）
2. Bug #8 - 按钮点击无响应 - 创建于 2024-01-20（40 天前）

### 路径检查结果
**失效路径：**
- Bug #3: `src/old/auth.ts` 已不存在
- Bug #7: `components/LegacyButton.vue` 已不存在

**有效记录：** 10 条

### 相似问题归类
**可能重复的 bugs：**
- Bug #3 和 Bug #7：都涉及 CSS 样式问题，标签重叠（auth, session）
  - #3: "登录页样式错位" - 分数 42.5
  - #7: "样式问题导致布局崩溃" - 分数 18.0
  - 建议：保留 #3，删除 #7

### 排序 TOP 10
1. #3 - session 存储未设置持久化 - 分数 42.5 ⏳未验证
2. #12 - 数据库连接池泄漏 - 分数 35.0 ✅已验证
3. #1 - 用户权限校验失败 - 分数 28.5 ✅已验证
4. #7 - 按钮样式错位 - 分数 18.0 ✅已验证
5. #8 - 按钮点击无响应 - 分数 15.0 ⏳未验证
...

### 待确认操作
请确认是否执行以下操作：

- [ ] **标记失效**：Bug #3（路径 src/old/auth.ts 已不存在）
- [ ] **标记失效**：Bug #7（路径 components/LegacyButton.vue 已不存在）
- [ ] **合并重复**：Bug #3 和 #7 → 保留 #3，删除 #7
- [ ] **验证**：Bug #5（已 45 天未验证，确认是否已修复？）
- [ ] **验证**：Bug #8（已 40 天未验证，确认是否已修复？）

**回复示例：**
- “全部执行” → 执行所有操作
- “只执行第 1 和第 4 项” → 选择性执行
- “我看一下 #3 和 #7 的详情” → 展开详细信息
- “#5 其实已经修复了” → 只验证 #5，跳过其他
```

**如果用户需要更多信息才能决定：**

当用户对某项操作有疑问时，AI 应该主动提供详细信息：

```python
# 用户问：“#3 和 #7 为什么可以合并？”
from scripts.bug_ops import get_bug_detail

detail_3 = get_bug_detail(3)
detail_7 = get_bug_detail(7)

print(f"""
## Bug #3 详情
- 标题：{detail_3['title']}
- 现象：{detail_3['phenomenon']}
- 根因：{detail_3.get('root_cause', 'N/A')}
- 解决方案：{detail_3.get('solution', 'N/A')}
- 标签：{', '.join(detail_3.get('tags', []))}
- 分数：{detail_3['score']}

## Bug #7 详情
- 标题：{detail_7['title']}
- 现象：{detail_7['phenomenon']}
- 根因：{detail_7.get('root_cause', 'N/A')}
- 解决方案：{detail_7.get('solution', 'N/A')}
- 标签：{', '.join(detail_7.get('tags', []))}
- 分数：{detail_7['score']}

## 相似性分析
- 共同标签：auth, session
- 根因相似度：高（都涉及 CSS 样式覆盖）
- 建议：保留分数更高的 #3，删除 #7
""")
```

**用户可能的反馈及处理：**
- “我看一下 #3 的详情” → 调用 `get_bug_detail(3)` 展示完整信息
- “#5 其实已经修复了” → 执行 `update_bug(5, verified=True, ...)`
- “#3 和 #7 不能合并，它们不一样” → 跳过该项操作
- “全部执行” → 执行所有待确认操作
- “只执行第 1 和第 3 项” → 选择性执行

## 注意事项

- 每次整理最多处理 50 条记录，避免单次操作过多
- 标记失效前必须向用户确认
- 合并记录前必须向用户确认
- 整理后提示用户关键变更
