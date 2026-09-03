# 动态 / 自适应设计层（UI 场景的动态建议依据）

针对所有 **UI 场景**（scenarios.md 第 1-7 画像），给可执行改进时可参考本层的**动态/自适应**判据。它回答"这套界面够不够现代、够不够会自适应"——Material 3 的核心理念是**界面随上下文自适应**（系统壁纸/明暗/设备），而不是写死的静态配色。非 UI 图像不套本层。

> 动态配色是**建议方向**，不是硬性必改；若产品有强品牌色、或明确要固定品牌形象，可说明"此场景更适合 baseline/品牌 seed 方案"再决定。与通用美学的交叉验证原则一致——不拿动态配色"摁死"设计。

## 一、Material dynamic color（动态配色）

- **是什么**：Material 3 / Material You 的自适应配色系统——颜色不写死，而是从一个 **key color（种子色）** 生成一套 **tonal 调色板**，再映射到 6 组颜色角色（primary/secondary/tertiary/error/neutral/neutral-variant）。
- **种子色来源**：系统壁纸（Android 系统自动取壁纸主色）或**品牌色**（设计师用 Material Theme Builder 用品牌色做 seed）。后者兼顾动态与品牌一致性。
- **HCT 色彩空间**：色相 Hue、色度 Chroma、色调 Tone 三维——保证同色调板内任意两步的感知明暗一致，是生成协调调色板的基础。
- **动态方案（scheme variants）**：同一 seed 可出多套——
  - **baseline（tonal）**：默认，色调柔和，最通用。
  - **monochrome（单色）**：只用灰阶，最克制、最安静。
  - **neutral（中性）**：接近单色，稍带一点色。
  - **tonal spot（色调点缀）**：主色带色、其余近中性，重心稳。
  - **vibrant（活力）**：色度更高、更饱和，有表现力。
- **自适应明暗**：动态方案自动区分 light/dark 两套，随系统 `prefers-color-scheme` 切换，无需手工配色。

## 二、怎么在评审里用（按场景给动态建议）

| 场景 | 推荐的动态方案 | 理由 |
|---|---|---|
| 写作工具 | **neutral / monochrome / tonal** | 沉静、低干扰、适合深色专注 |
| 落地页 | **baseline/tonal**，统一一个强调色并全局锁定 | 传达价值、有记忆点又不花 |
| 仪表盘 | **baseline** | 可读优先，避免高饱和把数据搞乱 |
| 电商 | **baseline/tonal** + 品牌 seed | 品质感、转换导向 |
| 作品集/创意 | **vibrant**（可选） | 有表现力、个性 |
| 内容/编辑 | **neutral** | 排版是主角，色安静 |
| 工具类 App | **baseline** | 稳、清晰、状态可读 |

## 三、自适应明暗（Adaptive Light/Dark）

- **双模式从设计一开始就做**，不交付只有单模式（尤其写作工具、内容类常在深色模式）。
- 用 **design tokens** 一处定义语义色（`--surface`、`--text-primary`、`--accent`），明暗自适应只换 token 值，不逐处硬编码。
- 尊重 `prefers-color-scheme`，默认跟随系统；品牌坚持单模式时才固定。
- **禁纯 `#000000` / 纯 `#ffffff`**：用 off-black / off-white（如 zinc-950 / zinc-50），纯值杀层次。
- 视觉层级在明暗两套下必须**等价**：亮色下 CTA 突出，暗色下也要突出；品牌主色两套都要可识别。

## 四、自适应 / 响应式布局

- **adaptive 而非纯缩放**：不同宽度不是简单放大缩小，而是重新组织（侧栏折叠、多列变单列、卡片重排）。
- 移动端列布局须**显式声明** `≤768px` 的回退，不靠"它会自动好"。
- 动效遵循 `prefers-reduced-motion`，`MOTION_INTENSITY>3` 必须降级为静态（见「动效维度」待补，先引用此原则）。

## 依据与出处

- **语料支撑（Material 官方一手）**：dynamic color（key color、tonal palette、6 角色、scheme variants baseline/monochrome/neutral/tonal/vibrant、明暗自适应）、HCT 色彩空间、design tokens、自适应明暗 —— **Material Design 3**（m3.material.io：Color / Dynamic color / Theme）。
- **语料支撑（可访问性）**：非文本组件对比 ≥3:1、`prefers-color-scheme` / `prefers-reduced-motion` 尊重用户偏好 —— **WCAG 2.1** 与 WAI-ARIA 用户偏好。
- **经验值**（语料未逐条覆盖，引用须注明）："写作工具宜 neutral/tonal、作品集宜 vibrant"等**场景→方案映射**为项目评审约定（基于各场景气质推导），非 Material 官方规定。
