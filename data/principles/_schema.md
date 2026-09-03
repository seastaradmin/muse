# 条目 Schema —— 通用审美原理层

每条审美原理一个 Markdown 文件。本文件说明字段与小节规范。

## 目录归属（category）

| 子目录 | category | 覆盖 |
|---|---|---|
| `color/` | `color` | 色彩理论、配色、对比 |
| `composition/` | `composition` | 构图、比例、视觉重心 |
| `typography/` | `typography` | 排版、字号、字体 |
| `space/` | `space` | 留白、层级、间距 |

## frontmatter 字段

| 字段 | 必填 | 取值 / 说明 |
|---|---|---|
| `title` | ✅ | 条目名（中文，与文件名一致） |
| `category` | ✅ | 上述子类之一 |
| `domain` | ✅ | `通用` / `UI` / `影视` —— 该原理主要服务于哪个领域 |
| `related` | 可选 | 相关条目名（用于后续知识图关系） |
| `source` | 可选 | 来源（如 Wikipedia、书籍），格式 `名称 (URL)` |

## 正文小节

每条按以下标题组织，便于机器解析与理论面引用：

```
# 定义          —— 一句话/一段话说清它是什么
# 核心要点      —— 用列表给出可执行的要点
# 适用范围      —— 在哪些场景下适用（通用/UI/影视）
# 常见误区      —— 反例或常见错误
# 来源          —— 引用来源
```

## 模板

```markdown
---
title: 条目名
category: color
domain: 通用
related: [相关条目]
source: Wikipedia (https://...)
---

# 定义

# 核心要点

# 适用范围

# 常见误区

# 来源
```
