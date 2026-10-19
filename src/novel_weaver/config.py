"""配置与路径管理。

数据默认存放在用户主目录下的 ~/.novel_weaver/ 中，
可通过环境变量 NOVEL_WEAVER_HOME 覆盖（便于测试或切换多个写作项目）。
"""
from __future__ import annotations

import os
from pathlib import Path

APP_DIR_NAME = ".novel_weaver"
ENV_HOME = "NOVEL_WEAVER_HOME"


def get_home() -> Path:
    """数据目录，默认 ~/.novel_weaver/。"""
    override = os.environ.get(ENV_HOME)
    if override:
        return Path(override).expanduser()
    return Path.home() / APP_DIR_NAME


def get_db_path() -> Path:
    """SQLite 数据库文件路径。"""
    return get_home() / "novel.db"
