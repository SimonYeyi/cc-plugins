# 路径匹配工具单元测试 - test_path_utils.py

本文档覆盖 `tests/test_path_utils.py` 中所有测试用例。文档和测试代码一一对应，TC-XX 编号在两侧保持一致。

**测试文件**: `tests/test_path_utils.py`  
**测试对象**: `path_utils.py` 模块中的 `normalize_path()` 和 `match_path()` 函数
**总用例数**: **38 个测试用例**

---

## 用例统计

| 分类 | 用例数 | 编号区间 | 测试函数数 |
|------|--------|----------|-----------|
| normalize_path 路径标准化 | 5 | TC-P01 ~ TC-P05 | 5 |
| match_path 基础匹配（从 bug_ops 迁移） | 15 | TC-G01 ~ TC-G15 | 15 |
| match_path 反向匹配 | 6 | TC-R01 ~ TC-R06 | 6 |
| match_path 边界情况 | 9 | TC-B01 ~ TC-B09 | 9 |
| 真实场景测试 | 3 | TC-S01 ~ TC-S03 | 3 |
| **总计** | **38** | | **38** |

---

## TC-P01 ~ TC-P05：normalize_path 路径标准化

| 用例编号 | 测试函数 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|---------|-----------|------|---------|---------|
| TC-P01 | `test_normalize_path_windows` | Windows 路径分隔符转换 | `"src\\auth\\test.ts"` | `"src/auth/test.ts"` | 正常流程 |
| TC-P02 | `test_normalize_path_unix` | Unix 路径保持不变 | `"src/auth/test.ts"` | `"src/auth/test.ts"` | 正常流程 |
| TC-P03 | `test_normalize_path_mixed` | 混合路径分隔符 | `"src\\auth/test.ts"` | `"src/auth/test.ts"` | 正常流程 |
| TC-P04 | `test_normalize_path_no_separator` | 无分隔符路径 | `"Makefile"` | `"Makefile"` | 正常流程 |
| TC-P05 | `test_normalize_path_empty` | 空路径 | `""` | `"."`（Path 标准化结果） | 边界条件 |

---

## TC-G01 ~ TC-G15：match_path 基础匹配（从 bug_ops 迁移）

这些测试用例是从原 `test_bug_ops.py` 的 TC-G01~TC-G15 迁移而来，现在独立测试 `path_utils.match_path()` 函数。

| 用例编号 | 测试函数 | 测试点描述 | file_path | pattern | 预期 | 测试类型 |
|---------|---------|-----------|-----------|---------|------|---------|
| TC-G01 | `test_match_single_wildcard` | 单段通配符匹配子目录 | `src/auth/session.ts` | `auth/*` | True | 正常流程 |
| TC-G02 | `test_match_single_wildcard_false` | 单段通配符不匹配 authority | `src/authority/index.ts` | `auth/*` | False | 边界条件 |
| TC-G03 | `test_match_multi_prefix` | 多段前缀匹配子路径 | `src/auth/login.ts` | `src/auth/*` | True | 正常流程 |
| TC-G04 | `test_match_multi_prefix_false` | 多段前缀不匹配 | `src/api/user.ts` | `src/auth/*` | False | 边界条件 |
| TC-G05 | `test_match_single_exact` | 单段精确任意位置 | `src/auth/file.ts` | `auth` | True | 正常流程 |
| TC-G06 | `test_match_single_exact_false` | 单段精确不匹配 | `authz/login.ts` | `auth` | False | 边界条件 |
| TC-G07 | `test_match_multi_exact_prefix` | 多段精确前缀 | `src/auth/file.ts` | `src/auth` | True | 正常流程 |
| TC-G08 | `test_match_exact_file` | 精确匹配文件 | `src/auth/session.ts` | `src/auth/session.ts` | True | 正常流程 |
| TC-G09 | `test_match_windows_path` | Windows 路径兼容 | `src\\auth\\session.ts` | `auth/*` | True | 正常流程 |
| TC-G10 | `test_match_dir_not_match_wildcard` | 目录不匹配通配符 | `src/auth` | `src/auth/*` | False | 边界条件 |
| TC-G11 | `test_match_path_too_long` | 路径长度不足 | `a/b` | `a/b/c/d` | False | 异常处理 |
| TC-G12 | `test_match_makefile` | 根目录文件不匹配 | `Makefile` | `auth/*` | False | 边界条件 |
| TC-G13 | `test_match_trailing_slash` | 末尾斜杠去除 | `src/auth/` | `src/auth` | True | 边界条件 |
| TC-G14 | `test_match_empty_path` | 空文件路径 | `` | `auth/*` | False | 异常处理 |
| TC-G15 | `test_match_single_to_single` | 单段路径匹配单段模式 | `auth/login.ts` | `auth` | True | 正常流程 |

---

## TC-R01 ~ TC-R06：match_path 反向匹配

这些测试验证双向匹配逻辑：数据库存通配符模式，用户查模块名时能否召回。

| 用例编号 | 测试函数 | 测试点描述 | file_path | pattern | 预期 | 测试类型 |
|---------|---------|-----------|-----------|---------|------|---------|
| TC-R01 | `test_reverse_match_pattern_as_file` | 反向匹配：pattern 作为 file_path | `auth` | `auth/*` | True（裸模块名匹配通配符） | 正常流程 |
| TC-R02 | `test_reverse_match_file_as_pattern` | 反向匹配：完整文件路径作为 pattern（不支持） | `src/auth/*` | `src/auth/login.ts` | False（pattern 不应是具体路径） | 边界条件 |
| TC-R03 | `test_reverse_match_module_name` | 反向匹配：模块名与通配符模式 | `auth` | `auth/*` | True（数据库存 auth/*，用户查 auth） | 正常流程 |
| TC-R04 | `test_reverse_match_no_match` | 反向匹配：不匹配的情况 | `api` | `auth/*` | False | 边界条件 |
| TC-R05 | `test_reverse_match_exact_file` | 反向匹配：精确文件路径互换 | `src/auth/test.ts` | `src/auth/test.ts` | True（两种方向都匹配） | 正常流程 |
| TC-R06 | `test_reverse_match_multi_segment` | 反向匹配：多段路径 | `src/auth` | `src/auth/*` | False（目录不匹配通配符） | 边界条件 |

---

## TC-B01 ~ TC-B09：match_path 边界情况

| 用例编号 | 测试函数 | 测试点描述 | file_path | pattern | 预期 | 测试类型 |
|---------|---------|-----------|-----------|---------|------|---------|
| TC-B01 | `test_match_both_empty` | 两个参数都为空 | `` | `` | True（都是空的） | 边界条件 |
| TC-B02 | `test_match_pattern_empty` | pattern 为空 | `src/auth/test.ts` | `` | 行为取决于实现（接受 True 或 False） | 边界条件 |
| TC-B03 | `test_match_special_characters` | 特殊字符路径 | `src/auth-test/file.ts` | `auth-test/*` | True | 正常流程 |
| TC-B04 | `test_match_deep_nested` | 深层嵌套路径 | `a/b/c/d/e/f.ts` | `a/b/c/*` | True | 正常流程 |
| TC-B05 | `test_match_case_sensitive` | 大小写敏感 | `src/Auth/test.ts` | `auth/*` | False | 边界条件 |
| TC-B06 | `test_match_with_numbers` | 包含数字的路径 | `src/v1/auth.ts` | `v1/*` | True | 正常流程 |
| TC-B07 | `test_match_dot_files` | 隐藏文件匹配 | `.git/config` | `.git/*` | True | 正常流程 |
| TC-B08 | `test_match_extension` | 文件扩展名匹配 | `src/auth.ts` | `*.ts` | False（当前实现不支持 * 前缀） | 边界条件 |
| TC-B09 | `test_match_with_spaces` | 包含空格的路径 | `my folder/file.ts` | `my folder/*` | True | 正常流程 |

---

## 真实场景测试

| 用例编号 | 测试函数 | 测试点描述 | 场景说明 |
|---------|---------|-----------|---------|
| TC-S01 | `test_real_scenario_auth_module` | 真实场景：auth 模块重构 | 模拟 auth 模块从 `src/auth/` 迁移到 `src/modules/auth/`，验证召回逻辑 |
| TC-S02 | `test_real_scenario_api_vs_auth` | 真实场景：api 和 auth 区分 | 验证修改 api 文件不会召回 auth 相关 bug |
| TC-S03 | `test_real_scenario_wildcard_in_middle` | 真实场景：中间通配符 | 验证 `*/auth/*` 能匹配 `src/auth/test.ts` 和 `lib/auth/test.ts` |

---

## 执行说明

### 运行所有测试

```bash
cd D:/yeyi/AI/cc-plugins/bug-book
python -m pytest tests/test_path_utils.py -v
```

### 运行特定分类测试

```bash
# 只测试 normalize_path
python -m pytest tests/test_path_utils.py -v -k "normalize"

# 只测试基础匹配
python -m pytest tests/test_path_utils.py -v -k "match_single or match_multi or match_exact"

# 只测试反向匹配
python -m pytest tests/test_path_utils.py -v -k "reverse"

# 只测试边界情况
python -m pytest tests/test_path_utils.py -v -k "empty or special or case"

# 只测试真实场景
python -m pytest tests/test_path_utils.py -v -k "real_scenario"
```

---

## 测试架构说明

### 独立于后端实现

`test_path_utils.py` 直接测试 `path_utils` 模块的工具函数，不依赖任何后端实现（SQLite 或 JSONL）。这使得：

1. **测试速度快**：无需初始化数据库或文件
2. **隔离性好**：不受后端状态影响
3. **可复用性高**：任何使用 `path_utils` 的代码都可以依赖这些测试

### 测试覆盖范围

- **路径标准化**：Windows/Unix 路径兼容性
- **基础匹配**：通配符、前缀、精确匹配等 15 种场景
- **反向匹配**：双向匹配逻辑，支持模块名召回
- **边界情况**：空值、特殊字符、大小写等 9 种边界场景
- **真实场景**：3 个实际开发中可能遇到的场景

---

## 与后端测试的关系

`test_backends.py` 中的搜索测试（TC-H01~TC-H06）会调用后端的 `recall_by_path()` 和 `search_by_module_patterns()` 方法，这些方法内部使用 `path_utils.match_path()`。因此：

- **`test_path_utils.py`**：测试底层的匹配算法
- **`test_backends.py`**：测试完整的搜索流程（包括数据库查询 + 路径匹配）

两者互补，确保从底层算法到上层 API 都有充分测试。

---

## 相关文档

- [后端单元测试](./backends.md) - `tests/test_backends.py`
- [元数据存储测试](./metadata-store.md) - `tests/test_metadata_store.py`
- [MCP Server 端到端测试](./mcp-server-e2e.md) - `tests/test_mcp_server_e2e.py`
