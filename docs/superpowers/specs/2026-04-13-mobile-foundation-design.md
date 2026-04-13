# Mobile Foundation 模块设计文档

## 概述

完成 CampusMind RN 移动端 foundation 模块开发，包含项目初始化、设计系统、类型定义、API 客户端、安全存储、路由架构、网络状态处理。

## 目录结构

```
mobile/src/
├── App.tsx                    # 应用入口
├── index.ts                   # 入口文件
├── api/
│   ├── client.ts              # Axios 实例 + 拦截器
│   ├── auth.ts                # 认证 API
│   ├── chat.ts                # 对话 API
│   ├── dialog.ts              # 对话管理 API
│   ├── knowledge.ts           # 知识库 API
│   ├── crawl.ts               # 爬取 API
│   └── types.ts               # API 类型定义
├── navigation/
│   ├── RootNavigator.tsx      # 根导航（含 Bottom Tabs）
│   ├── TabNavigator.tsx       # Tab 内部导航栈
│   └── types.ts               # 路由类型定义
├── stores/                    # Zustand stores (基础结构)
├── styles/
│   ├── tokens/                # 设计令牌
│   │   ├── colors.ts          # 颜色 #F8F5ED 暖纸主题
│   │   ├── typography.ts      # 字体排版
│   │   ├── spacing.ts         # 间距
│   │   └── elevation.ts       # 阴影层级
│   └── index.ts
├── types/                     # 全局类型定义
│   ├── chat.ts
│   ├── knowledge.ts
│   ├── user.ts
│   └── api.ts
└── utils/
    ├── parseSSELines.ts       # SSE 解析
    ├── parseThinking.ts       # 思考内容解析
    └── storage.ts             # 安全存储封装
```

## 功能详述

### F-001: 项目初始化

**技术栈**:
- Expo (优先) + React Native CLI fallback
- React Native 0.76+
- TypeScript 5
- Zustand 5
- React Navigation 7
- Axios
- EventSourcePolyfill (SSE 支持)
- @react-native-community/netinfo (网络状态)
- react-native-keychain (安全存储)
- @react-native-community/blur (毛玻璃)

### F-002: 设计系统 Tokens

从 Web 端 CSS tokens 转换为 RN StyleSheet 格式:

**颜色** (colors.ts):
- `--bg: #F8F5ED` → `colors.background`
- `--accent: #537D96` → `colors.accent`
- `--text: #3B3D3F` → `colors.text`
- 完整 semantic aliases 保持一致

**字体** (typography.ts):
- fontFamily: 系统默认 + 思源黑体 fallback
- 字号: 12/14/16/18/20/24/30/36/48

**间距** (spacing.ts):
- 4px 基准: 4/8/12/16/20/24/32/40/48/64/80/96

**阴影** (elevation.ts):
- 圆角: 6/10/16/18px
- 阴影层级: card/elevated/modal/toast

### F-003: TypeScript 类型

核心类型:
- `ChatMessage`, `Dialog`, `KnowledgeBase`, `KnowledgeFile`
- `User`, `UsageStats`, `Session`, `ToolEvent`
- API 类型: `LoginResponse`, `ApiError`

### F-004: API 客户端

- Axios 实例，baseURL 来自环境变量
- 请求拦截器: Bearer token 注入
- 响应拦截器: 401 → 清除 keychain → 跳转 LoginScreen
- SSE 流式方法 (chat.ts)

### F-005: 安全存储

封装 react-native-keychain:
- `storage.setToken(token)`
- `storage.getToken()`
- `storage.removeToken()`
- `storage.setSessionId(sessionId)`
- `storage.getSessionId()`

### F-006: 路由架构

- Bottom Tab Navigator (4 Tab: Home/Chats/Knowledge/Profile)
- Tab Bar: 毛玻璃效果
- 每个 Tab 内部 Stack Navigator
- 类型安全路由

### F-041: 网络状态处理

- @react-native-community/netinfo 监控网络状态
- 离线时 Toast 提示"网络不可用"
- 恢复连接时 Toast 提示"网络已恢复"

## 依赖关系

```
F-001 (项目初始化)
  ├── F-002 (设计系统) ← 依赖 F-001
  ├── F-003 (类型定义) ← 依赖 F-001
  ├── F-004 (API 客户端) ← 依赖 F-001, F-003
  ├── F-005 (安全存储) ← 依赖 F-001
  └── F-006 (路由架构) ← 依赖 F-001
        └── F-041 (网络状态) ← 依赖 F-001
```

## 测试策略

- F-001: 验证项目启动成功，依赖安装完整
- F-002: 验证 token 值与 Web 端一致
- F-003: TypeScript 编译无错误
- F-004: 401 拦截器触发登出流程
- F-005: keychain 存取正确
- F-006: 路由跳转正确
- F-041: 断网/恢复网络 Toast 正确显示
