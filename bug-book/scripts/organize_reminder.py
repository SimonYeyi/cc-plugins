#!/usr/bin/env python3
"""bug-book 会话启动 Hook - 检查是否需要提醒整理"""

import sys
import json
from pathlib import Path

# 确保可以导入 bug_ops
sys.path.insert(0, str(Path(__file__).parent))
from bug_ops import check_organize_reminder


def main():
    """检查是否需要提醒整理错题集"""
    result = check_organize_reminder(days_threshold=30)

    if result["should_remind"]:
        # 长期未整理 - 提醒但不强制
        message = (
            f"📋 Bug-Book 整理提醒：{result['message']}\n"
            f"上次整理时间: {result['last_organize_time']}\n"
            f"距今天数: {result['days_since']} 天\n"
            "建议操作: 运行 /bug-organize 开始整理"
        )

        # 输出 systemMessage JSON 格式
        print(json.dumps({"systemMessage": message}))
        return 0
    else:
        # 不需要提醒，静默退出
        return 0


if __name__ == "__main__":
    sys.exit(main())
