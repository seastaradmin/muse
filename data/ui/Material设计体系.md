---
title: Material 设计体系
category: system
domain: UI
related: [间距系统, 字体层级, 组件状态, 设计语言一致性]
source: 手工精编（依据 Material 3 官方规范 m3.material.io）
---

# 定义

Material Design 是 Google 官方的开源 UI 设计体系（"Google's open-source UI system"）。Material 3 是其当前版本，以 **design tokens、色彩 tonal 体系、typography scale、8dp 间距、elevation、组件状态**为一套可执行规范。它是前端 UI 评审的"体系尺子"——通用美学管气质，Material 管规范与可执行。

# 核心要点

- **Design tokens**：命名 `{group}-{property}-{variant}-{state}`（如 `md.sys.color.primary`、`md.sys.typescale.body-large`），分 color/typography/shape/motion/state 五类。用 token 而非裸值，一处定义全局复用。
- **色彩 tonal 体系**：6 个色调板（primary/secondary/tertiary/error/neutral/neutral-variant），每个 13 级 tonal scale（由 seed 色生成），映射到**色彩角色**（primary、on-primary、primary-container、on-primary-container…）。支持 dynamic color（从壁纸取色生成主题）。
- **Typography scale**：15 种字型（display/headline/title/body/label 各 large/medium/small），默认 Roboto。字号、字重、行高成体系，层级清晰。
- **间距**：**4dp 栅格 / 8dp 基准**。所有间距取 4 的整数倍，用 density 控制紧凑度。
- **Elevation**：5 级（0-5），用**阴影 + surface tint（表面色调叠加）**共同表达层级，而不是只靠投影。
- **组件状态**：每个组件定义 enabled、hovered、focused、pressed、dragged、disabled 等状态，有统一的状态视觉（如 focus 用焦点环）。
- **Theme Builder**：从品牌色/种子色一键生成可访问的亮暗色主题 + type theme，导出 design tokens 到代码（web 工具 + Figma 插件）。

# 适用范围

- **前端 UI**：任何用 Google 设计范式或想对齐主流 Web/Android 设计的产品。
- 组件库 / 设计系统：以 Material 的 token 与组件为基准。

# 常见误区

- 只搬 Material 组件外观，不跟它的 token 与状态体系，导致"形似神不似"。
- 把 Material 当唯一尺子硬套到非 Material 风格（极简、中式、艺术类）——体系是交叉验证的一维，不是裁决。
- 忽略 8dp/4dp 间距基准和 tonal 色彩角色，随意取数值。
- 只做亮色主题，忽略暗色与动态色彩的可访问性。

# 依据与出处

- **语料支撑（官方一手）**：Material 3 规范 —— design.google/about 确认 "Material Design, Google's open-source UI system"；规范正文见 https://m3.material.io/（Design tokens、Color、Typography、Shape、Motion、Elevation、States 章节）；Theme Builder https://m3.material.io/theme-builder；Material Web 组件库 https://material-web.dev/。注：规范页为 JS 渲染，本卡为基于官方规范的精编，非页面原文摘录。
- 可交叉引用：W3C Design Tokens (DTCG) 标准 https://www.w3.org/community/design-tokens/。
