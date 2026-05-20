#!/usr/bin/env python3
"""bug-book 会话启动 Hook - 检查是否需要提醒整理"""

import sys
import json
from pathlib import Path

# 确保可以导入 mcp 模块
sys.path.insert(0, str(Path(__file__).parent.parent / 'mcp'))

from metadata_store import metadata_store


def main():
    """检查是否需要提醒整理错题集"""
    result = metadata_store.check_organize_reminder(days_threshold=30)

    if result["should_remind"]:
        # 长期未整理 - 提醒但不强制
        message = f"📋 Bug-Book 已有 {result['days_since']} 天未整理。如需整理，请输入：整理bug-book"

        # 输出 systemMessage JSON 格式
        print(json.dumps({"systemMessage": message}))
        return 0
    else:
        # 不需要提醒，静默退出
        return 0


if __name__ == "__main__":
    sys.exit(main())
