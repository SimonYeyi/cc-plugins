"""共享配置，供 init_db.py 和 bug_ops.py 共用"""

from pathlib import Path

PROJECT_MARKERS = {
    ".git",
    "package.json",
    "requirements.txt",
    "go.mod",
    "Cargo.toml",
    "pyproject.toml",
    "pom.xml",
    "CLAUDE.md",
}


class ProjectRootNotFoundError(Exception):
    """向上遍历到文件系统根目录仍未找到项目标记文件"""
    pass


def find_project_root() -> Path:
    """向上查找项目根目录。

    从插件目录向上遍历，找到第一个包含 PROJECT_MARKERS 中任意标记的目录。
    如果到达文件系统根目录仍未找到，抛出 ProjectRootNotFoundError。
    """
    plugin_dir = Path(__file__).parent.parent
    for parent in [plugin_dir] + list(plugin_dir.parents):
        if parent == parent.parent:
            raise ProjectRootNotFoundError(
                f"未找到项目根目录（已到达文件系统根目录 {parent}），"
                f"请在项目中添加以下任意标记文件: {', '.join(sorted(PROJECT_MARKERS))}"
            )
        if any((parent / m).exists() for m in PROJECT_MARKERS):
            return parent
    # 理论上不会执行到这里，因为循环会在 parent == parent.parent 时终止
    raise ProjectRootNotFoundError(  # pragma: no cover
        f"未找到项目根目录，请添加项目标记文件: {', '.join(sorted(PROJECT_MARKERS))}"
    )
