"""SQLite 数据库层：连接、建表、CRUD。

设计说明：
- 全部使用标准库 sqlite3，不引入 ORM，代码透明、零额外依赖。
- 表结构由 SCHEMA 定义；列名用 seq 表示顺序（避免与 SQL 关键字冲突）。
- 行记录通过 sqlite3.Row 读取后转成 models 里的 dataclass。
"""
from __future__ import annotations

import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import (
    Character,
    Chapter,
    Foreshadow,
    LoreEntry,
    Relationship,
    SceneTag,
    Volume,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS characters (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    alias       TEXT DEFAULT '',
    role        TEXT DEFAULT '配角',
    description TEXT DEFAULT '',
    appearance  TEXT DEFAULT '',
    personality TEXT DEFAULT '',
    background  TEXT DEFAULT '',
    status      TEXT DEFAULT '在世',
    created_at  TEXT DEFAULT '',
    updated_at  TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS relationships (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    from_name     TEXT NOT NULL,
    to_name       TEXT NOT NULL,
    rel_type      TEXT DEFAULT '其他',
    strength      INTEGER DEFAULT 3,
    description   TEXT DEFAULT '',
    start_chapter TEXT DEFAULT '',
    end_chapter   TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS volumes (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    title   TEXT NOT NULL,
    seq     INTEGER DEFAULT 1,
    summary TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS chapters (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    seq         INTEGER DEFAULT 1,
    volume_seq  INTEGER DEFAULT 1,
    summary     TEXT DEFAULT '',
    word_count  INTEGER DEFAULT 0,
    status      TEXT DEFAULT '草稿'
);

CREATE TABLE IF NOT EXISTS scene_tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_seq INTEGER NOT NULL,
    category    TEXT NOT NULL,
    subtype     TEXT DEFAULT '',
    note        TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS lore (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    name     TEXT NOT NULL,
    content  TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS foreshadows (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    description     TEXT NOT NULL,
    plant_chapter   TEXT DEFAULT '',
    status          TEXT DEFAULT '埋设',
    resolve_chapter TEXT DEFAULT '',
    note            TEXT DEFAULT ''
);
"""


def now() -> str:
    """当前时间戳，ISO 格式。"""
    return datetime.now().isoformat(timespec="seconds")


class Database:
    """封装 SQLite 连接与各实体的 CRUD。"""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row

    @classmethod
    def init(cls, path: Path) -> "Database":
        """初始化数据库文件并建表。"""
        path.parent.mkdir(parents=True, exist_ok=True)
        db = cls(path)
        db.conn.executescript(SCHEMA)
        db.conn.commit()
        return db

    # -- 生命周期 ---------------------------------------------------------
    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    # -- 通用辅助 ---------------------------------------------------------
    def _insert(self, sql: str, params: tuple) -> int:
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur.lastrowid

    def _fetchall(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        return self.conn.execute(sql, params).fetchall()

    # -- 人物 -------------------------------------------------------------
    def add_character(self, c: Character) -> int:
        ts = now()
        return self._insert(
            "INSERT INTO characters (name, alias, role, description, appearance,"
            " personality, background, status, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (c.name, c.alias, c.role, c.description, c.appearance,
             c.personality, c.background, c.status, ts, ts),
        )

    def list_characters(self) -> list[Character]:
        rows = self._fetchall("SELECT * FROM characters ORDER BY id")
        return [Character(
            name=r["name"], alias=r["alias"], role=r["role"],
            description=r["description"], appearance=r["appearance"],
            personality=r["personality"], background=r["background"],
            status=r["status"], id=r["id"],
            created_at=r["created_at"], updated_at=r["updated_at"],
        ) for r in rows]

    def get_character(self, name: str) -> Optional[Character]:
        r = self.conn.execute(
            "SELECT * FROM characters WHERE name = ?", (name,)).fetchone()
        if r is None:
            return None
        return Character(
            name=r["name"], alias=r["alias"], role=r["role"],
            description=r["description"], appearance=r["appearance"],
            personality=r["personality"], background=r["background"],
            status=r["status"], id=r["id"],
            created_at=r["created_at"], updated_at=r["updated_at"])

    def remove_character(self, name: str) -> int:
        cur = self.conn.execute(
            "DELETE FROM characters WHERE name = ?", (name,))
        self.conn.commit()
        return cur.rowcount

    # -- 关系 -------------------------------------------------------------
    def add_relationship(self, rel: Relationship) -> int:
        return self._insert(
            "INSERT INTO relationships (from_name, to_name, rel_type, strength,"
            " description, start_chapter, end_chapter)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (rel.from_name, rel.to_name, rel.rel_type, rel.strength,
             rel.description, rel.start_chapter, rel.end_chapter),
        )

    def list_relationships(self) -> list[Relationship]:
        rows = self._fetchall("SELECT * FROM relationships ORDER BY id")
        return [Relationship(
            from_name=r["from_name"], to_name=r["to_name"],
            rel_type=r["rel_type"], strength=r["strength"],
            description=r["description"], start_chapter=r["start_chapter"],
            end_chapter=r["end_chapter"], id=r["id"]) for r in rows]

    def remove_relationship(self, rel_id: int) -> int:
        cur = self.conn.execute(
            "DELETE FROM relationships WHERE id = ?", (rel_id,))
        self.conn.commit()
        return cur.rowcount

    # -- 卷 ---------------------------------------------------------------
    def add_volume(self, v: Volume) -> int:
        return self._insert(
            "INSERT INTO volumes (title, seq, summary) VALUES (?, ?, ?)",
            (v.title, v.seq, v.summary))

    def list_volumes(self) -> list[Volume]:
        rows = self._fetchall("SELECT * FROM volumes ORDER BY seq")
        return [Volume(title=r["title"], seq=r["seq"],
                        summary=r["summary"], id=r["id"]) for r in rows]

    def remove_volume(self, seq: int) -> int:
        cur = self.conn.execute("DELETE FROM volumes WHERE seq = ?", (seq,))
        self.conn.commit()
        return cur.rowcount

    # -- 章 ---------------------------------------------------------------
    def add_chapter(self, ch: Chapter) -> int:
        return self._insert(
            "INSERT INTO chapters (title, seq, volume_seq, summary, word_count,"
            " status) VALUES (?, ?, ?, ?, ?, ?)",
            (ch.title, ch.seq, ch.volume_seq, ch.summary,
             ch.word_count, ch.status))

    def list_chapters(self) -> list[Chapter]:
        rows = self._fetchall("SELECT * FROM chapters ORDER BY seq")
        return [Chapter(
            title=r["title"], seq=r["seq"], volume_seq=r["volume_seq"],
            summary=r["summary"], word_count=r["word_count"],
            status=r["status"], id=r["id"]) for r in rows]

    def set_chapter_word_count(self, seq: int, word_count: int) -> int:
        cur = self.conn.execute(
            "UPDATE chapters SET word_count = ? WHERE seq = ?",
            (word_count, seq))
        self.conn.commit()
        return cur.rowcount

    def remove_chapter(self, seq: int) -> int:
        cur = self.conn.execute("DELETE FROM chapters WHERE seq = ?", (seq,))
        self.conn.commit()
        return cur.rowcount

    # -- 场景标签（配比追踪） --------------------------------------------
    def add_tag(self, t: SceneTag) -> int:
        return self._insert(
            "INSERT INTO scene_tags (chapter_seq, category, subtype, note)"
            " VALUES (?, ?, ?, ?)",
            (t.chapter_seq, t.category, t.subtype, t.note))

    def list_tags(self) -> list[SceneTag]:
        rows = self._fetchall("SELECT * FROM scene_tags ORDER BY id")
        return [SceneTag(
            chapter_seq=r["chapter_seq"], category=r["category"],
            subtype=r["subtype"], note=r["note"], id=r["id"]) for r in rows]

    def tag_ratio(self) -> dict[str, int]:
        """统计主线 / 情感标签数量及情感子类分布。"""
        rows = self._fetchall(
            "SELECT category, subtype FROM scene_tags")
        main = sum(1 for r in rows if r["category"] == "main")
        emotion = sum(1 for r in rows if r["category"] == "emotion")
        subtypes = Counter(
            r["subtype"] for r in rows
            if r["category"] == "emotion" and r["subtype"])
        return {
            "main": main,
            "emotion": emotion,
            "subtypes": dict(subtypes),
        }

    def remove_tag(self, tag_id: int) -> int:
        cur = self.conn.execute("DELETE FROM scene_tags WHERE id = ?", (tag_id,))
        self.conn.commit()
        return cur.rowcount

    # -- 设定 -------------------------------------------------------------
    def add_lore(self, e: LoreEntry) -> int:
        return self._insert(
            "INSERT INTO lore (category, name, content) VALUES (?, ?, ?)",
            (e.category, e.name, e.content))

    def list_lore(self) -> list[LoreEntry]:
        rows = self._fetchall("SELECT * FROM lore ORDER BY category, name")
        return [LoreEntry(category=r["category"], name=r["name"],
                           content=r["content"], id=r["id"]) for r in rows]

    def remove_lore(self, lore_id: int) -> int:
        cur = self.conn.execute("DELETE FROM lore WHERE id = ?", (lore_id,))
        self.conn.commit()
        return cur.rowcount

    # -- 伏笔 -------------------------------------------------------------
    def add_foreshadow(self, f: Foreshadow) -> int:
        return self._insert(
            "INSERT INTO foreshadows (description, plant_chapter, status,"
            " resolve_chapter, note) VALUES (?, ?, ?, ?, ?)",
            (f.description, f.plant_chapter, f.status,
             f.resolve_chapter, f.note))

    def list_foreshadows(self) -> list[Foreshadow]:
        rows = self._fetchall("SELECT * FROM foreshadows ORDER BY id")
        return [Foreshadow(
            description=r["description"], plant_chapter=r["plant_chapter"],
            status=r["status"], resolve_chapter=r["resolve_chapter"],
            note=r["note"], id=r["id"]) for r in rows]

    def resolve_foreshadow(self, fs_id: int, resolve_chapter: str) -> int:
        cur = self.conn.execute(
            "UPDATE foreshadows SET status = '已回收', resolve_chapter = ?"
            " WHERE id = ?", (resolve_chapter, fs_id))
        self.conn.commit()
        return cur.rowcount

    def remove_foreshadow(self, fs_id: int) -> int:
        cur = self.conn.execute("DELETE FROM foreshadows WHERE id = ?", (fs_id,))
        self.conn.commit()
        return cur.rowcount

    # -- 概览 -------------------------------------------------------------
    def counts(self) -> dict[str, int]:
        tables = ["characters", "relationships", "volumes", "chapters",
                  "scene_tags", "lore", "foreshadows"]
        return {t: self.conn.execute(
            f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tables}
