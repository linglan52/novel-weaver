# 纲维 novel-weaver

面向长篇网文写作者的**结构管理 + AI 一致性助手**。它不替你写文，而是解决长篇小说最疼的三个问题：人物关系乱、伏笔漏、主线情感比例失控。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![version](https://img.shields.io/badge/version-0.1.0-lightgrey)](pyproject.toml)

## 为什么做这个

长篇写作最大的成本不在「写」，而在「记」与「控」：

- 上百个人物，关系随时间变化，写着写着就崩了；
- 伏笔埋了几十章，回收时找不到出处；
- 想控制「主线 : 情感 = 4 : 1」的节奏，却只能凭感觉。

本项目把这些隐性成本结构化、数据化，让写作者把注意力还给创作本身。它的设计源自一个 250 万字 / 6 卷长篇的实际写作场景。

## 核心功能

| 模块 | 说明 | 状态 |
|---|---|---|
| 人物关系图谱 | 人物节点 + 有向关系边（类型、亲疏强度、起止章节），可可视化 | ✅ 数据层就绪，图谱可视化规划中 |
| 卷章与大纲 | 卷→章二级结构，字数统计、进度追踪 | ✅ 已实现 |
| 配比追踪 | 给场景打标签（主线/情感），自动统计比例并预警失衡 | ✅ 已实现 |
| 设定世界观库 | 力量体系、地名、势力、功法等条目化管理 | ✅ 已实现 |
| 伏笔管理 | 埋设—回收状态机，列出「已埋未收」清单 | ✅ 已实现 |
| AI 一致性助手 | 调 LLM 校验人物设定一致性、提示情节矛盾 | 🚧 规划中 |

## 快速开始

要求 Python 3.10+。

```bash
# 1. 安装
pip install -e .

# 2. 初始化数据库
novel-weaver init

# 3. 录入一个主角
novel-weaver character add --name "林砚" --role "主角" --description "沧澜书院外门弟子"

# 4. 给一章打标签（追踪配比）
novel-weaver tag add --chapter-seq 1 --category main --note "主线：下山试炼"

# 5. 查看配比与概览
novel-weaver tag ratio
novel-weaver status
```

## CLI 用法

顶层命令 `novel-weaver --help` 查看全部子命令。子命令分组如下：

| 命令 | 作用 | 示例 |
|---|---|---|
| `init` | 初始化数据库 | `novel-weaver init` |
| `status` | 数据概览 | `novel-weaver status` |
| `character add/list/rm` | 人物管理 | `novel-weaver character list` |
| `relationship add/list/rm` | 人物关系 | `novel-weaver relationship add --from 甲 --to 乙 --type 师徒` |
| `volume add/list/rm` | 卷管理 | `novel-weaver volume add --title 沧澜启澜 --seq 1` |
| `chapter add/list/wordcount/rm` | 章管理 | `novel-weaver chapter add --title 第一章 --seq 1` |
| `tag add/list/ratio/rm` | 配比追踪 | `novel-weaver tag ratio` |
| `lore add/list/rm` | 设定库 | `novel-weaver lore add --category 力量体系 --name 灵海` |
| `foreshadow add/list/resolve/rm` | 伏笔管理 | `novel-weaver foreshadow resolve 1 --chapter 第88章` |

## 数据存储

- 数据存放在 SQLite 单文件，默认路径 `~/.novel_weaver/novel.db`。
- 通过环境变量 `NOVEL_WEAVER_HOME` 可切换数据目录，便于管理多个写作项目：

```bash
# 不同项目各自一个数据库
NOVEL_WEAVER_HOME=~/novels/book1 novel-weaver init
NOVEL_WEAVER_HOME=~/novels/book2 novel-weaver init
```

- 备份即复制该 `.db` 文件。

## AI 一致性助手（规划中）

计划接入可插拔的 LLM provider（本地 Ollama / OpenAI 兼容接口），实现：

- 人物设定一致性校验（口吻、能力、立场是否前后漂移）；
- 情节矛盾提示（时间线、已回收伏笔是否被误用）。

## 目录结构

```
novel-weaver/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/novel_weaver/
│   ├── cli.py              # Typer 入口
│   ├── config.py           # 路径与配置
│   ├── db.py               # SQLite 连接与 CRUD
│   ├── models.py           # dataclass 数据模型
│   ├── services/           # 业务逻辑（图谱/配比/AI）
│   └── web/                # Streamlit 面板（规划中）
├── tests/
├── examples/               # 示例数据与命令
└── docs/
```

## Roadmap

- [x] 数据层与 CLI 增删改查
- [x] 主线/情感配比追踪
- [x] 单元测试（pytest，覆盖 CRUD 与配比统计）
- [x] GitHub Actions CI（多 Python 版本）
- [ ] 人物关系图谱可视化（networkx + plotly）
- [ ] AI 一致性助手（Ollama / OpenAI 兼容）
- [ ] Streamlit Web 面板

## 贡献

欢迎提 issue 与 PR，建议先开 issue 讨论改动方向。

本地开发：

```bash
pip install -e ".[dev]"
pytest -q
```

## 许可证

[MIT](LICENSE) © 2026 Zhang Gulei

---

> 部分代码由 AI 辅助生成。
