"""数据模型定义。

每个模型对应 SQLite 中的一张表，用 dataclass 表示一行记录。
人物用 name 作为自然键（UNIQUE），关系通过 name 引用人物，便于 CLI 直填名字。

领域约定：
- 主线:情感 建议配比 4:1；情感线分两个子类
    daily_warmth     日常温情（日常相处中的温情细节）
    adversity_warmth 逆境反压温情（困境中人物间的互相扶持）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# 人物定位枚举（自由字符串，此处给出常用值）
ROLES = ["主角", "配角", "反派", "龙套"]

# 关系类型枚举（自由字符串，给出常用值）
REL_TYPES = ["师徒", "恋人", "敌对", "亲情", "友情", "同门", "主仆", "其他"]

# 场景标签分类与情感子类
TAG_CATEGORIES = ["main", "emotion"]  # main=主线 / emotion=情感
EMOTION_SUBTYPES = ["daily_warmth", "adversity_warmth"]

# 设定条目分类
LORE_CATEGORIES = ["力量体系", "地名", "势力", "功法", "物品", "其他"]


@dataclass
class Character:
    """小说人物。"""
    name: str
    alias: str = ""
    role: str = "配角"          # 主角 / 配角 / 反派 / 龙套
    description: str = ""       # 一句话概括
    appearance: str = ""        # 外貌
    personality: str = ""       # 性格
    background: str = ""        # 背景
    status: str = "在世"        # 在世 / 死亡 / 退场
    id: Optional[int] = None
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Relationship:
    """人物之间的关系（有向：from 指向 to）。"""
    from_name: str
    to_name: str
    rel_type: str = "其他"      # 师徒 / 恋人 / 敌对 / ...
    strength: int = 3           # 亲疏强度 1-5，5 最亲近
    description: str = ""
    start_chapter: str = ""     # 关系起始章节
    end_chapter: str = ""       # 关系结束章节（空 = 仍在持续）
    id: Optional[int] = None


@dataclass
class Volume:
    """卷。"""
    title: str
    seq: int = 1                # 卷序号
    summary: str = ""
    id: Optional[int] = None


@dataclass
class Chapter:
    """章。"""
    title: str
    seq: int = 1                # 章内序号（全书唯一递增）
    volume_seq: int = 1         # 所属卷序号
    summary: str = ""
    word_count: int = 0
    status: str = "草稿"        # 草稿 / 已改 / 定稿
    id: Optional[int] = None


@dataclass
class SceneTag:
    """场景标签，用于主线/情感配比追踪。"""
    chapter_seq: int            # 所属章序号
    category: str               # main=主线 / emotion=情感
    subtype: str = ""           # 情感子类：daily_warmth / adversity_warmth
    note: str = ""
    id: Optional[int] = None


@dataclass
class LoreEntry:
    """世界观 / 设定条目。"""
    category: str               # 力量体系 / 地名 / 势力 / 功法 / 物品 / 其他
    name: str
    content: str = ""
    id: Optional[int] = None


@dataclass
class Foreshadow:
    """伏笔。"""
    description: str
    plant_chapter: str = ""     # 埋设章节
    status: str = "埋设"        # 埋设 / 已回收
    resolve_chapter: str = ""   # 回收章节
    note: str = ""
    id: Optional[int] = None
