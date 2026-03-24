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
| 2026-03-23 | 1.8.0 | 新增对话历史管理功能：Sidebar 侧边栏显示历史记录、HistoryItem 组件（带删除和标题过渡动画）、chatStore 新增 dialogs 状态管理、dialog API 重构、SSE 支持 `new_dialog` 和 `title_update` 事件 |
| 2026-03-23 | 1.7.0 | 优化知识库卡片 UI：修复 badge 与添加按钮重叠、调细选中边框、添加 iOS 风格 Toggle Switch RAG 开关 |
| 2026-03-23 | 1.6.0 | 修复知识库文件数量显示（后端添加 file_count），添加 RAG 开关和知识库选择功能到知识库列表页面 |
| 2026-03-23 | 1.5.0 | 添加代码语法高亮（Warm Paper 主题），修复文件内容获取 auth 问题，添加 Modal 组件和创建知识库对话框 |
| 2026-03-23 | 1.4.0 | 添加创建空知识库功能，支持通过表单创建新的知识库 |
| 2026-03-23 | 1.3.0 | 完成 Phase 3 知识库浏览功能，知识库列表、文件列表、文件详情页面 |
| 2026-03-22 | 1.2.0 | 添加 Phase 2 前端样式重设计，升级为 Warm Paper 蓝灰色调 |
| 2026-03-22 | 1.1.0 | 添加 Phase 2.5 单元测试，完成 164 个测试 |
| 2026-03-21 | 1.0.0 | 初始版本，完成 Phase 1 基础骨架 |

---

---

## 2026-03-23 Phase 4：知识库构建工作流

### 4.1 目标

完成 Phase 4 知识库构建工作流：

- 爬取面板（CrawlPanel）：知识库选择 + URL 列表输入
- 批量导入模态框（UrlImportModal）：支持 .txt/.csv 文件拖拽上传
- 任务列表（TaskList + TaskCard）：实时任务进度展示
- 内容审核（ReviewInbox + ReviewEditor）：审核队列 + Markdown 编辑器
- Tab 页面布局：爬取任务 / 审核队列

### 4.2 完成的功能

#### 新增文件

```
src/features/build/
├── KnowledgeBuildPage.tsx      # Tab 页面主组件
├── KnowledgeBuildPage.module.css
├── buildStore.ts              # Zustand 状态管理
├── buildStore.test.ts
├── api/
│   ├── crawl.ts              # 爬取 API 客户端
│   └── crawl.test.ts
└── components/
    ├── CrawlTab/
    │   ├── CrawlPanel.tsx           # 爬取表单
    │   ├── CrawlPanel.module.css
    │   ├── UrlImportModal.tsx       # 批量导入
    │   ├── UrlImportModal.module.css
    │   ├── UrlImportModal.test.tsx
    │   ├── TaskList.tsx             # 任务列表
    │   ├── TaskList.test.tsx
    │   ├── TaskCard.tsx             # 任务卡片
    │   └── TaskCard.module.css
    └── ReviewTab/
        ├── ReviewInbox.tsx          # 审核收件箱
        ├── ReviewInbox.module.css
        ├── ReviewInbox.test.tsx
        ├── ReviewEditor.tsx         # 内容编辑器
        ├── ReviewEditor.module.css
        └── ReviewEditor.test.tsx
```

#### API 集成

| 端点 | 方法 | 功能 |
|------|------|------|
| `/crawl/batch-with-knowledge` | POST | 批量爬取 |
| `/crawl/tasks` | GET | 获取任务列表 |
| `/crawl/tasks/{task_id}` | GET | 获取任务进度 |
| `/knowledge_file/pending_verify` | GET | 获取待审核文件 |
| `/knowledge_file/{file_id}/content` | GET/PUT | 获取/更新文件内容 |
| `/knowledge_file/{file_id}/trigger_index` | POST | 触发索引 |

#### 状态管理

`buildStore` 包含：

- **UI 状态**：`activeTab`
- **爬取状态**：`selectedKnowledgeId`, `crawlUrls`, `tasks`, `isPolling`
- **导入模态框**：`isImportModalOpen`, `previewUrls`
- **审核状态**：`pendingFiles`, `pendingReviewCount`, `selectedFile`, `fileContent`

#### 轮询机制

- 间隔：3 秒
- 终止条件：终端状态（SUCCESS/FAILED/completed）或 3 次连续错误
- 终端状态时自动刷新待审核文件数

### 4.3 设计决策

- Tab 布局：爬取任务 + 审核队列，支持 pendingReviewCount badge
- 审核面板：左侧收件箱列表 + 右侧 Markdown 编辑器
- 文件导入：支持 .txt（每行一个 URL）和 .csv（第一列）格式
- 任务卡片：进度条 + 成功/失败计数 + 状态图标

### 4.4 Git 提交记录

| 提交 | 描述 |
|------|------|
| `crawl API` | 添加 crawl API 客户端 |
| `buildStore` | 添加 buildStore 状态管理 |
| `TaskCard + TaskList` | 添加任务卡片和列表组件 |
| `CrawlPanel + UrlImportModal` | 添加爬取面板和导入模态框 |
| `ReviewInbox` | 添加审核收件箱组件 |
| `ReviewEditor` | 添加内容编辑器组件 |
| `KnowledgeBuildPage` | 实现 Tab 页面布局 |

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

---

## 2026-03-24 Phase 4.1：爬取任务改进

### 4.1.1 目标

修复爬取任务（知识库构建）Tab 的三个问题：
1. 任务列表无法滚动，新任务会顶掉旧任务
2. 完成任务没有删除按钮（需要确认对话框）
3. 任务状态显示不正确（部分成功时显示"成功"）

### 4.1.2 完成的功能

#### Backend 改动

**CrawlTask 模型** (`backend/app/database/models/crawl_task.py`):
- 新增 `failed_urls_json` 字段（TEXT 类型，存储 JSON 序列化的失败 URL）
- 新增 `failed_urls` 属性，自动解析 JSON 为列表
- `to_dict()` 方法包含 `failed_urls` 字段

**TaskService** (`backend/app/services/crawl/task_service.py`):
- `update_task_progress` 新增 `url` 和 `error` 参数
- 新增 `delete_task` 方法（只删除 CrawlTask，不级联删除 KnowledgeFile）
- 失败 URL 详情记录到 `failed_urls_json`

**TaskWorker** (`backend/app/services/crawl/task_worker.py`):
- `_crawl_one` 和 `_crawl_one_with_knowledge` 失败时传递 URL 和 error

**API 端点** (`backend/app/api/v1/crawl.py`):
- `DELETE /crawl/tasks/{task_id}` - 删除任务
- `POST /crawl/tasks/{task_id}/retry-failed` - 重试失败 URL

#### Frontend 改动

**ConfirmDialog 组件** (`src/features/build/components/ui/ConfirmDialog.tsx`):
- 通用确认对话框组件，支持危险操作高亮

**API Client** (`src/features/build/api/crawl.ts`):
- 新增 `FailedUrl` 接口
- `CrawlTask` 接口新增 `failed_urls` 字段
- 新增 `deleteTask` 和 `retryFailed` 方法

**buildStore** (`src/features/build/buildStore.ts`):
- `removeTask` - 调用 DELETE API
- `retryFailedUrls` - 调用 retry-failed API
- `clearCompletedTasks` - 批量删除已完成任务

**TaskList 组件** (`src/features/build/components/CrawlTab/TaskList.tsx`):
- 使用 flex 布局填充可用空间 (`flex: 1; min-height: 0`)
- 列表区域 `overflow-y: auto` 实现滚动
- 添加"清空已完成"按钮和确认对话框

**TaskCard 组件** (`src/features/build/components/CrawlTab/TaskCard.tsx`):
- 状态显示逻辑改进：正确显示"成功"/"部分成功"/"失败"
- 新增"重试失败链接"按钮
- 新增"删除任务"按钮
- 新增展开失败详情的可折叠区域

### 4.1.3 状态判断逻辑

```typescript
// 状态判断（TaskCard.tsx）
if (status === 'completed' || status === 'SUCCESS') {
  if (fail_count === 0) return '成功';
  if (success_count === 0) return '失败';
  return '部分成功';
}
```

### 4.1.4 测试结果

- 前端：244 tests passed
- 后端：302 tests passed (excluding e2e)
- 修复了 `conftest.py` 中模型未导入导致 `failed_urls_json` 列缺失的问题

#### 滚动问题修复 (2026-03-24 后续)

**问题**: 任务列表无法滚动，新任务会顶掉旧任务

**解决方案**: 使用 flex 布局约束空间
- `.page`: 添加 `height: 100%; display: flex; flex-direction: column`
- `.content`: 添加 `flex: 1; display: flex; flex-direction: column`
- `.crawlContent`: 新增包装容器，使用 `display: flex; flex-direction: column; flex: 1; min-height: 0`
- 整个爬取区域（表单+任务列表）作为一个整体滚动

**关键**: `min-height: 0` 是 flex 子元素能够收缩到低于内容尺寸的必要属性

#### failed_urls 序列化修复

**问题**: `failed_urls` 属性未被 API 返回

**解决方案**: 使用 `@computed_field` 装饰器使 Pydantic 正确序列化
```python
@computed_field
@property
def failed_urls(self) -> list:
    """Parse failed_urls_json to list - computed field for Pydantic serialization"""
```

#### 状态显示修复

**问题**: `success_count=0, fail_count>0` 时显示"等待中"而非"失败"

**解决方案**: 优先判断全部失败情况
```typescript
if (task.success_count === 0 && task.fail_count > 0) {
  return { icon: <X size={16} />, text: '失败', className: styles.failed };
}
```

#### 错误信息清理

**问题**: 失败详情显示 Python traceback，包含技术细节

**解决方案**: 新增 `clean_error_message()` 函数清理错误
```python
def clean_error_message(error_msg: str, url: str = "") -> str:
    """Clean up error message to remove technical details"""
    # 映射常见错误为用户友好的中文提示
    # ERR_NAME_NOT_RESOLVED → "DNS解析失败"
    # 404 / Not Found → "页面不存在 (404)"
    # ...
```

#### 样式符合设计标准

**问题**: TaskCard 使用硬编码颜色，不符合 Warm Paper 设计系统

**解决方案**:
- 状态颜色改用 CSS 变量：`--color-success`、`--color-error`、`--color-warning`
- 背景色使用：`--color-success-bg`、`--color-error-bg`、`--color-warning-bg`
- 动画使用 `var(--ease-spring, ease)` 弹簧曲线
- 状态颜色更新为柔和风格：
  - `--color-success: #4a8c5e`（柔和绿）
  - `--color-error: #b85c5c`（柔和红）
  - `--color-warning: #c4935a`（柔和橙）

### 4.1.5 Git 提交记录

| 提交 | 描述 |
|------|------|
| `4607113` | fix(storage): wrap bytes in BytesIO for MinIO put_object |
| `525af97` | docs(frontend): update progress log for Phase 4 completion |
| `c9d48f9` | feat(build): implement KnowledgeBuildPage with tab-based layout |
| `1c3a476` | feat(build): add ReviewEditor component for content verification |
| `1430d33` | feat(build): add ReviewInbox component for pending verification files |
| `87cd02a` | fix(build): 美化URL显示和知识库下拉框样式 |
| `a31c228` | feat(ui): 添加自定义Select组件替代原生下拉框 |
| `f03cc29` | feat(build): 改进审核队列Tab用户体验 |

## 2026-03-24 Phase 4.2：审核队列Tab改进

### 4.2.1 目标

- 文件列表可折叠，最大化预览区域
- 文件列表隐藏滚动条保持美观
- 保存/索引操作添加Toast用户反馈
- Markdown原文改为格式化预览，支持编辑

### 4.2.2 完成的功能

#### 可折叠文件列表

**实现**: ReviewInbox 添加 `isCollapsed` 和 `onToggleCollapse` props，切换侧边栏折叠状态

**文件**:
- `ReviewInbox.tsx`: 支持折叠/展开模式
- `ReviewInbox.module.css`: 折叠状态仅显示展开按钮
- `KnowledgeBuildPage.tsx`: 管理折叠状态
- `KnowledgeBuildPage.module.css`: 折叠时使用 `grid-template-columns: 48px 1fr`

**效果**: 点击收起按钮，侧边栏宽度从 350px 收缩到 48px，网格布局平滑过渡

#### 隐藏滚动条

**实现**: CSS `scrollbar-width: none` + `::-webkit-scrollbar { display: none }`

**文件**: `ReviewInbox.module.css`

#### Toast用户反馈

**实现**: 新增可复用Toast组件，保存/索引操作后显示成功/失败提示

**文件**:
- `Toast.tsx`: Toast组件 + useToast hook
- `Toast.module.css`: Toast样式（slide-in动画）
- `ReviewEditor.tsx`: 操作后调用 `addToast()`

#### Markdown预览与编辑

**实现**: ReviewEditor 添加模式切换，支持编辑/预览切换

**功能**:
- `parseMarkdown()`: 简单Markdown解析（标题/粗体/斜体/列表/代码）
- 工具栏: 粗体/斜体/标题/列表快捷按钮
- 编辑模式: textarea with 格式化工具栏
- 预览模式: 格式化HTML渲染

**文件**: `ReviewEditor.tsx`, `ReviewEditor.module.css`

### 4.2.3 测试结果

| 测试 | 结果 |
|------|------|
| 构建 | ✅ 通过 |
| 单元测试 (245) | ✅ 全部通过 |
| TypeScript类型 | ✅ 通过 |

### 4.2.4 更新 (2026-03-24 下午)

**问题**: 手写Markdown解析不完善，预览不支持滚动

**解决方案**:
- 使用 `react-markdown` + `remark-gfm` 替代手写解析
- 支持完整的 GFM 语法（表格、任务列表等）
- 预览区添加细滚动条样式，与设计风格一致

**提交**: `53fd325`

---

## 2026-03-24 Phase 5：个人中心 (Personal Center)

### 5.1 目标

实现个人中心页面，包含：
- 用户信息展示与编辑（显示名称、邮箱、手机号）
- 使用统计（对话数、消息数、知识库数、注册时间）
- 活跃会话管理（多设备登录管理）
- 退出登录功能

### 5.2 完成的功能

#### Backend 改动

**UserRepository** (`backend/app/repositories/user_repository.py`):
- `get_by_id()` - 根据 user_id 获取用户信息
- `update()` - 更新用户资料（display_name, email, phone）

**User API** (`backend/app/api/v1/user.py`):
- `GET /api/v1/users/me` - 获取当前用户资料
- `PATCH /api/v1/users/me` - 更新用户资料

**SessionTracker** (`backend/app/core/session/session_tracker.py`):
- `SessionInfo` - 会话信息数据类
- `create_session()` - 创建新会话
- `get_user_sessions()` - 获取用户所有活跃会话
- `delete_session()` - 删除指定会话

**Session API** (`backend/app/api/v1/session.py`):
- `GET /api/v1/auth/sessions` - 获取活跃会话列表
- `GET /api/v1/auth/sessions/current` - 获取当前会话信息
- `DELETE /api/v1/auth/sessions/{session_id}` - 登出指定会话

**登录响应更新**:
- `LoginResponse` 新增 `session_id` 字段

#### Frontend 改动

**API Client** (`src/api/client.ts`):
- 新增 `X-Session-ID` header 支持
- 401 处理时清除 `sessionId`

**AuthStore** (`src/features/auth/authStore.ts`):
- 新增 `sessionId` 状态
- 登录时存储 `sessionId` 到 sessionStorage
- 登出时清除 `sessionId`

**Profile Feature** (`src/features/profile/`):
```
profile/
├── ProfilePage.tsx           # 个人中心主页面
├── ProfilePage.css
├── profileStore.ts           # Zustand 状态管理
├── profileStore.test.ts
├── types.ts                 # TypeScript 类型定义
├── api/
│   └── profile.ts           # API 客户端
└── components/
    ├── ProfileCard.tsx      # 用户信息卡片
    ├── ProfileCard.css
    ├── StatsGrid.tsx        # 使用统计卡片组
    ├── StatsGrid.css
    ├── SessionList.tsx      # 活跃会话列表
    └── SessionList.css
```

**ProfileCard 组件**:
- 头像展示（支持上传按钮占位）
- 可编辑字段：显示名称、邮箱、手机号
- 用户名只读
- 点击编辑模式（输入框 + 保存/取消按钮）

**StatsGrid 组件**:
- 4 个统计卡片：对话数、消息数、知识库数、注册时间
- 使用 lucide-react 图标

**SessionList 组件**:
- 活跃会话列表展示
- 设备图标（PC 显示 Monitor，移动设备显示 Smartphone）
- 相对时间显示（"5分钟前"）
- 当前会话标记"当前"badge
- 非当前会话显示"登出"按钮

#### 路由更新

`src/routes.tsx`:
- `/profile` 路由使用真正的 `ProfilePage` 组件
- `ProtectedRoute` 保护

### 5.3 测试结果

| 测试 | 结果 |
|------|------|
| 构建 | ✅ 通过 |
| 单元测试 (262) | ✅ 全部通过 |
| TypeScript类型 | ✅ 通过 |

### 5.4 Git 提交记录

| 提交 | 描述 |
|------|------|
| `74ea751` | feat(backend): add user profile API endpoints |
| `132f671` | feat(backend): add session management API |
| `cf0a62b` | feat(profile): add profile API client, types, and store |
| `ede086e` | feat(profile): add ProfilePage with routing |
| `8794fd6` | test(profile): add unit tests for profile components |

---

## 2026-03-24 Bug Fix：历史会话工具调用重复

### 问题

点击历史会话时，工具调用显示"重复"：
- 状态图标显示 ○ 和 ✓
- 工具名称出现两次
- 参数显示在不应该的位置

### 根因

`loadDialog` 解析数据库 events 时未合并相同 id 的事件，与 `addToolEvent` 逻辑不一致。

### 解决方案

在 `chatStore.ts` 的 `loadDialog` 中添加去重合并逻辑：

```typescript
for (const event of parsed) {
  const existingIdx = events.findIndex((e) => e.id === event.id);
  if (existingIdx >= 0) {
    events[existingIdx] = { ...events[existingIdx], ...event };
  } else {
    events.push(event);
  }
}
```

### 测试结果

| 测试 | 结果 |
|------|------|
| 单元测试 (245) | ✅ 全部通过 |

---

## 2026-03-24 Bug Fix：页面刷新后跳转登录页

### 问题

登录成功后刷新页面，会跳转到登录页。

### 根因

`ProtectedRoute` 在 `initAuth` 完成前就检查了 `isAuthenticated`（初始为 `false`），导致提前重定向。

### 解决方案

1. `authStore.ts` 的 `initAuth` 添加 `isLoading` 状态管理
2. `ProtectedRoute.tsx` 检查 `isLoading`，为 `true` 时等待初始化完成

```typescript
// authStore.ts
initAuth: async () => {
  set({ isLoading: true });
  // ... restore from sessionStorage
  set({ isLoading: false });
}

// ProtectedRoute.tsx
if (isLoading) {
  return null;  // 等待初始化
}
```

### 测试结果

| 测试 | 结果 |
|------|------|
| 单元测试 (261) | ✅ 全部通过 |

---

## 2026-03-24 UI Redesign：登录页重设计

### 改动概述

将登录页从单调表单重构，添加小班子 mascot、浮动树叶装饰、自定义配色及交互细节。

### 设计方向

**Aesthetic**: 自定义设计（独立于 Warm Paper 主题）

### 主要改动

| 元素 | 旧 | 新 |
|------|----|----|
| 标题 | "Sign In" | CampusMind |
| 副标题 | "Welcome back to CampusMind" | 欢迎回来 / 请使用中南大学统一身份认证登录 |
| 表单标签 | English | 中文（学号、密码） |
| 按钮文字 | "Sign In" | 登录 |
| 出错提示 | "Login failed" | "登录失败，请检查学号和密码" |
| 装饰 | 无 | 浮动树叶动画 🍃 + 指南针 🧭 |
| mascot | 无 | 小班子 dashboard 图片 |
| 页脚 | 无 | © 2026 CampusMind · 中南大学智能校园助手 |
| 密码可见切换 | 无 | Eye/EyeOff 图标切换 |
| 输入图标 | 无 | User/Lock lucide 图标 |

### 文件变更

- `LoginPage.tsx` — 中文化文本 + mascot + lucide 图标 + 密码可见切换
- `LoginPage.css` — 自定义 CSS 变量（`--lp-*` 前缀）、浮动装饰动画、卡片阴影
- `LoginPage.test.tsx` — 更新测试断言以匹配中文文本

### 测试结果

| 测试 | 结果 |
|------|------|
| 单元测试 (261) | ✅ 全部通过 |
