# CampusMind 前端问题日志

> 本文档记录开发过程中遇到的关键问题及其根因分析、解决方案和经验教训。

---

## 问题 1：Design Token CSS 未被业务 App 加载

### 问题描述

Phase 1 实现完成后，启动 `npm run dev`，页面渲染出现严重问题：

- Sidebar 背景变为透明（glassmorphism 效果消失）
- 所有 CSS 变量（`--glass-surface`、`--color-bg-base` 等）不生效
- Card 组件部分样式异常

### 根因分析

**业务 App 入口 (`src/main.tsx`) 与 Playground 入口 (`src/playground/main.tsx`) 的 CSS 导入不一致。**

`playground/main.tsx` 正确导入了所有 design token：
```tsx
import '../styles/tokens/colors.css'
import '../styles/tokens/spacing.css'
import '../styles/tokens/typography.css'
import '../styles/tokens/elevation.css'
```

但业务 app 的 `main.tsx` 只导入了 `./index.css`：
```tsx
import './index.css'
```

这导致 `--glass-blur`、`--glass-surface`、`--color-bg-base` 等 CSS 变量在整个业务 app 中均未定义（浏览器解析为无效值）。

### 解决方案

在 `src/main.tsx` 中补齐 design token 的导入：

```tsx
import './index.css'
import './styles/tokens/colors.css'
import './styles/tokens/spacing.css'
import './styles/tokens/typography.css'
import './styles/tokens/elevation.css'
```

### 经验教训

- 多入口项目（business app + playground）应确保 CSS 变量导入策略一致
- 建议后续考虑在 `index.css` 中统一使用 `@import` 汇总所有 token 文件，避免遗漏
- 设计系统文档应明确说明 token CSS 的导入方式

---

## 问题 2：CSS 变量命名不符合设计系统规范

### 问题描述

Phase 1 初次实现时，使用了不存在的 CSS 变量名：

```tsx
// 错误用法
style={{ fontSize: 'var(--font-size-xl)' }}      // 应为 --text-xl
style={{ padding: 'var(--spacing-xl)' }}           // 应为 --space-8
style={{ borderRadius: '12px' }}                  // 应为 var(--radius-lg)
```

这些变量在设计系统中不存在，导致样式使用默认值（部分回退到浏览器默认样式）。

### 根因分析

实现者未在动手前仔细阅读设计文档（`docs/styles/` 下的规范），凭直觉使用了不符合命名规范的变量名。

设计系统明确的命名规范：

| 类别 | 变量模式 | 示例 |
|------|---------|------|
| 字号 | `--text-{size}` | `--text-xl`, `--text-sm` |
| 间距 | `--space-{n}` | `--space-1` (4px), `--space-8` (32px) |
| 圆角 | `--radius-{size}` | `--radius-md` (8px), `--radius-lg` (12px) |

### 解决方案

1. 重新阅读 `docs/styles/01-DESIGN_TOKENS_REFERENCE.md` 确认正确变量名
2. 将所有内联样式中的 CSS 变量替换为正确命名
3. 新增全局 CSS 类（如 `.layout-main`、`.placeholder-page`）避免后续内联样式问题

### 经验教训

- **必须先读文档，再动手**。设计文档详细规定了所有变量名和用法
- 文档路径：`frontend/docs/styles/` 下有完整的设计系统说明
- Playground (`npm run playground`) 可实时预览设计系统组件效果

---

## 问题 3：未复用已有 UI 组件

### 问题描述

初次实现的 LoginPage 使用了自行编写的 CSS 样式丑，而设计系统中已有 `Card` 组件（包含 `variant="auth"` 暖色渐变边框样式）可直接复用。

### 根因分析

实现者未先了解 `src/components/ui/` 下已有组件的功能和样式，直接从零编写。

已有的 UI 组件（均已包含完整 CSS）：

| 组件 | 已有样式 |
|------|---------|
| `Button` | primary/ghost/link 三种 variant，hover lift 效果 |
| `Input` | inset shadow focus 效果，error 状态 |
| `Card` | default/elevated/glass/auth 四种 variant |
| `Badge` | pill-shaped，muted colors |
| `Chip` | 标签样式 |

### 解决方案

使用 `Card variant="auth"` 替代自行编写的表单容器：

```tsx
<Card variant="auth" padding="lg">
  <CardBody>
    <h1 className="login-title">Sign In</h1>
    <form>
      <Input label="Username" ... />
      <Input label="Password" ... />
      <Button type="submit" fullWidth>Sign In</Button>
    </form>
  </CardBody>
</Card>
```

### 经验教训

- **动手前先探索代码库**，了解已有组件能力
- Playground (`npm run playground`) 可预览所有已有组件的实际效果
- 遵循 "Component Checklist"（设计系统文档第 6 节）确保复用而非重复造轮子

---

## 问题 4：未使用 frontend-design skill 的设计指导

### 问题描述

用户多次提到 "感觉更不协调"、"需要使用 /frontend-design skill"，但实现者未遵循该 skill 的工作流程，未进行 DFII 评分、明确美学方向等工作。

### 根因分析

- 未在实现前调用 `/frontend-design` skill 获取设计指导
- 未遵循 brainstorming → writing-plans → implementation 的标准流程
- 凭直觉进行样式调整，导致多次返工

### 解决方案

后续开发应遵循以下流程：

1. 调用 `superpowers:brainstorming` 明确设计方向
2. 使用 `superpowers:writing-plans` 创建实现计划
3. 调用 `frontend-design` skill 获取设计指导（DFII 评分、变量确认）
4. 才进入具体实现

### 经验教训

- **Skills 是工具，不是可选附件**。遇到 UI 相关任务必须先调用对应 skill
- 设计文档（`docs/styles/`）和 Playground 是最权威的参考，不是"参考之一"

---

## 问题 5：测试环境内存溢出 (OOM)

### 问题描述

运行全部测试时 Node.js 堆内存耗尽，Vitest 报错：
```
FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory
```

### 根因分析

Vitest 默认使用多个 worker 并行执行测试，内存使用量很大。全部测试同时运行时导致系统内存耗尽。

### 解决方案

1. **分批运行测试**：将测试分成多个批次执行
2. **增加 Node 内存限制**：
   ```bash
   NODE_OPTIONS="--max-old-space-size=4096" npm run test:run
   ```
3. **在 `package.json` 中添加测试脚本**：
   ```json
   {
     "scripts": {
       "test:run": "NODE_OPTIONS='--max-old-space-size=4096' vitest run"
     }
   }
   ```

### 经验教训

- 长时间运行的测试套件应考虑内存限制
- 大型测试套件应分批执行或使用 CI/CD 环境

---

## 问题 6：React Testing Library 查询不准确

### 问题描述

编写测试时遇到以下问题：

1. `Card` 测试：使用 `screen.getByText('Content').parentElement` 获取 card 元素不准确
2. `LoginPage` 测试：有多个 "Sign In" 元素（标题和按钮），导致 `getByText` 报错
3. `ToolEventCard` 和 `KnowledgeSelector`：状态更新未包装在 `act()` 中，导致 warning

### 解决方案

1. **使用 `document.querySelector()` 直接查询 CSS 类**：
   ```typescript
   // 错误
   expect(screen.getByText('Content').parentElement).toHaveClass('card')
   // 正确
   expect(document.querySelector('.card')).toHaveClass('card')
   ```

2. **使用更精确的查询**：
   ```typescript
   // 错误：多个 "Sign In"
   expect(screen.getByText('Sign In')).toBeInTheDocument()
   // 正确：指定按钮
   expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument()
   ```

3. **使用 `act()` 包装状态更新**：
   ```typescript
   await act(async () => {
     header?.click()
   })
   ```

### 经验教训

- React Testing Library 查询应尽量精确（使用 role、label）
- 状态更新必须用 `act()` 包装以避免 warning
- 直接查询 DOM 元素比依赖 parentElement 更可靠

---

## 总结

| 问题 | 严重程度 | 根因 | 预防措施 |
|------|---------|------|---------|
| Design Token 未加载 | 高 | 多入口 CSS 导入不一致 | 统一 CSS 导入策略 |
| CSS 变量命名错误 | 中 | 未读文档 | 先读 `docs/styles/` |
| 未复用 UI 组件 | 中 | 未探索代码库 | 先了解已有组件 |
| 未用 frontend-design skill | 高 | 流程缺失 | 遵循 skill 工作流 |
| 测试内存溢出 | 中 | 并行执行内存过大 | 增加内存或分批执行 |
| RTL 查询不准确 | 低 | 查询方式不当 | 使用精确查询和 act() |

---

## 问题 7：CSS 类名不匹配导致输入框样式失效

### 问题描述

输入框宽度过短（244px）、高度太小、不居中、白色长条不协调。

### 根因分析

JSX 中使用的类名是 `.chat-input-wrapper`，但 CSS 中定义的是 `.input-wrapper`，导致所有关键样式失效。

### 解决方案

将 CSS 选择器改为 `.chat-input-wrapper`，与 JSX 保持一致。

---

## 问题 8：输入框在有消息时被遮盖

### 问题描述

空状态时输入框正常显示，但发送消息后输入框被消息列表向上推挤出视口。

### 根因分析

- `.layout-main` 缺少 `height: 100vh` 和 `overflow: hidden`
- `.chat-page` 缺少 `overflow: hidden`

### 解决方案

添加 `overflow: hidden` 和固定高度，使输入框始终固定在视口底部。

---

## 问题 9：工具事件显示为独立卡片，无法折叠

### 问题描述

每个工具事件都渲染为独立的 ToolEventCard，占用空间大，需要逐个展开/收起。

### 根因分析

MessageBubble 直接渲染 message.events 数组中的每个 ToolEventCard，没有聚合组件。

### 解决方案

创建 ToolGroup 组件聚合所有工具事件，支持折叠/展开。

---

## 问题 10：工具状态始终显示 "进行中"

### 问题描述

即使工具执行完毕，状态仍显示为 "进行中"，没有正确更新。

### 根因分析

工具事件被存入全局 toolEvents[]，但助手消息的 events[] 始终为空。

### 解决方案

在 addToolEvent 中同时更新最后一条助手消息的 events 数组。

---

## 问题 11：用户消息气泡宽度占据整行

### 问题描述

用户消息的文字很短，但气泡占据整行宽度，下方有大片空白。

### 根因分析

`.message-content` 设置了 `width: 100%`，导致气泡始终占满可用宽度。

### 解决方案

用户消息使用 `width: fit-content`，助手消息保持 `width: 100%`。

---

## 问题 12：CSS 变量命名不一致导致样式错误

### 问题描述

CSS 中使用了 `--bg-card`、`--border`、`--shadow` 等变量，但部分变量未正确定义。

### 根因分析

设计模板中的变量名与实际设计系统不完全一致。

### 解决方案

统一使用设计系统中已正确定义的变量名。

---

## 问题 13：API 传入 user_id 存在安全隐患

### 问题描述

Phase 3 实现中，前端从 sessionStorage 获取 user_id 并传入 `GET /api/v1/users/{user_id}/knowledge` 接口。

### 根因分析

用户可以篡改请求，访问其他用户的知识库。正确的做法是后端从 JWT token 自动提取用户身份。

### 解决方案

后端 API 已重构为 `GET /api/v1/knowledge`，前端修改：
- 移除 `fetchKnowledgeBases(userId)` 的 `userId` 参数
- 调用 `fetchKnowledgeBases()` 无参数
- 移除 sessionStorage 获取 user_id 的逻辑

### 教训

- 前端不应传递 user_id，后端应从 token 解析
- API 安全性应由后端保证

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-03-23 | 1.3.1 | 修复 API 安全隐患，前端不再传入 user_id |
| 2026-03-23 | 1.3.0 | 完成 Phase 3 知识库浏览功能 |
| 2026-03-22 | 1.2.0 | 添加 Phase 3 样式重设计，记录问题 7-12 |
| 2026-03-22 | 1.1.0 | 添加 Phase 2.5 测试相关内容，记录测试问题 5、6 |
| 2026-03-21 | 1.0.0 | 初始版本，记录 Phase 1 开发中的 4 个关键问题 |
