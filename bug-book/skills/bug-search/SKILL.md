---
name: Bug Search
description: 当需要搜索错题集时触发。触发条件：用户询问有没有相关的 bug 记录、搜索特定关键词、查找某个文件的 bug 历史、查询某个功能的问题。
---

# Bug Search Skill

搜索 bug-book 数据库，快速找到相关的 bug 记录。

## 搜索场景

- 用户问"有没有 XX 相关的 bug"
- 改代码前查询相关历史问题
- 按文件/模块查找 bug
- 按标签/关键词查找

## 搜索流程

### 1. 关键词搜索

使用 `scripts/bug_ops.py` 的 `search_by_keyword()`：

```python
from scripts.bug_ops import search_by_keyword, get_bug_detail

results = search_by_keyword("session", limit=20)
```

### 2. 按路径召回

改代码前使用 `recall_by_path()` 或 `recall_by_pattern()`：

```python
from scripts.bug_ops import recall_by_path, recall_by_pattern

results = recall_by_path("src/auth/login.ts", limit=10)
results = recall_by_pattern("session", limit=10)
```

### 3. 按文件路径召回

当 AI 即将修改某个文件时，自动查询相关 bug：

```python
results = recall_by_path("src/api/user.ts")
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
