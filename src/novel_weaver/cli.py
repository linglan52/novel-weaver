"""CLI 入口（Typer）。

所有子命令分组：
    init           初始化数据库
    status         数据概览
    character      人物管理
    relationship   人物关系
    volume         卷
    chapter        章
    tag            场景标签（主线/情感配比）
    lore           设定库
    foreshadow     伏笔
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __app_name__, __version__
from .config import get_db_path
from .db import Database
from .models import (
    Character,
    Chapter,
    Foreshadow,
    LoreEntry,
    Relationship,
    SceneTag,
    Volume,
)

app = typer.Typer(
    help=f"{__app_name__} v{__version__} —— 长篇网文结构管理与 AI 一致性助手",
    no_args_is_help=True,
)
console = Console()


def _open_db() -> Database:
    """打开数据库；文件不存在时提示先 init。"""
    path = get_db_path()
    if not path.exists():
        console.print(
            f"[red]数据库不存在：{path}[/red]\n"
            f"请先运行 [bold]novel-weaver init[/bold] 初始化。")
        raise typer.Exit(code=1)
    return Database(path)


def _print_table(title: str, columns: list[str], rows: list[list]) -> None:
    table = Table(title=title, title_justify="left")
    for col in columns:
        table.add_column(col, overflow="fold")
    for row in rows:
        table.add_row(*[str(x) if x is not None else "" for x in row])
    console.print(table)


# ---------------------------------------------------------------------------
# 顶层命令
# ---------------------------------------------------------------------------
@app.command()
def init() -> None:
    """初始化数据库（在默认数据目录建表）。"""
    path = get_db_path()
    if path.exists():
        console.print(f"[yellow]数据库已存在，跳过：{path}[/yellow]")
        return
    Database.init(path).close()
    console.print(f"[green]✓ 已初始化数据库：{path}[/green]")


@app.command()
def status() -> None:
    """查看数据概览与数据库位置。"""
    path = get_db_path()
    if not path.exists():
        console.print(f"[yellow]尚未初始化。请先运行 novel-weaver init[/yellow]")
        return
    with _open_db() as db:
        counts = db.counts()
    console.print(f"数据库：[bold]{path}[/bold]")
    labels = {
        "characters": "人物", "relationships": "关系", "volumes": "卷",
        "chapters": "章", "scene_tags": "场景标签", "lore": "设定条目",
        "foreshadows": "伏笔",
    }
    table = Table(title="数据概览", title_justify="left")
    table.add_column("类别")
    table.add_column("数量", justify="right")
    for key, label in labels.items():
        table.add_row(label, str(counts[key]))
    console.print(table)


# ---------------------------------------------------------------------------
# 人物
# ---------------------------------------------------------------------------
character_app = typer.Typer(help="人物管理", no_args_is_help=True)
app.add_typer(character_app, name="character")


@character_app.command("add")
def character_add(
    name: str = typer.Option(..., "--name", help="姓名（唯一）"),
    alias: str = typer.Option("", "--alias", help="别名/称号"),
    role: str = typer.Option("配角", "--role", help="主角/配角/反派/龙套"),
    description: str = typer.Option("", "--description", help="一句话概括"),
    appearance: str = typer.Option("", "--appearance", help="外貌"),
    personality: str = typer.Option("", "--personality", help="性格"),
    background: str = typer.Option("", "--background", help="背景"),
    status: str = typer.Option("在世", "--status", help="在世/死亡/退场"),
) -> None:
    """新增人物。"""
    with _open_db() as db:
        try:
            db.add_character(Character(
                name=name, alias=alias, role=role, description=description,
                appearance=appearance, personality=personality,
                background=background, status=status))
        except Exception as e:  # noqa: BLE001
            console.print(f"[red]添加失败：{e}[/red]")
            raise typer.Exit(code=1)
    console.print(f"[green]✓ 已添加人物：{name}[/green]")


@character_app.command("list")
def character_list() -> None:
    """列出全部人物。"""
    with _open_db() as db:
        chars = db.list_characters()
    if not chars:
        console.print("[yellow]暂无人物[/yellow]")
        return
    _print_table(
        "人物", ["ID", "姓名", "别名", "定位", "状态", "概括"],
        [[c.id, c.name, c.alias, c.role, c.status, c.description] for c in chars])


@character_app.command("rm")
def character_rm(name: str = typer.Argument(..., help="人物姓名")) -> None:
    """删除人物。"""
    with _open_db() as db:
        n = db.remove_character(name)
    console.print(f"[green]✓ 已删除 {n} 条人物记录[/green]" if n
                  else f"[yellow]未找到人物：{name}[/yellow]")


# ---------------------------------------------------------------------------
# 关系
# ---------------------------------------------------------------------------
relationship_app = typer.Typer(help="人物关系管理", no_args_is_help=True)
app.add_typer(relationship_app, name="relationship")


@relationship_app.command("add")
def relationship_add(
    from_name: str = typer.Option(..., "--from", help="关系主体人物名"),
    to_name: str = typer.Option(..., "--to", help="关系对象人物名"),
    rel_type: str = typer.Option("其他", "--type", help="师徒/恋人/敌对/亲情/友情/同门/主仆/其他"),
    strength: int = typer.Option(3, "--strength", help="亲疏强度 1-5，5 最亲近"),
    description: str = typer.Option("", "--description", help="关系说明"),
    start_chapter: str = typer.Option("", "--start", help="关系起始章节"),
    end_chapter: str = typer.Option("", "--end", help="关系结束章节（空=仍在持续）"),
) -> None:
    """新增人物关系（有向：--from 指向 --to）。"""
    with _open_db() as db:
        db.add_relationship(Relationship(
            from_name=from_name, to_name=to_name, rel_type=rel_type,
            strength=strength, description=description,
            start_chapter=start_chapter, end_chapter=end_chapter))
    console.print(f"[green]✓ 已添加关系：{from_name} --{rel_type}--> {to_name}[/green]")


@relationship_app.command("list")
def relationship_list() -> None:
    """列出全部关系。"""
    with _open_db() as db:
        rels = db.list_relationships()
    if not rels:
        console.print("[yellow]暂无关系[/yellow]")
        return
    _print_table(
        "人物关系", ["ID", "主体", "关系", "对象", "强度", "说明"],
        [[r.id, r.from_name, r.rel_type, r.to_name, r.strength, r.description]
         for r in rels])


@relationship_app.command("rm")
def relationship_rm(rel_id: int = typer.Argument(..., help="关系 ID")) -> None:
    """删除关系。"""
    with _open_db() as db:
        n = db.remove_relationship(rel_id)
    console.print(f"[green]✓ 已删除 {n} 条关系[/green]" if n
                  else f"[yellow]未找到关系 ID：{rel_id}[/yellow]")


# ---------------------------------------------------------------------------
# 卷
# ---------------------------------------------------------------------------
volume_app = typer.Typer(help="卷管理", no_args_is_help=True)
app.add_typer(volume_app, name="volume")


@volume_app.command("add")
def volume_add(
    title: str = typer.Option(..., "--title", help="卷标题"),
    seq: int = typer.Option(1, "--seq", help="卷序号"),
    summary: str = typer.Option("", "--summary", help="卷梗概"),
) -> None:
    """新增卷。"""
    with _open_db() as db:
        db.add_volume(Volume(title=title, seq=seq, summary=summary))
    console.print(f"[green]✓ 已添加第 {seq} 卷：{title}[/green]")


@volume_app.command("list")
def volume_list() -> None:
    """列出全部卷。"""
    with _open_db() as db:
        vols = db.list_volumes()
    if not vols:
        console.print("[yellow]暂无卷[/yellow]")
        return
    _print_table("卷", ["序号", "标题", "梗概"],
                 [[v.seq, v.title, v.summary] for v in vols])


@volume_app.command("rm")
def volume_rm(seq: int = typer.Argument(..., help="卷序号")) -> None:
    """删除卷。"""
    with _open_db() as db:
        n = db.remove_volume(seq)
    console.print(f"[green]✓ 已删除第 {seq} 卷[/green]" if n
                  else f"[yellow]未找到第 {seq} 卷[/yellow]")


# ---------------------------------------------------------------------------
# 章
# ---------------------------------------------------------------------------
chapter_app = typer.Typer(help="章管理", no_args_is_help=True)
app.add_typer(chapter_app, name="chapter")


@chapter_app.command("add")
def chapter_add(
    title: str = typer.Option(..., "--title", help="章标题"),
    seq: int = typer.Option(1, "--seq", help="章序号（全书唯一）"),
    volume_seq: int = typer.Option(1, "--volume-seq", help="所属卷序号"),
    summary: str = typer.Option("", "--summary", help="章梗概"),
    word_count: int = typer.Option(0, "--word-count", help="字数"),
    status: str = typer.Option("草稿", "--status", help="草稿/已改/定稿"),
) -> None:
    """新增章。"""
    with _open_db() as db:
        db.add_chapter(Chapter(
            title=title, seq=seq, volume_seq=volume_seq, summary=summary,
            word_count=word_count, status=status))
    console.print(f"[green]✓ 已添加第 {seq} 章：{title}[/green]")


@chapter_app.command("list")
def chapter_list() -> None:
    """列出全部章。"""
    with _open_db() as db:
        chapters = db.list_chapters()
    if not chapters:
        console.print("[yellow]暂无章[/yellow]")
        return
    _print_table(
        "章", ["章序", "卷", "标题", "字数", "状态", "梗概"],
        [[c.seq, c.volume_seq, c.title, c.word_count, c.status, c.summary]
         for c in chapters])


@chapter_app.command("wordcount")
def chapter_wordcount(
    seq: int = typer.Argument(..., help="章序号"),
    word_count: int = typer.Argument(..., help="新字数"),
) -> None:
    """更新某章字数。"""
    with _open_db() as db:
        n = db.set_chapter_word_count(seq, word_count)
    console.print(f"[green]✓ 已更新第 {seq} 章字数为 {word_count}[/green]" if n
                  else f"[yellow]未找到第 {seq} 章[/yellow]")


@chapter_app.command("rm")
def chapter_rm(seq: int = typer.Argument(..., help="章序号")) -> None:
    """删除章。"""
    with _open_db() as db:
        n = db.remove_chapter(seq)
    console.print(f"[green]✓ 已删除第 {seq} 章[/green]" if n
                  else f"[yellow]未找到第 {seq} 章[/yellow]")


# ---------------------------------------------------------------------------
# 场景标签（配比追踪）
# ---------------------------------------------------------------------------
tag_app = typer.Typer(help="场景标签与主线/情感配比", no_args_is_help=True)
app.add_typer(tag_app, name="tag")


@tag_app.command("add")
def tag_add(
    chapter_seq: int = typer.Option(..., "--chapter-seq", help="所属章序号"),
    category: str = typer.Option(..., "--category", help="main=主线 / emotion=情感"),
    subtype: str = typer.Option("", "--subtype", help="情感子类：daily_warmth=日常温情 / adversity_warmth=逆境反压温情"),
    note: str = typer.Option("", "--note", help="标签说明"),
) -> None:
    """给某章打场景标签，用于配比统计。"""
    with _open_db() as db:
        db.add_tag(SceneTag(
            chapter_seq=chapter_seq, category=category,
            subtype=subtype, note=note))
    console.print(f"[green]✓ 已为第 {chapter_seq} 章打标签：{category}[/green]")


@tag_app.command("list")
def tag_list() -> None:
    """列出全部标签。"""
    with _open_db() as db:
        tags = db.list_tags()
    if not tags:
        console.print("[yellow]暂无标签[/yellow]")
        return
    _print_table(
        "场景标签", ["ID", "章序", "分类", "子类", "说明"],
        [[t.id, t.chapter_seq, t.category, t.subtype or "-", t.note]
         for t in tags])


@tag_app.command("ratio")
def tag_ratio() -> None:
    """统计主线:情感配比。"""
    with _open_db() as db:
        ratio = db.tag_ratio()
    main = ratio["main"]
    emotion = ratio["emotion"]
    total = main + emotion
    if total == 0:
        console.print("[yellow]暂无标签，无法统计配比。[/yellow]")
        return
    console.print(f"主线标签：{main}  情感标签：{emotion}  比例 ≈ "
                  f"{main / total:.0%} : {emotion / total:.0%}")
    if ratio["subtypes"]:
        console.print("情感子类分布：")
        for k, v in ratio["subtypes"].items():
            console.print(f"  {k}: {v}")
    target = 4 / 5
    actual = main / total
    if abs(actual - target) < 0.05:
        console.print("[green]✓ 主线占比接近 80%（4:1），符合预设。[/green]")
    else:
        console.print(f"[yellow]提示：主线占比 {actual:.0%}，与目标 4:1 有偏差。[/yellow]")


@tag_app.command("rm")
def tag_rm(tag_id: int = typer.Argument(..., help="标签 ID")) -> None:
    """删除标签。"""
    with _open_db() as db:
        n = db.remove_tag(tag_id)
    console.print(f"[green]✓ 已删除标签 {tag_id}[/green]" if n
                  else f"[yellow]未找到标签 ID：{tag_id}[/yellow]")


# ---------------------------------------------------------------------------
# 设定
# ---------------------------------------------------------------------------
lore_app = typer.Typer(help="世界观/设定库", no_args_is_help=True)
app.add_typer(lore_app, name="lore")


@lore_app.command("add")
def lore_add(
    category: str = typer.Option(..., "--category", help="力量体系/地名/势力/功法/物品/其他"),
    name: str = typer.Option(..., "--name", help="条目名"),
    content: str = typer.Option("", "--content", help="设定内容"),
) -> None:
    """新增设定条目。"""
    with _open_db() as db:
        db.add_lore(LoreEntry(category=category, name=name, content=content))
    console.print(f"[green]✓ 已添加设定：[{category}] {name}[/green]")


@lore_app.command("list")
def lore_list() -> None:
    """列出全部设定。"""
    with _open_db() as db:
        entries = db.list_lore()
    if not entries:
        console.print("[yellow]暂无设定[/yellow]")
        return
    _print_table("设定库", ["ID", "分类", "名称", "内容"],
                 [[e.id, e.category, e.name, e.content] for e in entries])


@lore_app.command("rm")
def lore_rm(lore_id: int = typer.Argument(..., help="设定条目 ID")) -> None:
    """删除设定条目。"""
    with _open_db() as db:
        n = db.remove_lore(lore_id)
    console.print(f"[green]✓ 已删除设定 {lore_id}[/green]" if n
                  else f"[yellow]未找到设定 ID：{lore_id}[/yellow]")


# ---------------------------------------------------------------------------
# 伏笔
# ---------------------------------------------------------------------------
foreshadow_app = typer.Typer(help="伏笔管理", no_args_is_help=True)
app.add_typer(foreshadow_app, name="foreshadow")


@foreshadow_app.command("add")
def foreshadow_add(
    description: str = typer.Option(..., "--description", help="伏笔内容"),
    plant_chapter: str = typer.Option("", "--plant-chapter", help="埋设章节"),
    note: str = typer.Option("", "--note", help="备注"),
) -> None:
    """新增伏笔。"""
    with _open_db() as db:
        db.add_foreshadow(Foreshadow(
            description=description, plant_chapter=plant_chapter, note=note))
    console.print("[green]✓ 已埋设伏笔[/green]")


@foreshadow_app.command("list")
def foreshadow_list() -> None:
    """列出全部伏笔。"""
    with _open_db() as db:
        items = db.list_foreshadows()
    if not items:
        console.print("[yellow]暂无伏笔[/yellow]")
        return
    _print_table(
        "伏笔", ["ID", "内容", "埋设章", "状态", "回收章", "备注"],
        [[f.id, f.description, f.plant_chapter, f.status,
          f.resolve_chapter, f.note] for f in items])


@foreshadow_app.command("resolve")
def foreshadow_resolve(
    fs_id: int = typer.Argument(..., help="伏笔 ID"),
    chapter: str = typer.Option(..., "--chapter", help="回收章节"),
) -> None:
    """标记伏笔已回收。"""
    with _open_db() as db:
        n = db.resolve_foreshadow(fs_id, chapter)
    console.print(f"[green]✓ 伏笔 {fs_id} 已回收于 {chapter}[/green]" if n
                  else f"[yellow]未找到伏笔 ID：{fs_id}[/yellow]")


@foreshadow_app.command("rm")
def foreshadow_rm(fs_id: int = typer.Argument(..., help="伏笔 ID")) -> None:
    """删除伏笔。"""
    with _open_db() as db:
        n = db.remove_foreshadow(fs_id)
    console.print(f"[green]✓ 已删除伏笔 {fs_id}[/green]" if n
                  else f"[yellow]未找到伏笔 ID：{fs_id}[/yellow]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
