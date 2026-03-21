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

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-03-21 | 1.0.0 | 初始版本，完成 Phase 1 基础骨架 |
