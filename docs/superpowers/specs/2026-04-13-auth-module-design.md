# Auth 模块设计方案

## 1. 概述

### 1.1 模块目标

实现移动端用户认证功能，包含：AuthStore 状态管理、LoginScreen 登录页面、ProtectedRoute 路由保护。

### 1.2 与 Web 端一致性

- **接口一致**：使用与 Web 端相同的 `/auth/login` 和 `/auth/logout` API
- **样式主题**：延续"温柔文具/暖纸"设计语言（#F8F5ED 背景色）
- **交互逻辑**：参考 Web 端 LoginPage 的交互模式

### 1.3 技术选型

| 技术 | 说明 |
|------|------|
| 状态管理 | Zustand 5 |
| 安全存储 | react-native-keychain |
| 导航 | React Navigation 7 |
| HTTP 客户端 | Axios（已在 foundation 模块配置） |

---

## 2. 文件结构

```
mobile/src/features/auth/
├── authStore.ts          # Zustand 状态管理
├── LoginScreen.tsx       # 登录页面
├── ProtectedRoute.tsx    # 路由保护组件
└── api/
    └── auth.ts           # 认证 API 调用
```

---

## 3. 详细设计

### 3.1 AuthStore (F-007)

#### State

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  sessionId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
```

#### Actions

| Action | 说明 |
|--------|------|
| `login(username, password)` | 调用 `/auth/login`，存储 token/sessionId/user |
| `logout()` | 调用 `/auth/logout`，清除存储和状态 |
| `initAuth()` | 应用启动时恢复会话（从 keychain 读取） |

#### 与 Web 端差异

| 差异点 | Web 端 | 移动端 |
|--------|--------|--------|
| 存储介质 | sessionStorage | react-native-keychain |
| 401 处理 | 路由重定向 | 通过 `onUnauthorizedCallback` 回调触发登出 |

#### 实现要点

1. **登录成功**：调用 `storage.setToken()` 和 `storage.setSessionId()` 存储凭证
2. **初始化**：App 启动时调用 `initAuth()` 恢复会话
3. **401 回调**：设置 `setUnauthorizedCallback` 供 API client 在 401 时自动触发登出
4. **登出**：调用 API 登出接口后清除所有存储和状态

### 3.2 LoginScreen (F-008)

#### 布局结构

```
┌─────────────────────────────────────┐
│  [装饰性树叶动画]                    │
│                                     │
│         🧭 (指南针装饰)              │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      CampusMind Logo        │   │
│  │        标题文字              │   │
│  │     欢迎回来副标题           │   │
│  │                             │   │
│  │  ┌───────────────────────┐  │   │
│  │  │ 👤 学号输入框          │  │   │
│  │  └───────────────────────┘  │   │
│  │                             │   │
│  │  ┌───────────────────────┐  │   │
│  │  │ 🔒 密码输入框 [👁]     │  │   │
│  │  └───────────────────────┘  │   │
│  │                             │   │
│  │  [错误提示]                  │   │
│  │                             │   │
│  │  ┌───────────────────────┐  │   │
│  │  │      登录按钮          │  │   │
│  │  └───────────────────────┘  │   │
│  │                             │   │
│  │  ─────────────────────────  │   │
│  │  © 2026 CampusMind         │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

#### 设计规范（参考 Web 端 + 移动适配）

| 元素 | 规范 |
|------|------|
| 背景色 | `#F8F5ED` |
| 卡片背景 | `#FCFAF5` |
| 主色调 | `#537D96` |
| 圆角 | `16px` |
| 阴影 | `0 8px 32px rgba(59, 61, 63, 0.09)` |
| 输入框高度 | `44px` |
| 按钮高度 | `48px` |
| 字体 | 系统默认字体 |
| 输入框图标大小 | `18px` |

#### 交互设计

| 交互 | 行为 |
|------|------|
| 学号输入 | 文本输入，placeholder "请输入学号" |
| 密码输入 | 密码模式，可切换显示，placeholder "请输入密码" |
| 密码显示切换 | 点击眼睛图标切换 |
| 登录按钮点击 | 调用 `authStore.login()`，按钮显示 "登录中..." |
| 登录成功 | 跳转到 Home Tab |
| 登录失败 | 显示错误提示 "登录失败，请检查学号和密码" |
| 加载中 | 按钮禁用，显示 loading 状态 |

### 3.3 ProtectedRoute (F-009)

#### 用途

未登录用户访问受保护页面时，重定向到 LoginScreen。

#### 实现方式

React Navigation 条件渲染：

```typescript
// RootNavigator.tsx
function RootNavigator() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainTabs /> : <AuthStack />}
    </NavigationContainer>
  );
}
```

#### 路由结构

```
RootNavigator
├── AuthStack (未登录)
│   └── LoginScreen
└── MainTabs (已登录)
    └── TabNavigator
```

---

## 4. 依赖关系

```
F-007 (AuthStore)
├── F-004: API client (apiClient)
├── F-005: Storage (storage)
└── F-003: User type

F-008 (LoginScreen)
├── F-007: AuthStore
└── F-002: Design tokens (colors, typography, spacing)

F-009 (ProtectedRoute)
├── F-007: AuthStore
└── F-006: Navigation types
```

---

## 5. 测试策略

| Feature | 测试点 |
|---------|--------|
| AuthStore.login | 成功流程、失败流程、网络错误 |
| AuthStore.logout | 登出后状态清除 |
| AuthStore.initAuth | Token 恢复、会话过期处理 |
| LoginScreen | 表单输入、错误提示、Loading 状态 |
| ProtectedRoute | 未登录重定向、已登录放行 |

---

## 6. 待完成事项

- [ ] 实现 `features/auth/api/auth.ts`
- [ ] 实现 `features/auth/authStore.ts`
- [ ] 实现 `features/auth/LoginScreen.tsx`
- [ ] 实现 `features/auth/ProtectedRoute.tsx`
- [ ] 更新 `navigation/RootNavigator.tsx` 集成 ProtectedRoute
- [ ] 编写测试文件
