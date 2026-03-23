# CampusMind 前端进度日志

> 本文档记录前端开发的阶段性进度，包括完成的功能、遇到的问题及解决方案。

---

## 2026-03-21 Phase 1：基础骨架搭建

### 1.1 目标

根据 `docs/ARCHITECTURE.md` 中 Phase 1 的定义，完成以下工作：

- 布局框架（Sidebar + 路由）
- 认证流程（登录页、受保护路由）
- 基础聊天页面（占位符）

### 1.2 完成的功能

#### 依赖安装

| 包 | 版本 | 用途 |
|----|------|------|
| `react-router-dom` | ^6.x | 路由管理 |
| `zustand` | ^5.x | 状态管理 |

#### 文件结构

```
src/
├── api/
│   ├── client.ts          # API 基础客户端（JWT 注入、401 处理）
│   ├── auth.ts            # 认证 API 封装
│   └── types.ts          # User、ApiError、LoginResponse 类型
├── features/
│   ├── auth/
│   │   ├── authStore.ts       # Zustand 认证状态管理
│   │   ├── LoginPage.tsx      # 登录页
│   │   ├── LoginPage.css      # 登录页样式（auth 渐变卡片）
│   │   └── ProtectedRoute.tsx # 受保护路由组件
│   ├── chat/
│   │   ├── ChatPage.tsx       # 聊天页（Phase 2 完整实现）
│   │   └── chatStore.ts       # 聊天状态（Phase 2 完整实现）
│   ├── knowledge/
│   │   └── KnowledgeListPage.tsx  # 知识库列表（Phase 3 完整实现）
│   └── build/
│       └── KnowledgeBuildPage.tsx  # 知识库构建（Phase 4 完整实现）
├── components/
│   └── layout/
│       └── Sidebar/
│           ├── Sidebar.tsx    # 侧边栏导航
│           └── Sidebar.css    # 侧边栏样式（玻璃态效果）
├── App.tsx                  # 根组件（路由 + 认证初始化）
├── routes.tsx               # 路由配置
└── index.css                # 全局重置 + 布局样式
```

#### 路由设计

| 路由 | 组件 | 权限 |
|------|------|------|
| `/` | ChatPage | 公开 |
| `/login` | LoginPage | 公开 |
| `/knowledge` | KnowledgeListPage | 公开 |
| `/knowledge/build` | KnowledgeBuildPage | 需要认证 |
| `/profile` | ProfilePage | 需要认证 |

#### 组件复用

- **LoginPage**：使用 `Card variant="auth"`（暖色渐变边框）+ `CardBody` + `Input` + `Button`
- **Sidebar**：使用 glassmorphism 效果（`--glass-blur` + `--glass-surface`）
- **Placeholder 页面**：统一使用全局 CSS 类 `.placeholder-page`

### 1.3 设计系统对齐

Phase 1 实现过程中发现多处未遵循设计系统规范的实现，已全部修正：

#### CSS 变量命名

| 错误用法 | 正确用法 |
|---------|---------|
| `--font-size-xl` | `--text-xl` |
| `--font-size-lg` | `--text-lg` |
| `--font-size-sm` | `--text-sm` |
| `--spacing-xl` | `--space-8` |
| `--spacing-lg` | `--space-6` |
| `--spacing-md` | `--space-4` |
| `--spacing-sm` | `--space-2` |
| `--spacing-xs` | `--space-1` |

#### 组件复用原则

- 优先复用 `src/components/ui/` 下的组件（Button、Input、Card）
- 避免自行编写与已有组件功能重复的 CSS
- 样式统一使用 CSS 变量，不使用硬编码值

### 1.4 Git 提交记录

| 提交 | 描述 |
|------|------|
| `5017071` | 添加 react-router-dom 和 zustand 依赖 |
| `65f90e6` | 添加 API 层（client、auth、types） |
| `e0a60ec` | 添加认证功能（store、login、受保护路由） |
| `ef90955` | 添加 Sidebar 组件和样式 |
| `f899ca0` + `cb7baac` | 添加路由和占位符页面 |
| `b7eef0c` | 更新 App.tsx（路由 + 认证初始化） |
| `e55e2cf` | 修正 CSS 变量与设计系统对齐 |
| `13014ec` | 添加全局 CSS 重置和布局变量 |
| 修复提交 | 补齐 main.tsx 中缺失的 design token 导入 |

### 1.5 待完成（Phase 2+）

- [ ] SSE 流式聊天
- [ ] 工具调用事件渲染
- [ ] 消息历史加载
- [ ] 知识库 CRUD
- [ ] 爬取/上传/索引工作流
- [ ] 响应式侧边栏收起/展开
- [ ] Token 刷新机制

---

## 2026-03-21 Phase 2：流式聊天

### 2.1 目标

完成 Phase 2 的流式聊天功能：
- SSE 流式输出
- 工具调用事件卡片
- 消息历史加载
- 知识库选择

### 2.2 完成的功能

#### 依赖安装

| 包 | 版本 | 用途 |
|----|------|------|
| `react-markdown` | ^10.x | Markdown 渲染 |
| `remark-gfm` | ^4.x | GitHub Flavored Markdown |

#### 文件结构变更

新增文件：
- `src/utils/parseSSELines.ts` - SSE 行解析工具
- `src/api/chat.ts` - SSE stream API
- `src/api/dialog.ts` - Dialog history API
- `src/features/chat/useChatStream.ts` - SSE Hook
- `src/components/chat/EmptyState/` - 空状态组件
- `src/components/chat/KnowledgeSelector/` - 知识库选择
- `src/components/chat/StreamingText/` - 流式文字
- `src/components/chat/ToolEventCard/` - 工具事件卡片
- `src/components/chat/MessageBubble/` - 消息气泡
- `src/components/chat/MessageList/` - 消息列表
- `src/components/chat/ChatInput/` - 输入框
- `src/features/chat/ChatPage.css` - 聊天页样式

修改文件：
- `src/features/chat/chatStore.ts` - 完整状态管理
- `src/features/chat/ChatPage.tsx` - 集成所有组件
- `package.json` - 新增依赖

### 2.3 设计决策

- 消息气泡：双色对称（用户深色右对齐，助手浅色左对齐）
- 知识库选择：聊前选择模式
- 流式交互：流式中禁用发送
- 工具事件：可展开详情卡片
- 空状态：Logo + 系统介绍
- Markdown：react-markdown + remark-gfm

### 2.4 Git 提交记录

| 提交 | 描述 |
|------|------|
| `b2a766e` | 重构 ChatPage，集成所有聊天组件 |
| `5d20644` | 添加 ChatInput 组件 |
| `79e3f17` | 添加 MessageList 组件 |
| `6699226` | 添加 MessageBubble 组件 |
| `c8ddd14` | 添加 ToolEventCard 组件 |
| `c35842e` | 添加 StreamingText 组件 |
| `e8cb773` | 添加 KnowledgeSelector 组件 |
| `ed17fdd` | 添加 EmptyState 组件 |
| `897cce6` | 添加 useChatStream Hook |
| `532e301` | 添加 chat API 层（SSE stream + dialog history） |
| `4cbfc00` | 重写 chatStore，包含完整状态管理 |
| `20e8638` | 添加 SSE 行解析工具 |
| `a49a4e5` | add react-markdown and remark-gfm for markdown rendering |
| `becf738` | 添加 Phase 2 聊天模块实现计划 |
| `37f83fd` | 添加 Phase 2 聊天模块设计方案 |

---

## 2026-03-22 Phase 2.5：单元测试

### 2.5.1 目标

为已完成的组件和状态管理编写单元测试，确保代码质量：

- UI 组件测试（Button、Input、Card、Chip、Badge）
- 聊天组件测试（EmptyState、ToolEventCard、ChatInput、MessageBubble、MessageList、KnowledgeSelector、StreamingText）
- 状态管理测试（authStore、chatStore）
- 工具函数测试（parseSSELines）
- 页面组件测试（LoginPage）

### 2.5.2 测试框架配置

| 包 | 版本 | 用途 |
|----|------|------|
| `vitest` | ^4.1.0 | 测试框架 |
| `@testing-library/react` | ^16.3.2 | React 组件测试 |
| `@testing-library/jest-dom` | ^6.9.1 | DOM 断言扩展 |
| `happy-dom` | ^20.8.4 | DOM 环境 |

**配置**: `vite.config.ts` 中配置了 `test` 块，使用 `happy-dom` 环境。

### 2.5.3 测试文件结构

```
src/
├── components/
│   ├── ui/
│   │   ├── Button/Button.test.tsx
│   │   ├── Input/Input.test.tsx
│   │   ├── Card/Card.test.tsx
│   │   ├── Chip/Chip.test.tsx
│   │   └── Badge/Badge.test.tsx
│   └── chat/
│       ├── EmptyState/EmptyState.test.tsx
│       ├── ToolEventCard/ToolEventCard.test.tsx
│       ├── ChatInput/ChatInput.test.tsx
│       ├── MessageBubble/MessageBubble.test.tsx
│       ├── MessageList/MessageList.test.tsx
│       ├── KnowledgeSelector/KnowledgeSelector.test.tsx
│       └── StreamingText/StreamingText.test.tsx
├── features/
│   ├── auth/
│   │   ├── authStore.test.ts
│   │   └── LoginPage.test.tsx
│   └── chat/
│       └── chatStore.test.ts
└── utils/
    └── parseSSELines.test.ts
```

### 2.5.4 测试覆盖

| 测试文件 | 测试数量 | 覆盖内容 |
|---------|---------|---------|
| `Button.test.tsx` | 12 | 渲染、变体、尺寸、图标、禁用、加载状态 |
| `Input.test.tsx` | 15 | 标签、错误、提示、图标、ID 生成 |
| `Card.test.tsx` | 13 | Card、CardHeader、CardBody 渲染和样式 |
| `Chip.test.tsx` | 8 | 渲染、变体、尺寸、图标 |
| `Badge.test.tsx` | 6 | 渲染、变体、尺寸 |
| `EmptyState.test.tsx` | 5 | Logo、标题、副标题、功能列表 |
| `ToolEventCard.test.tsx` | 13 | 状态图标、展开/折叠、样式类 |
| `ChatInput.test.tsx` | 13 | 输入、发送、禁用、加载状态 |
| `MessageBubble.test.tsx` | 7 | 用户/助手样式、Markdown、工具事件 |
| `MessageList.test.tsx` | 4 | 空状态、消息渲染 |
| `KnowledgeSelector.test.tsx` | 6 | Chip 切换、清除按钮 |
| `StreamingText.test.tsx` | 4 | 文本渲染、光标 |
| `authStore.test.ts` | 21 | 登录、登出、会话恢复、sessionStorage |
| `chatStore.test.ts` | 21 | 消息、流式、工具事件 |
| `parseSSELines.test.ts` | 9 | SSE 解析、时间戳、错误处理 |
| `LoginPage.test.tsx` | 8 | 表单渲染、提交、错误、加载状态 |

**总计**: 16 个测试文件，164 个测试用例，全部通过

### 2.5.5 测试最佳实践

- 使用 React Testing Library 查询（by role、label、text）
- 使用 `act()` 包装状态更新
- Mock 外部 API 依赖
- Zustand store 在 `beforeEach` 中重置
- Vitest 用于 stores 和工具函数，RTL 用于组件

### 2.5.6 运行测试

```bash
cd frontend
npm run test:run        # 运行所有测试（单次）
npm run test            # 运行测试（watch 模式）
npm run test:coverage   # 生成覆盖率报告
```

### 2.5.7 已知问题

- `ProtectedRoute.test.tsx` 在 happy-dom 环境中可能导致测试卡死，已移除
- 完整测试套件运行时可能因内存不足导致 OOM，需使用 `NODE_OPTIONS="--max-old-space-size=4096"`

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-03-23 | 1.4.0 | 添加创建空知识库功能，支持通过表单创建新的知识库 |
| 2026-03-23 | 1.3.0 | 完成 Phase 3 知识库浏览功能，知识库列表、文件列表、文件详情页面 |
| 2026-03-22 | 1.2.0 | 添加 Phase 2 前端样式重设计，升级为 Warm Paper 蓝灰色调 |
| 2026-03-22 | 1.1.0 | 添加 Phase 2.5 单元测试，完成 164 个测试 |
| 2026-03-21 | 1.0.0 | 初始版本，完成 Phase 1 基础骨架 |

---

## 2026-03-22 Phase 2：前端样式重设计

### 3.1 目标

根据 AI Agent 设计模板文档，对前端样式进行全面升级：

- 核心色彩系统：从 Warm Cream + Terracotta 升级为 Warm Paper 蓝灰色调
- 动画与交互：升级为弹簧曲线 cubic-bezier(0.16, 1, 0.3, 1)
- 圆角与阴影体系：统一组件圆角，采用弥散阴影
- 组件样式细化：Session Item、Message Bubble、ChatInput、Thinking Block、Tool Group

### 3.2 完成的功能

#### Phase 1：核心色彩系统

更新 `src/styles/tokens/colors.css`：

| Token | 原值 | 新值 |
|-------|------|------|
| `--bg` | `#F4F3EE` | `#F8F5ED` |
| `--accent` | `#B5846E` | `#537D96` |
| `--text` | `#2D2B28` | `#3B3D3F` |
| `--border` | `rgba(177,173,161,0.28)` | `rgba(83,125,150,0.22)` |

#### Phase 2：动画曲线与圆角体系

更新 `src/styles/tokens/elevation.css`：

| Token | 原值 | 新值 |
|-------|------|------|
| `--ease-default` | cubic-bezier(0.4, 0, 0.2, 1) | cubic-bezier(0.16, 1, 0.3, 1) |
| `--radius-lg` | 12px | 16px |
| `--radius-xl` | 16px | 18px |

#### Phase 2：组件样式

**ChatInput** (`src/components/chat/ChatInput/`):
- 输入框背景改为透明
- 使用 `.chat-input-wrapper` 类名
- 添加 `align-items: center` 垂直居中
- 移除白色长条

**MessageBubble** (`src/components/chat/MessageBubble/`):
- 用户消息宽度改为 `fit-content`
- 助手消息保持 `width: 100%`
- 添加 Markdown 表格样式
- 气泡最大宽度限制为 70ch

**ToolGroup** (`src/components/chat/ToolGroup/`) - 新增:
- 折叠/展开聚合工具事件
- 显示 "执行完成 X 个工具" 或 "运行中 X/Y 个工具"
- 点击展开查看详情

**ThinkingBlock** (`src/components/chat/ThinkingBlock/`) - 新增:
- AI 思考过程折叠面板
- 左侧极简划线指示

**布局修复**:
- `.layout-main` 添加 `height: 100vh; overflow: hidden`
- `.chat-page` 添加 `overflow: hidden`
- `.message-list` 添加底部 padding 预留输入框空间
- 输入框始终固定在视口底部

### 3.3 设计文档

新增文件：
- `frontend/docs/superpowers/specs/2026-03-22-frontend-style-redesign-design.md`
- `frontend/docs/superpowers/plans/2026-03-22-frontend-style-redesign-plan.md`

### 3.4 Git 提交记录

| 提交 | 描述 |
|------|------|
| `0448159` | fix(frontend): 修复输入框定位和工具事件显示问题 |
| `3b4d020` | fix(chatinput): 修复输入框样式不生效和定位问题 |
| `b6dccdf` | feat(toolgroup): 新增 Tool Group 组件 Phase 3.5 |
| `e5cbc0e` | feat(thinkingblock): 新增 Thinking Block 组件 Phase 3.4 |
| `91a1ad6` | style(messagebubble): 应用消息气泡样式升级 Phase 3.3 |
| `890b8ca` | style(chatinput): 应用输入框样式升级 Phase 3.2 |
| `6c85d1c` | style(sidebar): 应用 session-item 样式升级 Phase 3.1 |
| `48efee6` | style(elevation): 应用弹簧曲线和圆角升级 Phase 2 |
| `0cbabee` | style(colors): 应用 Warm Paper 蓝灰色调主题 Phase 1 |
| `e1d34e8` | docs(frontend): 添加前端样式重设计实施计划 |
| `b099226` | docs(frontend): 添加前端样式重设计规范文档 |
