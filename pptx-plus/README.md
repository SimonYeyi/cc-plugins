# PPTX Plus Plugin

通过智能工作流生成专业分享 PPT 的 Claude Code 插件。

## 功能概述

将简略材料（文本/文件/文件夹/飞书文档）转换为可用于团队分享的专业演示文稿。整个过程由 AI 驱动，用户始终掌控方向和深度。

## 核心流程

```
用户输入 → 大纲生成 → 用户确认 → 丰富级别选择 → 内容丰富 → 内容预览确认 → PPT 生成 → 发送
```

8 步工作流，两次用户确认点（大纲 + 内容预览）。

## 文件结构

```
pptx-plus/
├── .claude-plugin/
│   └── plugin.json              # 插件清单
├── skills/
│   └── ppt-report/
│       └── SKILL.md            # 主工作流 skill
├── tools/
│   ├── content-enricher/       # 内容丰富工具（L1-L4）
│   │   └── SKILL.md
│   └── pptx/                   # PPT 生成工具
│       ├── SKILL.md
│       ├── pptxgenjs.md        # 从零创建 PPT
│       ├── editing.md          # 编辑现有 PPT
│       ├── scripts/            # 辅助脚本
│       └── LICENSE.txt
├── docs/
│   └── superpowers/
│       ├── specs/              # 设计规格
│       └── plans/              # 实施计划
└── test-workflow.md            # 测试指南
```

## 安装

### 方式一：从 GitHub 市场安装（推荐）

1. 添加插件市场

```bash
/plugin marketplace add SimonYeyi/cc-plugins
```

2. 安装插件：

```bash
/plugin install pptx-plus@cc-plugins
```

### 方式二：本地加载（开发时使用）

使用 `--plugin-dir` 参数启动 Claude Code：

```bash
claude --plugin-dir D:/path/to/cc-plugins/pptx-plus
```

这样可以实时调试插件修改。

## 升级

### 市场安装的用户

```bash
/plugin update pptx-plus@cc-plugins
```

### 本地开发用户

```bash
cd D:/path/to/cc-plugins/pptx-plus
git pull origin master
```

## 卸载

### 市场安装的用户

```bash
/plugin uninstall pptx-plus@cc-plugins
```

## 验证安装

在 Claude Code 中输入与 PPT 相关的请求（如"帮我做个PPT"），如果触发 `ppt-report` skill 则说明安装成功。

## 使用方式

### 触发方式

- 输入"帮我做 PPT"
- 输入"生成演示文稿"
- 引用 .pptx 文件
- 使用任何 PPT 相关词汇

### 工作流步骤

1. **STEP 1**：AI 解析输入（支持文本/文件/文件夹/飞书文档）
2. **STEP 2**：AI 生成 PPT 大纲呈现给用户
3. **STEP 3**：用户确认大纲，AI 立即保存原始材料
4. **STEP 4**：用户选择丰富级别（L1-L4）
5. **STEP 5**：AI 按级别丰富内容（L3/L4 含网络搜索）
6. **STEP 6**：用户预览确认内容，AI 立即保存
7. **STEP 7**：AI 生成 PPT 保存到 output 目录
8. **STEP 8**：AI 报告完成并发送文件

### 丰富级别

| 级别 | 说明 |
|------|------|
| L1 | 极简，仅大纲结构 |
| L2 | 基础，包含核心内容 |
| L3 | 标准，内容较完整（含网络搜索） |
| L4 | 详细，深度扩展（含深度网络搜索） |

## 依赖

- **feishu-doc**：读取飞书文档（全局 skill）
- **metabot**：飞书文件发送（全局 skill）
- **Web 搜索**：L3/L4 级别内容丰富

## 输出路径

- **输入保存**：`~/.pptx-plus/<话题>/input/`
- **PPT 输出**：`~/.pptx-plus/<话题>/output/`

## 测试

参见 `test-workflow.md` 了解完整的测试场景和检查清单。
