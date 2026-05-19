# 测试用例文档索引

本文档是 bug-book 项目所有测试用例文档的索引。每个测试文件对应一份独立的测试用例文档，文档中的用例编号与测试代码完全对齐。

---

## 测试文件与文档映射

| 测试文件 | 测试用例文档 | 用例数 | 说明 |
|---------|------------|--------|------|
| `tests/test_backends.py` | [backends.md](./backends.md) | 75 函数 × 2 后端 = **150 用例** | SQLite 和 JSONL 双后端测试 |
| `tests/test_path_utils.py` | [path-utils.md](./path-utils.md) | **38 用例** | 路径匹配工具函数独立测试 |
| `tests/test_metadata_store.py` | [metadata-store.md](./metadata-store.md) | **25 用例** | 元数据存储单例测试 |
| `tests/test_mcp_server_e2e.py` | [mcp-server-e2e.md](./mcp-server-e2e.md) | **31 工具** × 2 后端 | MCP Server 端到端测试 |

**总计**: **244+ 个测试用例**

---

## 文档结构说明

### 1. [后端双实现测试 - backends.md](./backends.md)

**覆盖范围**: `tests/test_backends.py`

**测试分类**:
- TC-A: add_bug 新增记录（8 用例）
- TC-B: update_bug 更新记录（6 用例）
- TC-C: delete_bug 删除记录（3 用例）
- TC-D: increment_score 分数累加（3 用例）
- TC-E: update_bug_paths / add_recall（3 用例）
- TC-F: search_by_keyword 关键词搜索（5 用例）
- TC-H: recall_by_path / recall_by_pattern 路径召回（9 用例）
- TC-S: 高级搜索（5 用例）
- TC-I: get_bug_detail 详情查询（4 用例）
- TC-J: list_bugs 列表查询（4 用例）
- TC-K: mark_invalid 失效标记（3 用例）
- TC-L: 懒初始化与集成（3 用例）
- TC-M: 影响关系管理（10 用例）
- TC-N: 路径和 recalls 管理（5 用例）
- TC-O: 路径迁移（3 用例）

**特点**:
- 使用 pytest 参数化 fixture，每个测试在 SQLite 和 JSONL 两个后端各执行一次
- 完整的 CRUD、搜索、召回、影响关系等后端公共 API 测试
- 测试隔离：每次测试前清理数据库/文件

---

### 2. [路径匹配工具测试 - path-utils.md](./path-utils.md)

**覆盖范围**: `tests/test_path_utils.py`

**测试分类**:
- TC-P: normalize_path 路径标准化（5 用例）
- TC-G: match_path 基础匹配（15 用例，从 bug_ops 迁移）
- TC-R: match_path 反向匹配（6 用例）
- TC-B: match_path 边界情况（9 用例）

**特点**:
- 独立于后端实现，直接测试 `path_utils` 模块
- 覆盖 Windows/Unix 路径兼容性
- 包含双向匹配逻辑测试（数据库存通配符，用户查模块名）
- 测试速度快，无需初始化数据库

---

### 3. [元数据存储测试 - metadata-store.md](./metadata-store.md)

**覆盖范围**: `tests/test_metadata_store.py`

**测试分类**:
- TC-M: 初始化和持久化（4 用例）
- TC-C: 基本 CRUD 操作（6 用例）
- TC-E: 异常处理（3 用例）
- TC-T: 整理时间管理（4 用例）
- TC-S: 单例模式和线程安全（2 用例）
- TC-B: 边界情况（6 用例）

**特点**:
- 测试 `MetadataStore` 单例模式
- 核心功能：记录最后整理时间、检查是否需要提醒
- 临时目录隔离，不影响生产数据
- 模块级变量处理策略

---

### 4. [MCP Server 端到端测试 - mcp-server-e2e.md](./mcp-server-e2e.md)

**覆盖范围**: `tests/test_mcp_server_e2e.py`

**测试分类**:
- CRUD 操作（5 工具）
- 查询功能（3 工具）
- 搜索功能（7 工具）
- 召回功能（3 工具）
- 影响关系管理（6 工具）
- 高级功能（3 工具）

**特点**:
- 通过 stdio 协议与 MCP Server 通信
- 覆盖所有 31 个 MCP 工具
- SQLite 和 JSONL 双后端测试
- 真实场景的端到端验证

---

## 测试执行指南

### 运行所有测试

```bash
cd D:/yeyi/AI/cc-plugins/bug-book
python -m pytest tests/ -v
```

### 运行特定测试文件

```bash
# 后端双实现测试
python -m pytest tests/test_backends.py -v

# 路径匹配工具测试
python -m pytest tests/test_path_utils.py -v

# 元数据存储测试
python -m pytest tests/test_metadata_store.py -v

# MCP Server 端到端测试
python -m pytest tests/test_mcp_server_e2e.py -v
```

### 运行特定后端测试

```bash
# 只测试 SQLite 后端
python -m pytest tests/test_backends.py -v -k sqlite

# 只测试 JSONL 后端
python -m pytest tests/test_backends.py -v -k jsonl
```

### 运行特定分类测试

```bash
# 只测试 CRUD 操作
python -m pytest tests/test_backends.py -v -k "add_bug or update_bug or delete_bug"

# 只测试影响关系
python -m pytest tests/test_backends.py -v -k "impact"

# 只测试路径匹配
python -m pytest tests/test_path_utils.py -v -k "match"

# 只测试整理时间
python -m pytest tests/test_metadata_store.py -v -k "organize or reminder"
```

---

## 测试架构说明

### 测试分层

1. **单元测试层** (`test_path_utils.py`, `test_metadata_store.py`)
   - 测试独立的工具函数和模块
   - 不依赖后端实现
   - 执行速度快

2. **集成测试层** (`test_backends.py`)
   - 测试后端公共 API
   - 参数化测试 SQLite 和 JSONL
   - 完整的业务逻辑验证

3. **端到端测试层** (`test_mcp_server_e2e.py`)
   - 测试 MCP Server 完整流程
   - 通过 stdio 协议通信
   - 真实场景验证

### 测试隔离策略

- **临时目录**: 使用 `tempfile.mkdtemp()` 创建隔离的测试环境
- **模块缓存清除**: 使用 `del sys.modules[...]` 强制重新导入
- **数据清理**: 每次测试前清理数据库/文件

### 测试覆盖率

- **后端接口**: 100% 覆盖所有公共 API
- **MCP 工具**: 100% 覆盖所有 31 个工具
- **路径匹配**: 覆盖 38 种匹配场景
- **元数据存储**: 覆盖 25 种操作和边界情况

---

## 相关资源

- [SPEC.md](../SPEC.md) - 项目规格说明
- [README.md](../../../README.md) - 项目说明
- [CLAUDE.md](../../../CLAUDE.md) - AI 助手指南

---

## 更新记录

| 日期 | 更新内容 |
|------|---------|
| 2026-05-08 | 重构测试文档结构，每份测试文件对应独立文档 |
| 2026-05-08 | 修复 test_backends.py 重复测试函数名问题 |
| 2026-05-08 | 新增 path-utils.md 和 metadata-store.md |
| 2026-05-08 | 删除旧的 logic.md，统一文档结构 |
