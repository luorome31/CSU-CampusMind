# Mobile 开发进度日志

## 格式说明

| id | date | progress | commit |
|----|------|----------|--------|
| 自增编号 | 记录日期 | 已完成的功能或变更 | 对应的 commit hash |

---

## 日志

| id | date | progress | commit |
|----|------|----------|--------|
| 1 | 2026-04-13 | 完成 foundation 模块：项目初始化 (Expo + RN 0.76+)、设计系统 tokens (颜色/字体/间距/阴影)、TypeScript 类型定义、API 客户端、安全存储、路由架构、网络状态监控 | 054ca26 |
| 2 | 2026-04-13 | 完成 auth 模块：AuthStore 状态管理 (login/logout/initAuth)、LoginScreen 登录页面 (学号/密码表单)、ProtectedRoute 路由保护、RootNavigator 认证状态集成 |  |
| 3 | 2026-04-14 | 修复 auth 模块漏洞并优化移动端体验：修复 proxy 502 连接错误，替换不支持的 keychain 为 expo-secure-store 支持，并增加对 Web 和 Expo Go 的全平台适配及详细日志追踪；适配移动端 UI |  |
| 4 | 2026-04-14 | 完成 ui 模块：基础 UI 组件 (Button/Card/Input/Badge/Modal 与 Web 端 Props API 对齐)、LoginScreen emoji 替换为 lucide icons、Tab Bar 毛玻璃效果、移动端特权工具 (imagePicker/documentPicker) |  | |
| 5 | 2026-04-14 | 完成 home 模块：HeroBanner (品牌介绍圆角大卡)、FeatureGrid (2列功能磁贴)、HistoryList (对话历史列表)、HomeScreen (组合所有组件)、dialog API (listDialogs/deleteDialog)、TabNavigator 集成 | (见 git log) |
| 6 | 2026-04-14 | 深度重构首页 UI 以匹配设计原稿：HeroBanner 角色插图破框溢出效果、精简 2 列功能按钮、卡片式对话历史列表；修复 TabBar 毛玻璃穿透效果及遮挡问题 | 后续 commit |
| 7 | 2026-04-14 | 完成 F-020 ToolGroup 组件：内联折叠卡片设计，显示工具调用进度和状态图标(成功/失败/进行中)，展开后显示每个工具的名称、输入、输出、错误信息 | |
| 8 | 2026-04-15 | 完成 build 模块：Completed F-030 to F-034: BuildStore, CrawlPanel, TaskList, TaskCard, ReviewInbox, ReviewEditor, BuildScreen | All build module features implemented with tests |
| 9 | 2026-04-16 | 完成 knowledge 模块：F-023~F-029: KnowledgeStore (KB列表/文件列表/文件内容状态管理)、KnowledgeCard (KB卡片)、FileTable (文件列表)、FileContentViewer (Markdown渲染)、RAGSwitch (RAG开关+KB选择器)、KnowledgeScreen+KnowledgeDetailScreen+FileDetailScreen (三级导航)、Build入口跳转；修复Markdown图片key prop错误和status值与API不匹配问题 | c34e2f4 |
| 10 | 2026-04-16 | 完成 profile 模块：F-035~F-039 ProfileStore/ProfileCard/StatsGrid/SessionList/ProfileScreen | |
