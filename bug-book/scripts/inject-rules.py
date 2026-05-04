#!/usr/bin/env python3
import os
import sys
import json

def main():
    # 1. 获取插件根目录（由环境变量提供）
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")

    if not plugin_root:
        # 如果获取失败，输出空消息，不阻断会话
        print(json.dumps({"continue": True}))
        return

    # 2. 构建规则文件的绝对路径
    rule_file_path = os.path.join(plugin_root, "rules", "bug-book.md")

    # 3. 读取规则内容
    try:
        with open(rule_file_path, 'r', encoding='utf-8') as f:
            rule_content = f.read().strip()
    except FileNotFoundError:
        # 如果文件不存在，静默退出（避免插件安装失败）
        print(json.dumps({"continue": True}))
        return

    # 4. 输出给 Claude Code 的标准结构
    output = {
        "continue": True,        # 继续执行会话
        "suppressOutput": True,  # 不在界面显示此 Hook 的输出
        "hookSpecificOutput": {  # SessionStart Hook 专用嵌套结构
            "hookEventName": "SessionStart",
            "additionalContext": rule_content  # 使用 additionalContext 而非 systemMessage
        }
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()