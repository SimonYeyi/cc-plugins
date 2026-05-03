---
name: bug-search
description: 当需要搜索和召回历史 Bug 记录。核心触发场景：1. 用户主动搜索 Bug；2. **AI 准备修改代码前，必须调用此技能进行路径召回（recall_by_path）以检查历史报错**；3. 查询特定模块的已知缺陷。
---

# Bug Search Skill

搜索 bug-book 数据库，快速找到相关的 bug 记录。

## Python 脚本执行规则

**【强制要求】禁止 cd 到插件目录！必须在当前项目目录执行 Python 代码。**

- ✅ 正确：保持在项目目录（如 `/home/user/my-project`）执行
- ❌ 错误：cd 到插件目录（如 `~/.claude/plugins/bug-book/scripts`）

如果需要使用插件脚本，使用绝对路径导入：
```python
import sys
sys.path.insert(0, "{CLAUDE_PLUGIN_DIR}/bug-book")
from scripts.bug_ops import search_by_keyword, recall_by_path, get_impacted_bugs
```

## 搜索场景

- 用户问"有没有 XX 相关的 bug"
- 改代码前查询相关历史问题
- 按文件/模块查找 bug
- 按标签/关键词查找

## 搜索流程

### 1. 关键词搜索

使用 `scripts/bug_ops.py` 的 `search_by_keyword()`：

```python
from scripts.bug_ops import search_by_keyword

results = search_by_keyword("session", limit=20)
```

### 2. 按路径召回

当 AI 即将修改某个文件时，自动查询该文件相关的历史 bugs：

#### 2.1 按具体文件路径召回

```python
from scripts.bug_ops import recall_by_path

# 查询 src/auth/login.ts 相关的 bugs
results = recall_by_path("src/auth/login.ts", limit=10)
```

**匹配规则：**
- 精确匹配：`src/auth/login.ts` → 匹配记录中 paths 包含该文件的 bugs
- 模式匹配：`src/auth/*` → 匹配 autoRecall 中包含 `auth/*` 的 bugs

#### 2.2 按影响关系召回

当 AI 即将修改某个文件时，查询哪些历史 bug 的修复曾影响过该文件：

```python
from scripts.bug_ops import get_impacted_bugs

# 查询哪些 bug 的修复会影响 src/cart/checkout.ts
impacted = get_impacted_bugs("src/cart/checkout.ts", limit=10)
```

**返回示例：**
```python
[
    {
        "id": 42,
        "title": "session 过期页面空白",
        "phenomenon": "登录30分钟后刷新页面显示空白",
        "score": 56.5,
        "status": "resolved",
        "impacted_path": "src/cart/add_to_cart.ts",
        "impact_type": "regression",
        "description": "修改 session 持久化导致购物车的用户状态判断失效",
        "severity": 8,
    }
]
```

**使用场景：**
- AI 准备修改 cart 模块，想知道之前有哪些 bug 的修复影响过这个模块
- 用户说“小心别又搞坏了购物车”，AI 查询影响关系给出警告

**展示格式：**
```markdown
🔴 **影响链警告**

以下 bug 的修复曾影响过你即将修改的文件：

- **Bug #42**: session 过期页面空白 (score: 56.5) ✅ 已验证
  - ⚠️ 该 bug 的修复曾导致购物车模块出现问题！
  - 影响路径：src/cart/add_to_cart.ts
  - 影响类型：回归问题（严重度 8/10）
  - 描述：修改 session 持久化导致购物车的用户状态判断失效

💡 **建议**：修改时务必检查与 auth/session 的交互逻辑
```

#### 2.3 按 autoRecall 模式召回

```python
from scripts.bug_ops import recall_by_pattern

# 查询所有 autoRecall 包含 "session" 的 bugs
results = recall_by_pattern("session", limit=10)
```

**匹配规则：**
- 只匹配 bug_recalls 表中的 pattern 字段
- 支持 glob 模式：`auth/*`, `*.ts`, `src/**/*`

**使用场景：**
- 用户说：“帮我找找所有和 session 相关的 bugs”
- AI 准备修改 auth 模块，想看看有哪些 autoRecall 模式匹配的 bugs

### 3. 列表浏览

当用户想查看所有 bugs 或按条件筛选时：

```python
from scripts.bug_ops import list_bugs

# 获取所有活跃 bugs（按分数排序）
bugs = list_bugs(status="active", order_by="score", limit=50)

# 获取所有状态的 bugs
all_bugs = list_bugs(status=None, order_by="created_at", limit=100)

# 获取已失效的 bugs
invalid_bugs = list_bugs(status="invalid", order_by="score", limit=20)

# 分页查询
page2_bugs = list_bugs(status="active", order_by="score", limit=20, offset=20)
```

**展示格式：**

```
## Bugs 列表（共 N 条）

| ID | 标题 | 分数 | 状态 | 创建时间 |
|----|------|------|------|----------|
| #3 | session 存储未设置持久化 | 42.5 | ⏳ | 2024-01-15 |
| #12 | 数据库连接池泄漏 | 35.0 | ✅ | 2024-02-01 |
| #1 | 用户权限校验失败 | 28.5 | ✅ | 2024-01-10 |
...

> 提示：输入“查看 #3 详情”可展开完整信息
```

### 4. 高级搜索

#### 5.1 按标签搜索

```python
from scripts.bug_ops import search_by_tag

# 搜索包含 "auth" 标签的 bugs
results = search_by_tag("auth", limit=20)

# 搜索包含 "session" 标签的 bugs
results = search_by_tag("session", limit=20)
```

#### 5.2 搜索最近创建的 bugs

```python
from scripts.bug_ops import search_recent

# 搜索最近 7 天创建的 bugs
recent = search_recent(days=7, limit=20)

# 搜索最近 30 天创建的 bugs
recent_month = search_recent(days=30, limit=50)
```

#### 5.3 搜索高分 bugs（需要重点关注）

```python
from scripts.bug_ops import search_high_score

# 搜索分数 >= 30 的高分 bugs
high_score = search_high_score(min_score=30.0, limit=20)

# 搜索分数 >= 20 的中高分 bugs
medium_high = search_high_score(min_score=20.0, limit=30)
```

#### 5.4 搜索最严重的前 N 个 bugs（高分 + 未验证）

```python
from scripts.bug_ops import search_top_critical

# 获取最严重的前 20 个未验证 bugs
critical = search_top_critical(limit=20)
```

**使用场景：**
- 快速定位最需要关注的问题
- 优先处理高风险的未验证 bugs

#### 5.5 搜索最近创建但未验证的 bugs

```python
from scripts.bug_ops import search_recent_unverified

# 搜索最近一周创建但未验证的 bugs
recent_unverified = search_recent_unverified(days=7, limit=20)

# 搜索最近一个月创建但未验证的 bugs
month_unverified = search_recent_unverified(days=30, limit=50)
```

**使用场景：**
- 检查新记录是否已验证
- 跟踪最近的 bug 修复进度

#### 5.6 组合搜索（状态 + 分数范围 + 验证状态）

```python
from scripts.bug_ops import search_by_status_and_score

# 搜索活跃的、分数在 20-40 之间的 bugs
medium_bugs = search_by_status_and_score(
    status="active",
    min_score=20.0,
    max_score=40.0,
    limit=30
)

# 搜索已验证的低分 bugs（< 20 分，可自动验证的小问题）
low_verified = search_by_status_and_score(
    status="active",
    max_score=20.0,
    verified=True,
    order_by="created_at",
    limit=20
)

# 搜索所有未验证的活跃 bugs（按分数排序）
unverified_active = search_by_status_and_score(
    status="active",
    verified=False,
    order_by="score",
    limit=50
)
```

## 展示搜索结果

搜索结果按分数排序，展示格式：

```
## 搜索结果：session（共 N 条）

### Bug #3 - session 存储未设置持久化 - 分数 42.5 ⏳未验证
**现象**：登录后 session 立即丢失
**根因**：session 存储时未设置持久化（预估）
**解决方案**：添加 cookie 的 maxAge 配置（预估）
**相关文件**：src/auth/session.ts, src/middleware/auth.ts
**autoRecall**：auth/*

> ⏳ 此 bug 未验证，根因和方案可能不完整。改代码时谨慎参考，如已修复请告知我验证。

### Bug #7 - 按钮样式错位 - 分数 18.0 ✅已验证(by User)
**现象**：按钮被遮挡
**根因**：CSS z-index 未设置
**解决方案**：添加 z-index: 1
**相关文件**：src/views/Login.vue
```

每个结果包含：
- Bug ID 和标题
- 分数（高亮前 3 条）
- 验证状态（未验证标注 ⏳，已验证标注 ✅）
- 现象（1-2 句）
- 根因和解决方案（预估的标注"预估"）
- 相关文件路径
- autoRecall 匹配模式

## 展示完整详情

如果用户需要查看某条 bug 的完整信息，使用 `get_bug_detail()`：

```python
detail = get_bug_detail(3)
```

展示格式：

```
## Bug #3 详情

**标题**：session 存储未设置持久化
**状态**：✅ 已验证
**创建时间**：2024-01-15
**更新时间**：2024-01-16
**验证时间**：2024-01-16 by User

### 评分
| 维度 | 分值 |
|------|------|
| 功能重要性 | 7 |
| 逻辑复杂度 | 5 |
| 影响范围 | 4 |
| 修复难度 | 3 |
| 出现次数 | 2 |
| 用户情绪 | 0 |
| 预防价值 | 6 |
| **总分** | **42.5** |

### 现象
session 存储后刷新页面立即失效

### 根因
session 中间件配置缺少 `cookie.maxAge`

### 解决方案
在 session 中间件配置中添加：
cookie: { maxAge: 7 * 24 * 60 * 60 * 1000 }

### 测试用例
登录后刷新页面，验证 session 保持

### 相关路径
- src/auth/session.ts
- src/middleware/auth.ts

### 标签
auth, session, cookie

### autoRecall
auth/*
```

## 主动召回提醒

当搜索到相关 bug 时，AI 应该主动提醒用户：

```
⚠️ 提醒：这个功能之前踩过坑（Bug #3）
涉及文件：src/auth/session.ts
建议：修改前先查看完整记录
```

## 注意事项

- 搜索结果默认最多 20 条，可通过 limit 参数调整
- 高分 bug（>30）必须展示完整信息
- 如果没有结果，提示用户可以记录新问题
- 搜索时忽略 `status=invalid` 的记录，除非用户明确要求
- 未验证 bug 在展示时标注 ⏳，并提醒用户谨慎参考
