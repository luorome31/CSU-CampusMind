# 🌟 AI Agent 跨端设计系统复用模板 (Design System Template)

此模板提取自优雅的“温柔文具 (Gentle Stationery)”设计风格，为你开发的任何新型 AI Agent 项目提供一套经过验证的、具备高度统一性与呼吸感的设计基因。

---

## 🎨 1. 核心视觉基因与色彩配置 (Color Palette)

系统包含多套色彩主题（如 `absolutely`, `contemplation`, `deep-think`, `midnight` 等），为了带来最舒适、最低眼压的阅读体验，这里提取 **Warm Paper (暖纸)** 作为**默认主题配置**。

### 核心理念：
*   **低对比度和谐 (Low-Contrast Harmony)**：告别刺眼的纯白（`#FFFFFF`）和死黑（`#000000`），采用柔和的纸张底色和灰阶文字。
*   **触感深度 (Tactile Depth)**：使用高透明度的弥散阴影，以及低对比度的极细边框，界面层级清晰又不生硬。

### 💡 CSS Variables / Global CSS 模板

```css
/* global.css (基于 Warm Paper) */
:root {
  /* 基础背景层级 */
  --bg:           #F8F5ED;  /* App 整体底色 */
  --bg-card:      #FCFAF5;  /* 卡片、对话气泡、弹出层底色 */
  --bg-glass:     rgba(250, 248, 242, 0.92); /* 毛玻璃/头部遮罩底色 */

  /* 主题色/品牌色 */
  --accent:       #537D96;
  --accent-hover: #456A80;
  --accent-light: rgba(83, 125, 150, 0.08);

  /* 文字颜色层级 */
  --text:         #3B3D3F;  /* 正文高对比度文字 */
  --text-light:   #6B6F73;  /* 辅助文字/副标题 */
  --text-muted:   #8E9196;  /* 提示文本、时间戳、禁用状态 */

  /* 结构色 */
  --border:       rgba(83, 125, 150, 0.22); /* 全局统一细边框 */
  --shadow:       rgba(59, 61, 63, 0.09);   /* 弥散阴影 */

  /* 状态层级 */
  --green:        #7BAE7F;  /* 成功状态 */
  --coral:        #EC8F8D;  /* 醒目/警告/红色系提示 */

  /* 业务强相关语义色 */
  --sidebar-bg:   #F4F2EA; /* 侧边栏专属稍微暗一点的背景，区分内容区 */
  --user-bg:      rgba(83, 125, 150, 0.08); /* 用户消息气泡背景（采用主题色的浅透明度） */
  --tool-bg:      rgba(83, 125, 150, 0.06); /* AI思考/工具调用气泡底色 */
  --tool-text:    #6B6F73;
}
```

---

## 📏 2. 布局、排版与交互规则 (Layout, Typography & Interaction)

### 2.1 圆角与阴影体系
在全局基础 CSS 中设定以下标准（可通过 CSS Variables 统一管理）：
*   **大板块/弹窗 (Modal/Sidebar)**: `--radius-lg: 16px;`。
*   **卡片/消息气泡 (Card/Bubble)**: `--radius-md: 10px;` 或 `12px`，保证内容块之间的独立感，但是不会过于圆滑显得幼小。
*   **小按钮/Tag (Button/Tag)**: `--radius-sm: 6px;` 配合微小的阴影。
*   **阴影 (Shadows)**: 弃用生硬的重阴影，采用环境弥散投影 `box-shadow: 0 4px 24px var(--shadow);`。

### 2.2 动画过渡弹簧曲线 (Fluid & Springy)
所有的交互动画（展开折叠、Hover状态等）应抛弃线性的 `ease-in`。推荐全局物理弹簧曲线：
```css
/* 全局默认动画曲线 */
--ease-spring: cubic-bezier(0.16, 1, 0.3, 1);
--duration-base: 300ms;
```

### 2.3 核心布局框架 (响应式)
典型的三列跨端布局设计：左侧栏 (Session) + 主工作区 (Chat) + 右侧挂载区 (Context/Preview)。
*   **桌面端 (`>= 768px`)**：左侧边栏默认 `240px`宽度 (`--sidebar-width`)，右侧预览窗宽 `580px` (`--preview-panel-width`)。
*   **动态收缩规则**：当主聊天区宽度挤压至 `< 400px` (`CHAT_MIN_WIDTH`) 时，系统应当**自动折叠**侧栏（先折叠扩展的右侧，再折叠左侧）。
*   **移动端 (`< 768px`)**：侧栏变为抽屉式 (Drawer) 并呼出底部 TabBar，点击空白处自动收起。

---

## 🧩 3. 核心组件样式与结构提取 (Components Deep Dive)

### 3.1 侧边栏条目 (Sidebar Session List)
*   **设计要点**：干净的悬浮高亮、两端对齐、附加上下文信息与大模型专属徽章 (Badge)。
*   **交互**：Hover 时背景变为类似 `--overlay-subtle: rgba(0,0,0,0.03)` 的轻微反馈。
```css
/* CSS */
.session-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  transition: background-color var(--ease-spring) 0.2s;
  cursor: pointer;
  border: none;
  background: transparent;
}
.session-item:hover {
  background-color: var(--overlay-light, rgba(0,0,0,0.05));
}
.session-item:active {
  background-color: var(--overlay-medium, rgba(0,0,0,0.08));
}
.session-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}
.session-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.session-item-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.session-item-meta {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

```tsx
// React 结构参考
<button className="session-item">
  <div className="session-item-content">
    <div className="session-item-header">
      {/* 活跃指示器或思考中小圆点 */}
      {isStreaming && <span className="streaming-dot" />}
      <span className="session-item-title">对话标题示例</span>
    </div>
    <div className="session-item-meta">
      Agent模型名 · 10分钟前
    </div>
  </div>
  {/* 菜单、网页悬浮标记等小图标 */}
</button>
```

### 3.2 对话展示区 (Chat Bubbles)
*   **User Message (用户)**: 极简流线型。靠右或靠左均可，但背景使用强调色的 8% 透明度 `--user-bg: rgba(83,125,150,0.08)`，无边框。携带附件时，附件以单独的卡片形式吸附在气泡上方。
*   **Agent Message (模型)**: 白底或透明底（由外层布局决定），左侧紧贴头像。
*   **Thinking Block (思考过程 / 折叠面板)**:
    这是 AI Agent 产品区别于传统对话极其关键的一环，用于隐藏长篇幅 CoT（思维链）。
*   **Tool Group (工具调用)**: 
    支持多工具调用的汇总（类似：✓ 已完成 3 个工具执行）。

```tsx
// 思考过程组件 (Thinking Block) 结构与 CSS 概要
/* CSS */
.thinking-block {
  margin: 8px 0;
  border-left: 2px solid var(--border); /* 左侧极简划线指示层级 */
  padding-left: 12px;
}
.thinking-block-summary {
  cursor: pointer;
  color: var(--text-muted);
  font-size: 0.85rem;
  user-select: none;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.2s;
}
.thinking-block-summary:hover {
  color: var(--text);
}
.thinking-block-body {
  color: var(--text-light);
  font-size: 0.9rem;
  margin-top: 6px;
  /* 运用灰阶色彩削弱视觉优先级，凸显最终回答 */
}
```

```tsx
// 工具调用组件 (Tool Group Block) 交互逻辑
// 运行中显示 "Running 2 tools..." 以及波浪跳动的三点动画
// 运行完毕折叠显示 "✓ 4 tools executed"，点击展开具体参数与返回状态
export const ToolGroup = ({ tools }) => {
  const allDone = tools.every(t => t.done);
  return (
    <div className="bg-[var(--tool-bg)] rounded-md border border-[var(--border)] p-2 my-2 text-sm">
      <div className="text-[var(--text-light)] flex items-center gap-2">
        {allDone ? '✓ 执行完成' : <LoadingDots />}
      </div>
      {/* 被折叠的具体列表 */}
    </div>
  )
}
```

### 3.3 输入交互区 (Input Area & Toolbar)
不仅仅是一个居中的 text input，当代 Agent 输入框通常是一个功能极其丰富的**操作台 (Command Center)**。

*   **布局**：整体在底部绝对居中悬浮或固定，采用类似内凹陷框或者是稍微突起的带阴影悬浮卡片。
*   **自动高度扩容**：`textarea` 根据输入换行自动撑高（限制 `max-height: 120px` 左右），避免挡住过多视线。
*   **顶部/附件挂载区 (Top Bar)**：
    输入框顶部可动态挂载 **To-Do 进度提示**以及用户拖拽进来的**附件标签**。
*   **底部操作栏 (Bottom Bar)**：
    包含：Plan Mode(规划模式开关)、Doc Context(文档上下文开关)、模型切换器 (Model Selector)。
*   **核心特性 (上下文使用率环 Context Ring)**：
    这是一个绝妙的提示器，右侧放置一个小小的环形 SVG 进度条，根据已用 Token 计算当前会话的上下文容量，指导用户何时应该 `compact` 清理上下文。

```tsx
// 输入框底部操作栏的 CSS 示例提取
.input-wrapper {
  background: var(--bg-card);
  border: 1px solid var(--border);
  box-shadow: 0 4px 16px var(--shadow);
  border-radius: 16px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: all var(--ease-spring) 0.3s;
}

.input-bottom-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.context-ring {
  width: 24px;
  height: 24px;
  /* 配合 SVG 动态 stroke-dashoffset 呈现环形进度 */
}
```

### 3.4 全局/附加界面块 (Settings & Modals)
*   **卡片风格弹窗 (Confirm Cards/Settings)**: 不要做占据全屏的庞大弹窗，使用固定宽度中等弹窗 (例：maxWidth: 480px)。
*   **移动设备**：当宽度 `< 640px`，弹窗自动降级为自下而上的抽屉底端表单 (Bottom-sheet Drawer)，顶部附带一个视觉把手 (grip) 暗示可向下滑动关闭。

---

## 🚀 4. 在新项目中快速使用 (Quick Start Guide)

将以下基础配置复制到你全新的项目中，作为 `global.css` 快速铺设底层。

**1. 全局 CSS 基础注入 (global.css)**:
```css
:root {
  /* 基础背景层级 */
  --bg:           #F8F5ED;
  --bg-card:      #FCFAF5;
  --bg-glass:     rgba(250, 248, 242, 0.92);

  /* 主题与状态色 */
  --accent:       #537D96;
  --accent-hover: #456A80;
  --text:         #3B3D3F;
  --text-muted:   #8E9196;
  --border:       rgba(83, 125, 150, 0.22);
  --shadow:       rgba(59, 61, 63, 0.09);

  /* 圆角大小 */
  --radius-sm:    6px;
  --radius-md:    10px;
  --radius-lg:    16px;

  /* 动画曲线与阴影 */
  --ease-spring:  cubic-bezier(0.16, 1, 0.3, 1);
  --shadow-glass: 0 8px 32px var(--shadow);
  
  /* 字体族 */
  --font-ui:      "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  --font-serif:   "Songti SC", "Georgia", serif;
}

body {
  background-color: var(--bg);
  color: var(--text);
  font-family: var(--font-ui);
  margin: 0;
  padding: 0;
}
```

**2. 预设 Prompt 面向 AI 生成 UI 的指南 (系统指令)**
你可以将此挂载给帮你写 UI 的大模型，确保设计系统不偏离：
> *风格设定：你需要构建一个温柔的、如同手抄本文具般 (Gentle Stationery) 交互的 AI 页面。所有样式使用纯 CSS 编写，不依赖 Utility Classes 框架。避免生硬的纯黑纯白，背景色使用 `var(--bg)`，卡片底色使用 `var(--bg-card)`，文本色彩使用 `var(--text)` 等全局变量（已在 `:root` 中定义）。卡片圆角采用 `var(--radius-lg)` 并在四周点缀极其轻量的弥散阴影 `var(--shadow-glass)`。所有的悬浮与交互动效必须使用 `transition: all var(--ease-spring) 0.3s`。最后，交互点击区域在移动设备下至少保证高度不小于 `44px` 大小。*
