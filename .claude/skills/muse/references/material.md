# Material 设计体系（UI 评审尺子）

评审**前端 UI**时，通用美学负责感受/气质，Material 规范负责可执行。遇 UI 界面，交叉验证以下要点（不全套硬套，尊重设计意图）。

## 颜色
- 色彩角色而非裸色：primary / on-primary / primary-container / error / neutral… 主次由角色定义。
- 6 个 tonal 色调板（primary/secondary/tertiary/error/neutral/neutral-variant），各 13 级。
- 对比硬阈值（WCAG）：正文 ≥4.5:1，大字 ≥3:1；非文本组件边界 ≥3:1。

## 排版（Typography scale）
- 15 种字型：display/headline/title/body/label × large/medium/small。
- 字号/字重/行高成体系，层级由 scale 表达，不靠随意取数。

## 间距
- **4dp 栅格 / 8dp 基准**，density 控制紧凑。间距取 4 的整数倍。
- 间距表达分组与优先级：不同优先级元素用不同间距是**有意的差异化**，不是不一致。

## Elevation / 状态
- 5 级 elevation（0-5）：阴影 + surface tint 表达层级。
- 组件状态：enabled / hovered / focused / pressed / dragged / disabled，统一视觉（focus 用焦点环）。

## 一致性
- 用 design tokens（`{group}-{property}-{variant}-{state}`）一处定义、全局复用，而非每处硬编码。

## 依据与出处
- **语料支撑（官方一手）**：m3.material.io（Design tokens / Color / Typography / Shape / Motion / Elevation / States）。
- 交叉验证时注意：Material 是 Google 范式，遇到非 Material 风格（极简、中式、艺术类）只作参考维度，不当作裁决。