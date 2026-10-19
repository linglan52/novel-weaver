"""db.py 的单元测试：CRUD 与配比统计。"""
from __future__ import annotations

import pytest

from novel_weaver.db import Database
from novel_weaver.models import (
    Chapter,
    Character,
    Foreshadow,
    LoreEntry,
    Relationship,
    SceneTag,
    Volume,
)


@pytest.fixture
def db(tmp_path):
    database = Database.init(tmp_path / "test.db")
    yield database
    database.close()


def test_init_creates_db(tmp_path):
    path = tmp_path / "novel.db"
    Database.init(path).close()
    assert path.exists()


def test_counts_empty(db):
    counts = db.counts()
    assert counts["characters"] == 0
    assert counts["chapters"] == 0


def test_character_crud(db):
    db.add_character(Character(name="林砚", role="主角"))
    chars = db.list_characters()
    assert len(chars) == 1
    assert chars[0].name == "林砚"
    assert chars[0].role == "主角"

    assert db.remove_character("林砚") == 1
    assert db.list_characters() == []


def test_character_name_is_unique(db):
    db.add_character(Character(name="林砚"))
    with pytest.raises(Exception):
        db.add_character(Character(name="林砚"))


def test_relationship(db):
    db.add_character(Character(name="林砚"))
    db.add_character(Character(name="沈青璃"))
    db.add_relationship(Relationship(
        from_name="林砚", to_name="沈青璃", rel_type="恋人", strength=4))
    rels = db.list_relationships()
    assert len(rels) == 1
    assert rels[0].rel_type == "恋人"
    assert rels[0].strength == 4


def test_volume_and_chapter(db):
    db.add_volume(Volume(title="沧澜启澜", seq=1))
    db.add_chapter(Chapter(title="外门试炼", seq=1, volume_seq=1, word_count=3600))

    assert len(db.list_volumes()) == 1
    chapters = db.list_chapters()
    assert len(chapters) == 1
    assert chapters[0].word_count == 3600

    db.set_chapter_word_count(1, 4000)
    assert db.list_chapters()[0].word_count == 4000


def test_tag_ratio_reaches_4_1(db):
    for _ in range(4):
        db.add_tag(SceneTag(chapter_seq=1, category="main"))
    db.add_tag(SceneTag(chapter_seq=1, category="emotion", subtype="daily_warmth"))

    ratio = db.tag_ratio()
    assert ratio["main"] == 4
    assert ratio["emotion"] == 1
    assert ratio["subtypes"] == {"daily_warmth": 1}


def test_tag_ratio_empty(db):
    ratio = db.tag_ratio()
    assert ratio["main"] == 0
    assert ratio["emotion"] == 0
    assert ratio["subtypes"] == {}


def test_lore(db):
    db.add_lore(LoreEntry(category="力量体系", name="灵海", content="炼气之根基"))
    entries = db.list_lore()
    assert len(entries) == 1
    assert entries[0].category == "力量体系"


def test_foreshadow_resolve(db):
    db.add_foreshadow(Foreshadow(description="灵海为何残缺"))
    fs = db.list_foreshadows()[0]
    assert fs.status == "埋设"

    db.resolve_foreshadow(fs.id, "第88章")
    resolved = db.list_foreshadows()[0]
    assert resolved.status == "已回收"
    assert resolved.resolve_chapter == "第88章"
