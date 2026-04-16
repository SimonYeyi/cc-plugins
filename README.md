# Claude Plugins

Claude Code 插件市场，管理多个插件项目。

## 插件列表

| 插件 | 说明 |
|------|------|
| pptx-plus | 通过智能工作流生成专业分享 PPT |

## 添加市场

### 方式一：GitHub 市场

在 `~/.claude/settings.json` 的 `extraKnownMarketplaces` 中添加：

```json
"extraKnownMarketplaces": {
  "claude-plugins": {
    "source": {
      "source": "github",
      "repo": "SimonYeyi/claude-plugins"
    }
  }
}
```

> Claude Code 重启后生效。
>
> **注意**：目前没有自动化命令添加市场，需要手动编辑 `settings.json`。

### 方式二：本地市场（开发时使用）

本地开发时，可以添加本地市场目录：

```json
"extraKnownMarketplaces": {
  "local-dev": {
    "source": {
      "source": "local",
      "path": "D:/path/to/claude-plugins"
    }
  }
}
```

然后安装本地插件：

```bash
/plugin install pptx-plus@local-dev
```

## 安装插件

```bash
/plugin install <插件名>@claude-plugins
```

例如安装 pptx-plus：
```bash
/plugin install pptx-plus@claude-plugins
```

## 升级插件

```bash
/plugin update <插件名>@claude-plugins
```

## 卸载插件

```bash
/plugin uninstall <插件名>@claude-plugins
```

## 本地开发

使用 `--plugin-dir` 参数启动 Claude Code：

```bash
claude --plugin-dir D:/path/to/claude-plugins/pptx-plus
```

## 添加新插件

1. 在仓库根目录创建新插件子目录
2. 修改 `.claude-plugin/marketplace.json`，添加插件信息：

```json
{
  "name": "claude-plugins",
  "plugins": [
    {
      "name": "新插件名",
      "description": "插件描述",
      "version": "1.0.0",
      "source": {
        "source": "local",
        "path": "./新插件目录"
      }
    }
  ]
}
```
