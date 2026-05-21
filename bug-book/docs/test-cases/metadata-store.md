# 元数据存储单元测试 - test_metadata_store.py

本文档覆盖 `tests/test_metadata_store.py` 中所有测试用例。文档和测试代码一一对应，TC-XX 编号在两侧保持一致。

**测试文件**: `tests/test_metadata_store.py`  
**测试对象**: `mcp/metadata_store.py` 模块中的 `MetadataStore` 类  
**总用例数**: **25 个测试用例**

---

## 用例统计

| 分类 | 用例数 | 编号区间 | 测试函数数 |
|------|--------|----------|-----------|
| 初始化和持久化 | 4 | TC-M01 ~ TC-M04 | 4 |
| 基本 CRUD 操作 | 6 | TC-C01 ~ TC-C06 | 6 |
| 异常处理 | 3 | TC-E01 ~ TC-E03 | 3 |
| 整理时间管理 | 4 | TC-T01 ~ TC-T04 | 4 |
| 单例模式和线程安全 | 2 | TC-S01 ~ TC-S02 | 2 |
| 边界情况 | 6 | TC-B01 ~ TC-B06 | 6 |
| **总计** | **25** | | **25** |

---

## TC-M01 ~ TC-M04：初始化和持久化

| 用例编号 | 测试函数 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|---------|-----------|------|---------|---------|
| TC-M01 | `test_init_creates_file` | 初始化时创建文件 | 首次实例化 MetadataStore | meta.json 文件被创建 | 正常流程 |
| TC-M02 | `test_init_loads_existing_data` | 初始化时加载已有数据 | 预先写入数据到 meta.json | 实例能读取到已有数据 | 正常流程 |
| TC-M03 | `test_persistence_across_instances` | 跨实例持久化 | 实例 A 写入数据，实例 B 读取 | 实例 B 能读到实例 A 写入的数据 | 正常流程 |
| TC-M04 | `test_file_format` | 文件格式验证 | 写入数据后检查文件内容 | JSON 格式正确，包含所有键值对 | 正常流程 |

---

## TC-C01 ~ TC-C06：基本 CRUD 操作

| 用例编号 | 测试函数 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|---------|-----------|------|---------|---------|
| TC-C01 | `test_set_and_get` | 设置和获取键值对 | `set("key", "value")` | `get("key") == "value"` | 正常流程 |
| TC-C02 | `test_get_nonexistent_key` | 获取不存在的键 | `get("nonexistent")` | 返回 None | 边界条件 |
| TC-C03 | `test_set_overwrites` | 覆盖已有键 | `set("key", "v1")` 然后 `set("key", "v2")` | `get("key") == "v2"` | 正常流程 |
| TC-C04 | `test_remove` | 删除键 | `set("key", "value")` 然后 `remove("key")` | `get("key") is None` | 正常流程 |
| TC-C05 | `test_remove_nonexistent` | 删除不存在的键 | `remove("nonexistent")` | 无报错 | 边界条件 |
| TC-C06 | `test_unicode_support` | Unicode 支持 | `set("中文键", "中文值")` | 能正确存储和读取 | 正常流程 |

---

## TC-E01 ~ TC-E03：异常处理

| 用例编号 | 测试函数 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|---------|-----------|------|---------|---------|
| TC-E01 | `test_corrupted_file_handling` | 损坏的文件处理 | 写入非法 JSON 到 meta.json | 自动重置为空数据，不崩溃 | 异常处理 |
| TC-E02 | `test_empty_file_handling` | 空文件处理 | 创建空的 meta.json | 自动重置为空数据，不崩溃 | 异常处理 |
| TC-E03 | `test_permission_error_simulation` | 权限错误模拟 | 模拟文件写入失败 | 优雅降级，不崩溃 | 异常处理 |

---

## TC-T01 ~ TC-T04：整理时间管理

这些是元数据存储的核心功能，用于管理 bug-book 整理提醒。

| 用例编号 | 测试函数 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|---------|-----------|------|---------|---------|
| TC-T01 | `test_set_last_organize_time` | 设置最后整理时间 | `set_last_organize_time()` | last_organize_time 设置为当前 ISO 时间字符串 | 正常流程 |
| TC-T02 | `test_get_last_organize_time_none` | 首次调用返回 None | 全新实例，未设置过时间 | `get_last_organize_time()` 返回 None | 边界条件 |
| TC-T03 | `test_check_reminder_first_time` | 首次调用检查提醒 | `check_organize_reminder(days_threshold=30)` | should_remind=False, last_organize_time=None, days_since=None，并自动设置时间 | 正常流程 |
| TC-T04 | `test_check_reminder_custom_threshold` | 自定义阈值检查 | 设置时间为 40 天前，`check_organize_reminder(days_threshold=30)` | should_remind=True, days_since>=40 | 正常流程 |

---

## TC-S01 ~ TC-S02：单例模式和线程安全

| 用例编号 | 测试函数 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|---------|-----------|------|---------|---------|
| TC-S01 | `test_singleton_pattern` | 单例模式验证 | 多次实例化 MetadataStore | 所有实例是同一个对象（id 相同） | 正常流程 |
| TC-S02 | `test_thread_safety` | 线程安全验证 | 多线程并发读写 | 无数据竞争，最终状态一致 | 正常流程 |

---

## TC-B01 ~ TC-B06：边界情况

| 用例编号 | 测试函数 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|---------|-----------|------|---------|---------|
| TC-B01 | `test_empty_string_value` | 空字符串值 | `set("key", "")` | `get("key") == ""` | 边界条件 |
| TC-B02 | `test_none_value` | None 值 | `set("key", None)` | `get("key") is None` | 边界条件 |
| TC-B03 | `test_numeric_string` | 数字字符串 | `set("key", "123")` | `get("key") == "123"`（保持字符串类型） | 边界条件 |
| TC-B04 | `test_long_key_and_value` | 长键和长值 | 设置超长键值对（>1000 字符） | 能正确存储和读取 | 边界条件 |
| TC-B05 | `test_special_characters_in_key` | 键中包含特殊字符 | `set("key.with.dots", "value")` | 能正确存储和读取 | 边界条件 |
| TC-B06 | `test_boolean_string` | 布尔字符串 | `set("key", "true")` | `get("key") == "true"`（保持字符串，不转换） | 边界条件 |

---

## 执行说明

### 运行所有测试

```bash
cd D:/yeyi/AI/cc-plugins/bug-book
python -m pytest tests/test_metadata_store.py -v
```

### 运行特定分类测试

```bash
# 只测试初始化
python -m pytest tests/test_metadata_store.py -v -k "init"

# 只测试 CRUD 操作
python -m pytest tests/test_metadata_store.py -v -k "set or get or remove"

# 只测试异常处理
python -m pytest tests/test_metadata_store.py -v -k "corrupted or empty or permission"

# 只测试整理时间
python -m pytest tests/test_metadata_store.py -v -k "organize or reminder"

# 只测试单例和线程安全
python -m pytest tests/test_metadata_store.py -v -k "singleton or thread"
```

---

## 测试架构说明

### 临时目录隔离

测试使用 `tempfile.mkdtemp()` 创建临时目录，并通过环境变量 `CLAUDE_PLUGIN_DATA` 指向该目录，确保：

1. **不影响生产数据**：测试数据与生产数据完全隔离
2. **自动清理**：测试结束后通过 `teardown_module()` 清理临时目录
3. **可重复执行**：每次测试都是干净的环境

### 模块级变量处理

由于 `metadata_store.META_FILE` 在模块导入时计算，测试采用以下策略：

1. **先设置环境变量**：在 `setup_module()` 中设置 `CLAUDE_PLUGIN_DATA`
2. **再导入模块**：确保 `META_FILE` 指向测试目录
3. **清除模块缓存**：在 `setup_function()` 中删除 `sys.modules['metadata_store']`，强制重新导入

### 单例模式测试

`MetadataStore` 使用单例模式，测试时需要注意：

- **不需要手动重置单例**：通过清除模块缓存实现隔离
- **线程安全测试**：使用 `threading.Thread` 并发访问，验证无数据竞争

---

## 核心功能说明

### 元数据存储用途

`metadata_store.py` 不是通用的元数据存储，而是专门用于：

1. **记录最后整理时间**：`last_organize_time` 字段
2. **检查是否需要提醒**：距离上次整理超过阈值时提醒用户
3. **本地轻量级存储**：使用简单的 JSON 文件，无需数据库

### 为什么独立于 MCP Server？

metadata 功能是本地辅助功能，不需要通过 MCP 协议暴露：

- **直接调用**：Skill 或脚本可以直接 import 使用
- **简化架构**：减少不必要的 MCP 工具定义
- **提高性能**：避免 JSON-RPC 通信开销

---
