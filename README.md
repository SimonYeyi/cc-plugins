# Claude Code Plugins

Claude Code 插件市场，管理多个插件项目。

## 插件列表

| 插件 | 说明 |
|------|------|
| pptx-plus | 通过智能工作流生成专业分享 PPT |

## 添加市场

GitHub 市场：
```bash
/plugin marketplace add SimonYeyi/cc-plugins
```
或手动编辑 settings.json：
```json
"extraKnownMarketplaces": {
  "cc-plugins": {
    "source": {
      "source": "github",
      "repo": "SimonYeyi/cc-plugins"
    }
  }
}
```

本地市场：
```bash
/plugin marketplace add D:/path/to/cc-plugins
```
或手动编辑 settings.json：
```json
"extraKnownMarketplaces": {
  "cc-plugins": {
    "source": {
      "source": "directory",
      "path": "D:/path/to/cc-plugins"
    }
  }
}
```

## 安装插件

```bash
/plugin install <插件名>@cc-plugins
```

## 升级插件

```bash
/plugin update <插件名>@cc-plugins
```

## 卸载插件

```bash
/plugin uninstall <插件名>@cc-plugins
```

## 本地开发

使用 `--plugin-dir` 参数启动 Claude Code：

```bash
claude --plugin-dir D:/path/to/cc-plugins/<插件名>
```

## 添加新插件

1. 在仓库根目录创建新插件子目录
2. 修改 `.claude-plugin/marketplace.json`，添加插件信息：

```json
{
  "name": "cc-plugins",
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
