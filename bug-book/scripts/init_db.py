#!/usr/bin/env python3
"""初始化 bug-book SQLite 数据库"""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import find_project_root

DB_PATH = find_project_root() / "bug-book.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS bugs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    title       TEXT NOT NULL,
    phenomenon  TEXT NOT NULL,
    root_cause  TEXT,
    solution    TEXT,
    test_case   TEXT,
    status      TEXT DEFAULT 'active' CHECK(status IN ('active', 'resolved', 'invalid')),
    verified    INTEGER DEFAULT 0,
    verified_at DATETIME,
    verified_by TEXT,
    score       REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bug_scores (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id      INTEGER NOT NULL,
    dimension   TEXT NOT NULL,
    value       REAL NOT NULL,
    FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bug_paths (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id      INTEGER NOT NULL,
    path        TEXT NOT NULL,
    is_old      INTEGER DEFAULT 0,
    FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bug_tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id      INTEGER NOT NULL,
    tag         TEXT NOT NULL,
    FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bug_keywords (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id      INTEGER NOT NULL,
    keyword     TEXT NOT NULL,
    FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bug_recalls (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id      INTEGER NOT NULL,
    pattern     TEXT NOT NULL,
    FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_bugs_score ON bugs(score DESC);
CREATE INDEX IF NOT EXISTS idx_bugs_status ON bugs(status);
CREATE INDEX IF NOT EXISTS idx_bugs_verified ON bugs(verified);
CREATE INDEX IF NOT EXISTS idx_bugs_created_at ON bugs(created_at);
CREATE INDEX IF NOT EXISTS idx_bug_scores_bug_id ON bug_scores(bug_id);
CREATE INDEX IF NOT EXISTS idx_paths_path ON bug_paths(path);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON bug_tags(tag);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON bug_keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_recalls_pattern ON bug_recalls(pattern);
"""

# FTS5 虚拟表用于全文搜索
FTS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS bugs_fts USING fts5(
    title,
    phenomenon,
    root_cause,
    solution,
    test_case,
    content='bugs',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS bugs_fts_insert AFTER INSERT ON bugs BEGIN
    INSERT INTO bugs_fts(rowid, title, phenomenon, root_cause, solution, test_case)
    VALUES (new.id, new.title, new.phenomenon, new.root_cause, new.solution, new.test_case);
END;

CREATE TRIGGER IF NOT EXISTS bugs_fts_delete AFTER DELETE ON bugs BEGIN
    INSERT INTO bugs_fts(bugs_fts, rowid, title, phenomenon, root_cause, solution, test_case)
    VALUES ('delete', old.id, old.title, old.phenomenon, old.root_cause, old.solution, old.test_case);
END;

CREATE TRIGGER IF NOT EXISTS bugs_fts_update AFTER UPDATE ON bugs BEGIN
    INSERT INTO bugs_fts(bugs_fts, rowid, title, phenomenon, root_cause, solution, test_case)
    VALUES ('delete', old.id, old.title, old.phenomenon, old.root_cause, old.solution, old.test_case);
    INSERT INTO bugs_fts(rowid, title, phenomenon, root_cause, solution, test_case)
    VALUES (new.id, new.title, new.phenomenon, new.root_cause, new.solution, new.test_case);
END;
"""


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    try:
        conn.executescript(FTS_SCHEMA)
    except sqlite3.OperationalError as e:
        # FTS5 可能不可用（Android/某些嵌入式SQLite），降级
        import sys as _sys
        print(f"FTS5 不可用，将使用LIKE搜索降级: {e}", file=_sys.stderr)
    conn.commit()
    print(f"数据库已初始化: {DB_PATH}")


if __name__ == "__main__":
    init_db()
