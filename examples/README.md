# 示例数据

以下示例演示如何用 CLI 录入一个最小可用的写作世界（人名与设定均为虚构示例，不含任何真实作品内容）。

## 1. 初始化

```bash
NOVEL_WEAVER_HOME=./examples/_data novel-weaver init
```

## 2. 录入人物

```bash
export NOVEL_WEAVER_HOME=./examples/_data

novel-weaver character add --name "林砚" --role "主角" --description "沧澜书院外门弟子，身怀残缺灵海"
novel-weaver character add --name "沈青璃" --role "主角" --description "书院剑道首席，冷面热心"
novel-weaver character add --name "顾玄" --role "反派" --description "天澜阁少阁主"
```

## 3. 录入关系

```bash
novel-weaver relationship add --from 林砚 --to 沈青璃 --type 恋人 --strength 4 --start 第12章
novel-weaver relationship add --from 顾玄 --to 林砚 --type 敌对 --strength 2 --start 第8章
```

## 4. 录入卷章

```bash
novel-weaver volume add --title "沧澜启澜" --seq 1 --summary "主角入书院，灵海觉醒"
novel-weaver chapter add --title "外门试炼" --seq 1 --volume-seq 1 --word-count 3600 --status 定稿
```

## 5. 打标签（配比追踪）

```bash
novel-weaver tag add --chapter-seq 1 --category main --note "主线：试炼夺魁"
novel-weaver tag add --chapter-seq 1 --category emotion --subtype daily_warmth --note "日常温情：沈青璃送药"
novel-weaver tag add --chapter-seq 1 --category emotion --subtype adversity_warmth --note "逆境反压温情：灵海反噬时相扶"

novel-weaver tag ratio
```

## 6. 设定与伏笔

```bash
novel-weaver lore add --category 力量体系 --name "灵海" --content "修士炼气之根基，分九品"
novel-weaver foreshadow add --description "林砚的灵海为何残缺" --plant-chapter 第1章
```

示例数据目录 `_data/` 已加入 `.gitignore`，不会被提交。
