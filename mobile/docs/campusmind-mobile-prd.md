# CampusMind (RN 端) 产品需求文档 (PRD)

## 1. 产品定位与全局设计规范

- **业务定位**：基于 Web 端核心能力，实现移动端友好的交互体验。核心发力点在于"功能到移动端小屏幕的布局折叠与原生组件适配"。
- **UI 设计规范**：
  - **核心主题**：延续"温柔文具/暖纸"设计语言（主背景色：#F8F5ED）。
  - **视觉语言**：低对比度、大圆角（推荐 `16px` 及以上基准）、弥散阴影，保证大面积留白的呼吸感。界面组件使用半透明毛玻璃材质过渡。
- **存储与网络策略**：纯在线架构（即拿即用）。移动端重渲染、轻存储。发生弱网或断网时，通过优雅的全量 Toast 或缺省占位图提示网络状态。

## 2. 根部路由与架构层级 (Root Navigation)

- **底层架构**：标准底部标签导航（`Bottom-Tab-Navigator`）。
- **Tab 结构配置（共 4 个平级功能入口，底部居留毛玻璃栏）**：
  1. `Home` - 主页（品牌展示 + 功能入口 + 历史记录）
  2. `Chats` - 会话流核心
  3. `Knowledge` - 知识库 + RAG 控制 + 知识构建跳转
  4. `Profile` - 个人中心

## 3. 核心功能模块详细说明

### 3.1 首页（Home Tab）- 沉浸式聚合展示

本页面强调信息聚合和快捷引导，采用卡片化垂直布局：

- **头部沉浸看板 (Hero Banner)**：高度突出品牌，采用圆角大卡（`radius: 16px`），内嵌 CampusMind 品牌介绍与手绘水彩 Logo。
- **腰部导航区块 (Feature Grid)**：两列并排的功能磁贴（Tiles），支持用户一键跳转到核心模块：
  - `新建对话` - 进入 Chats Tab 创建新对话
  - `知识库` - 进入 Knowledge Tab
  - `知识构建` - 进入 Knowledge Build 模块
  - `个人中心` - 进入 Profile Tab
- **底部线性列表 (History Tracker)**：紧跟功能磁贴之后的一份线性列表，收纳最近的对话记录，展示时间戳和对话标题，点击即进入对应聊天上下文（跳转至 Chats Tab 并加载该对话）。

### 3.2 对话核心（Chats Tab）- Tool-calling 呈现与心流保护

移动端最复杂的展示模块，需基于现有 Web 端的 MessageBubble 逻辑进行移动化复刻。

- **消息渲染**：
  - 继承 Web 端 `MessageBubble` 组件逻辑，支持用户消息和助手消息的区分展示。
  - 助手消息支持 Markdown 渲染，包含代码块语法高亮（暖纸主题配色）。
- **Agent 思考状态呈现**：
  - 代码层面继承原有的 `ThinkingBlock` 和 `ToolGroup` 的渲染逻辑。
  - **UI 适配策略**：采用"折叠小化"以节省空间，单行高亮或灰色引用框提示当前调用工具的状态，支持用户主动点击展开查看底层执行日志。
- **知识库溯源跳转 (Citation) 路由规则（待设计项）**：
  - 触发行为：在对话气泡中点击模型引用的 `Citation` 角标。
  - **待设计方案**：禁止当前路由栈的随意 `Tab` 跨越，维持对话高度沉浸感。查阅完来源文档后关闭面板，无缝衔接原有提问输入。
- **注意**：本 Tab 不包含 RAG 开关。RAG 开关位于 Knowledge Tab，由用户在知识库界面选择参与当前对话的知识库。

### 3.3 知识库（Knowledge Tab）- 移动原生采集枢纽

本 Tab 承担双重职责：知识库浏览 + RAG 上下文控制。

- **RAG 控制面板 (RAG Control)**：
  - 顶部或显著位置提供 `启用 RAG` 开关。
  - 知识选择器（`KnowledgeSelector`）：用户可勾选当前对话关联的知识库。被勾选的 KB 将通过 `knowledge_ids` 参数参与后续对话的 RAG 检索。
- **强化采集面板 (Build Entry)**：
  - 提供明显的「知识构建」入口按钮，支持系统默认相机拍文档拍板书、直接调起本地相册/文件管理器上传（移动端特权）。
  - 入口跳转至 Knowledge Build 模块（Crawl + Review 工作流）。
- **文件管理 (View-Only Management)**：
  - 保持列表结构、支持基础文件夹归档和长文档快速点按阅读。
  - **杜绝**在手机端引入"长按重命名、拖拽移动跨文件夹跳转"等过重度节点管理行为。复杂管理引导用户去 Web 端操作。

### 3.4 个人中心（Profile Tab）

- **信息编辑**：支持修改昵称、邮箱、手机号（ProfileCard 组件）。
- **用量统计**：展示对话数、消息数、知识库数、加入时间（StatsGrid 组件）。
- **会话管理**：查看当前活跃会话列表（设备、位置），支持 revocation（SessionList 组件）。
- **偏好设置**：AI 回复偏好调校、历史缓存清理、界面外观设置（如未来可能的夜间模式切换）。
- **关于与登出**：关于我们、版本信息、退出登录。

## 4. 知识构建模块（Knowledge Build）

不作为独立 Tab，通过 Home Feature Grid 或 Knowledge Tab 的「知识构建」入口跳转。

- **Crawl 阶段**：
  - URL 输入面板（CrawlPanel），支持批量 URL 导入（UrlImportModal）。
  - 任务卡片列表（TaskList），展示爬取进度和状态。
- **Review 阶段**：
  - 待审核文件收件箱（ReviewInbox）。
  - 内容审核编辑器（ReviewEditor），支持修改后触发索引。
- **状态轮询**：爬取任务 3 秒轮询间隔。

## 5. 技术栈与框架选型

### 5.1 核心框架

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 跨平台框架 | **React Native 0.76+** | 主流 RN 版本，支持新架构 |
| 语言 | **TypeScript 5** | 类型安全，与 Web 端保持一致 |
| 包管理 | **npm / yarn** | 优先使用 npm，与前端统一 |
| 状态管理 | **Zustand 5** | 轻量级，与 Web 端 Zustand 一致 |
| 路由 | **React Navigation 7** | RN 官方推荐路由方案，支持 Bottom Tabs |
| HTTP 客户端 | **Axios** | 拦截器统一处理 token 注入和 401 自动登出 |
| SSE 处理 | **EventSourcePolyfill** | RN 端 SSE 流式对话支持 |

### 5.2 UI 组件库

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 基础 UI | **React Native Paper** 或 **Tamagui** | Material Design / 原子化 CSS 方案 |
| 图标 | **Lucide React Native** | 与 Web 端 lucide-react 一致的图标库 |
| 毛玻璃效果 | **@react-native-community/blur** | 实现 Tab Bar 毛玻璃效果 |
| 圆角卡片 | **react-native-reanimated** | 圆角、阴影动画支持 |

### 5.3 原生能力

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 相机/相册 | **react-native-image-picker** | 文档拍摄与相册上传 |
| 文件系统 | **react-native-document-picker** | 文件管理器调用 |
| 安全存储 | **react-native-keychain** | token 安全存储（替代 sessionStorage） |
| 手势处理 | **react-native-gesture-handler** | Bottom Sheet 滑动手势 |

### 5.4 开发与构建

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 开发调试 | **Expo**（优先）** | 优先 Expo 提升开发体验 |
| 构建平台 | **Android**（首发）+ iOS | 双平台支持 |
| CI/CD | **GitHub Actions** | 构建与发布流程 |

### 5.5 测试

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 测试框架 | **Jest** | JavaScript/TypeScript 通用测试框架 |
| 组件测试 | **@testing-library/react-native** | RN 组件行为测试 |
| 测试规范 | 测试文件置于源文件旁（`Button.test.tsx` 伴随 `Button.tsx`） | 与 Web 端测试规范一致 |
| 平台适配 | `*.native.test.tsx` 为共享测试，`*.ios.test.tsx` / `*.android.test.tsx` 为平台特定 | 平台差异隔离 |

### 5.6 与 Web 端技术对比

| 维度 | Web 端 | RN 端 |
|------|--------|-------|
| 框架 | React 18 + Vite | React Native 0.76+ |
| 状态管理 | Zustand 5 | Zustand 5（统一） |
| 路由 | React Router v6 | React Navigation 7 |
| 样式 | CSS Modules + Tokens | StyleSheet + Tokens |
| 存储 | sessionStorage | react-native-keychain |
| 字体 | LXGW WenKai Screen | 系统默认 + 思源黑体 |

## 6. 项目文件夹结构

```
mobile/
├── docs/                          # 项目文档
│   ├── campusmind-mobile-prd.md  # 本文档
│   ├── progress-log.md          # 开发进度日志
│   └── problems-log.md          # 问题与解决方案
│
├── src/                           # 源代码
│   ├── App.tsx                    # 应用入口
│   ├── index.ts                   # 入口文件
│   │
│   ├── components/                # 可复用 UI 组件
│   │   ├── ui/                    # 基础 UI 组件（与 Web 端对齐）
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   ├── Input/
│   │   │   ├── Badge/
│   │   │   └── Modal/
│   │   ├── chat/                  # 聊天相关组件
│   │   │   ├── MessageBubble/
│   │   │   ├── MessageList/
│   │   │   ├── ChatInput/
│   │   │   ├── ThinkingBlock/
│   │   │   ├── ToolGroup/
│   │   │   └── EmptyState/
│   │   ├── knowledge/             # 知识库组件
│   │   │   ├── KnowledgeCard/
│   │   │   ├── FileTable/
│   │   │   └── FileContentViewer/
│   │   ├── build/                 # 知识构建组件
│   │   │   ├── CrawlPanel/
│   │   │   ├── TaskList/
│   │   │   ├── ReviewInbox/
│   │   │   └── ReviewEditor/
│   │   ├── home/                  # 首页组件
│   │   │   ├── HeroBanner/
│   │   │   ├── FeatureGrid/
│   │   │   └── HistoryList/
│   │   └── profile/               # 个人中心组件
│   │       ├── ProfileCard/
│   │       ├── StatsGrid/
│   │       └── SessionList/
│   │
│   ├── screens/                   # 页面级组件（对应 Tab）
│   │   ├── HomeScreen.tsx         # 首页
│   │   ├── ChatsScreen.tsx        # 对话
│   │   ├── KnowledgeScreen.tsx    # 知识库
│   │   └── ProfileScreen.tsx      # 个人中心
│   │
│   ├── features/                  # 功能模块
│   │   ├── auth/                  # 认证模块
│   │   │   ├── LoginScreen.tsx
│   │   │   ├── authStore.ts
│   │   │   └── api/
│   │   ├── chat/                  # 对话模块
│   │   │   ├── chatStore.ts
│   │   │   ├── useChatStream.ts
│   │   │   └── api/
│   │   ├── knowledge/             # 知识库模块
│   │   │   ├── knowledgeStore.ts
│   │   │   └── api/
│   │   ├── build/                 # 知识构建模块
│   │   │   ├── buildStore.ts
│   │   │   └── api/
│   │   └── profile/               # 个人中心模块
│   │       ├── profileStore.ts
│   │       └── api/
│   │
│   ├── navigation/                # 路由配置
│   │   ├── RootNavigator.tsx     # 根导航（含 Bottom Tabs）
│   │   ├── TabNavigator.tsx       # Tab 内部导航栈
│   │   └── types.ts               # 路由类型定义
│   │
│   ├── api/                       # API 客户端
│   │   ├── client.ts              # Axios 实例，拦截器
│   │   ├── auth.ts
│   │   ├── chat.ts                # 包含 SSE 流式方法
│   │   ├── dialog.ts
│   │   ├── knowledge.ts
│   │   ├── crawl.ts
│   │   └── types.ts
│   │
│   ├── hooks/                     # 自定义 Hooks
│   │   ├── useAuth.ts
│   │   ├── useChat.ts
│   │   └── useKnowledge.ts
│   │
│   ├── stores/                    # Zustand Stores（轻量级）
│   │   ├── authStore.ts
│   │   ├── chatStore.ts
│   │   ├── knowledgeStore.ts
│   │   └── profileStore.ts
│   │
│   ├── utils/                     # 工具函数
│   │   ├── parseSSELines.ts       # SSE 解析
│   │   ├── parseThinking.ts       # 思考内容解析
│   │   └── storage.ts             # 安全存储封装
│   │
│   ├── styles/                    # 设计系统
│   │   ├── tokens/                # 设计令牌
│   │   │   ├── colors.ts          # 颜色（#F8F5ED 暖纸主题）
│   │   │   ├── typography.ts      # 字体排版
│   │   │   ├── spacing.ts         # 间距
│   │   │   └── elevation.ts       # 阴影层级
│   │   └── index.ts
│   │
│   └── types/                     # 全局类型定义
│       ├── chat.ts
│       ├── knowledge.ts
│       ├── user.ts
│       └── api.ts
│
├── android/                       # Android 原生项目
├── ios/                           # iOS 原生项目
├── .env.example                   # 环境变量模板
├── package.json
├── tsconfig.json
├── babel.config.js
├── metro.config.js
└── app.json                       # Expo 配置（如使用 Expo）
```

### 目录设计原则

1. **组件层 (`components/`)**: 纯 UI 组件，无业务逻辑，与 Web 端组件命名对齐
2. **页面层 (`screens/`)**: 对应 Tab 的顶层页面，组合 components
3. **功能层 (`features/`)**: 包含业务逻辑、状态管理、API 调用
4. **API 层 (`api/`)**: 统一 Axios 实例，token 自动注入，401 自动登出
5. **设计系统 (`styles/tokens/`)**: 颜色/字体/间距/阴影与 Web 端保持语义一致

## 7. 参考：Web 端功能文件列表

以下为 Web 端已有功能对应的源文件，供移动端开发参考：

### 对话核心 (Chat)

| 功能 | 文件路径 |
|------|----------|
| ChatPage（对话页面） | `frontend/src/features/chat/ChatPage.tsx` |
| ChatStore（状态管理） | `frontend/src/features/chat/chatStore.ts` |
| useChatStream（流式 Hook） | `frontend/src/features/chat/useChatStream.ts` |
| MessageBubble（消息气泡） | `frontend/src/components/chat/MessageBubble/index.tsx` |
| MessageList（消息列表） | `frontend/src/components/chat/MessageList/index.tsx` |
| ChatInput（输入框） | `frontend/src/components/chat/ChatInput/index.tsx` |
| ThinkingBlock（思考过程） | `frontend/src/components/chat/ThinkingBlock/index.tsx` |
| ToolGroup（工具调用组） | `frontend/src/components/chat/ToolGroup/index.tsx` |
| KnowledgeSelector（知识选择器） | `frontend/src/components/chat/KnowledgeSelector/index.tsx` |
| EmptyState（空状态） | `frontend/src/components/chat/EmptyState/index.tsx` |
| StreamingText（流式文本） | `frontend/src/components/chat/StreamingText/index.tsx` |
| API：SSE 流式对话 | `frontend/src/api/chat.ts` |
| API：对话框管理 | `frontend/src/api/dialog.ts` |
| 工具函数：SSE 解析 | `frontend/src/utils/parseSSELines.ts` |
| 工具函数：思考内容解析 | `frontend/src/utils/parseThinking.ts` |

### 知识库 (Knowledge)

| 功能 | 文件路径 |
|------|----------|
| KnowledgeListPage（KB 列表页） | `frontend/src/features/knowledge/KnowledgeListPage.tsx` |
| KnowledgeFileListPage（文件列表页） | `frontend/src/features/knowledge/KnowledgeFileListPage.tsx` |
| KnowledgeFileDetailPage（文件内容页） | `frontend/src/features/knowledge/KnowledgeFileDetailPage.tsx` |
| KnowledgeListStore（状态管理） | `frontend/src/features/knowledge/knowledgeListStore.ts` |
| KnowledgeCard（KB 卡片） | `frontend/src/components/knowledge/KnowledgeCard/index.tsx` |
| FileTable（文件表格） | `frontend/src/components/knowledge/FileTable/index.tsx` |
| FileContentViewer（文件内容查看器） | `frontend/src/components/knowledge/FileContentViewer/index.tsx` |
| CreateKnowledgeDialog（创建 KB 对话框） | `frontend/src/features/knowledge/CreateKnowledgeDialog.tsx` |
| API：知识库 CRUD | `frontend/src/api/knowledge.ts` |

### 知识构建 (Build)

| 功能 | 文件路径 |
|------|----------|
| KnowledgeBuildPage（构建页面） | `frontend/src/features/build/KnowledgeBuildPage.tsx` |
| BuildStore（状态管理） | `frontend/src/features/build/buildStore.ts` |
| CrawlPanel（爬取面板） | `frontend/src/components/knowledge_build/CrawlTab/CrawlPanel.tsx` |
| UrlImportModal（URL 导入弹窗） | `frontend/src/components/knowledge_build/CrawlTab/UrlImportModal.tsx` |
| TaskCard（任务卡片） | `frontend/src/components/knowledge_build/CrawlTab/TaskCard.tsx` |
| TaskList（任务列表） | `frontend/src/components/knowledge_build/CrawlTab/TaskList.tsx` |
| ReviewInbox（审核收件箱） | `frontend/src/components/knowledge_build/ReviewTab/ReviewInbox.tsx` |
| ReviewEditor（审核编辑器） | `frontend/src/components/knowledge_build/ReviewTab/ReviewEditor.tsx` |
| API：爬取任务 | `frontend/src/api/crawl.ts` |

### 用户与认证 (Auth/Profile)

| 功能 | 文件路径 |
|------|----------|
| LoginPage（登录页） | `frontend/src/features/auth/LoginPage.tsx` |
| ProtectedRoute（路由鉴权） | `frontend/src/features/auth/ProtectedRoute.tsx` |
| AuthStore（认证状态） | `frontend/src/features/auth/authStore.ts` |
| ProfilePage（个人中心页） | `frontend/src/features/profile/ProfilePage.tsx` |
| ProfileStore（个人状态） | `frontend/src/features/profile/profileStore.ts` |
| ProfileCard（信息卡片） | `frontend/src/features/profile/components/ProfileCard.tsx` |
| StatsGrid（用量统计） | `frontend/src/features/profile/components/StatsGrid.tsx` |
| SessionList（会话列表） | `frontend/src/features/profile/components/SessionList.tsx` |
| API：认证 | `frontend/src/api/auth.ts` |
| API：用户 | `frontend/src/features/profile/api/profile.ts` |

### 布局与路由 (Layout)

| 功能 | 文件路径 |
|------|----------|
| 路由配置 | `frontend/src/routes.tsx` |
| LayoutWithSidebar（侧边栏布局） | `frontend/src/components/layout/Sidebar/Sidebar.tsx` |
| HistoryItem（历史记录项） | `frontend/src/components/layout/Sidebar/HistoryItem.tsx` |
| App 入口 | `frontend/src/App.tsx` |
| 主入口 | `frontend/src/main.tsx` |

### 设计系统 (Design Tokens)

| 资源 | 文件路径 |
|------|----------|
| 颜色令牌 | `frontend/src/styles/tokens/colors.css` |
| 字体排版 | `frontend/src/styles/tokens/typography.css` |
| 间距系统 | `frontend/src/styles/tokens/spacing.css` |
| 阴影层级 | `frontend/src/styles/tokens/elevation.css` |
| 全局样式 | `frontend/src/styles/globals.css` |

### API 客户端 (API Client)

| 功能 | 文件路径 |
|------|----------|
| ApiClient（统一请求客户端） | `frontend/src/api/client.ts` |
| 类型定义 | `frontend/src/api/types.ts` |
