# Profile 模块设计方案

## 1. 概述

Profile 模块是 CampusMind 移动端的个人中心页面，基于"温柔文具/暖纸"设计语言，为用户提供个人信息管理、用量统计查看、会话管理和应用信息功能。

**功能范围（F-035 ~ F-039）：**
- ProfileCard - 信息编辑卡片（昵称/邮箱/电话）
- StatsGrid - 用量统计网格（对话数/消息数/KB数/加入时间）
- SessionList - 活跃会话列表（设备/位置/时间 + "当前"标识）
- ProfileScreen - 个人中心完整页面（含 AboutSection + LogoutButton）

**不包含：** Session revocation 功能（已在 PRD 中移除）

## 2. 布局结构

```
ScrollView (垂直滚动, paddingHorizontal: 16)
├── ProfileCard
├── StatsGrid
├── SessionList
├── AboutSection
└── LogoutButton
```

各区块之间间距 16px，使用 Card 组件包裹。

## 3. 组件详细设计

### 3.1 ProfileCard

**布局：**
```
┌─────────────────────────────────────┐
│  ┌───────┐  显示名称          ›  │
│  │ 头像  │  用户名                 │
│  │  📷   │                          │
│  └───────┘  邮箱: xxx@...     ›  │
│              手机: 138****...  ›  │
└─────────────────────────────────────┘
```

**设计规范：**
- 头像：圆形 64x64，右下角相机图标（半透明遮罩）
- 字段行高：48px，点击区域 44px（WCAG 标准）
- 编辑方式：内联编辑
  - 点击字段 → 该行变为输入框 + 保存(✓)/取消(✗) 按钮
  - 用户名字段为只读，不可编辑
- 保存后显示 success/error toast

### 3.2 StatsGrid

**布局：**
```
┌─────────────────────────────────────┐
│  使用统计                            │
│  ┌─────────┐  ┌─────────┐          │
│  │ 💬 12  │  │ 💭 156  │          │
│  │ 对话数  │  │ 消息数  │          │
│  └─────────┘  └─────────┘          │
│  ┌─────────┐  ┌─────────┐          │
│  │ 📚 3   │  │ 📅 2024 │          │
│  │ 知识库数│  │ 注册时间 │          │
│  └─────────┘  └─────────┘          │
└─────────────────────────────────────┘
```

**设计规范：**
- 2x2 网格，gap: 12px
- 每个 stat-card：圆角 12px，padding 12px
- 图标：24px，使用 lucide-react-native
- 数值：textLg, fontBold
- 标签：textSm, textLight

### 3.3 SessionList

**布局：**
```
┌─────────────────────────────────────┐
│  活跃会话                            │
│  📱 iPhone 15   上海  •  刚刚 [当前] │
│  💻 Chrome      北京  •  2小时前     │
└─────────────────────────────────────┘
```

**设计规范：**
- 设备图标：手机(Mobile) / 电脑(Monitor)
- 设备名称 + 位置 + 时间（相对时间：刚刚/X分钟前/X小时前/日期）
- 当前设备显示 "当前" badge（accent 色调）
- 无 revocation 操作

### 3.4 AboutSection

**布局：**
```
┌─────────────────────────────────────┐
│  ℹ️ 关于我们                    ›  │
│  📋 版本信息 v1.0.0                 │
└─────────────────────────────────────┘
```

### 3.5 LogoutButton

**布局：**
```
┌─────────────────────────────────────┐
│         退出登录                      │
└─────────────────────────────────────┘
```

**设计规范：**
- 全宽按钮，高度 48px
- 背景：coral 色 (#EC8F8D)
- 文字：白色，fontMedium
- 点击弹出确认对话框

## 4. API 设计

### 4.1 端点（参考 Web 端）

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /users/me | 获取用户信息 |
| PATCH | /users/me | 更新用户信息 |
| GET | /users/me/stats | 获取用量统计 |
| GET | /auth/sessions | 获取会话列表 |

### 4.2 profileApi 模块

```typescript
// mobile/src/features/profile/api/profile.ts
export const profileApi = {
  getProfile: () => apiClient.get<User>('/users/me'),
  updateProfile: (data: UpdateProfileData) => apiClient.patch<User>('/users/me', data),
  getStats: () => apiClient.get<UsageStats>('/users/me/stats'),
  getSessions: () => apiClient.get<Session[]>('/auth/sessions'),
};
```

## 5. 状态管理

### ProfileStore (Zustand)

```typescript
interface ProfileState {
  user: User | null;
  stats: UsageStats | null;
  sessions: Session[];
  isLoading: boolean;
  error: string | null;
}

interface ProfileActions {
  loadProfile: () => Promise<void>;
  updateProfile: (data: UpdateProfileData) => Promise<void>;
  loadStats: () => Promise<void>;
  loadSessions: () => Promise<void>;
  clearError: () => void;
}
```

## 6. 类型定义

```typescript
// mobile/src/types/user.ts (已有)
interface User {
  id: string;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  created_at: string | null;
  updated_at: string | null;
}

interface UsageStats {
  conversation_count: number;
  message_count: number;
  knowledge_base_count: number;
  join_date: string;
}

interface Session {
  session_id: string;
  device: string;
  location: string;
  created_at: number;
  is_current: boolean;
}
```

## 7. 文件结构

```
mobile/src/
├── features/profile/
│   ├── api/
│   │   └── profile.ts          # API 调用
│   ├── profileStore.ts         # Zustand store
│   ├── components/
│   │   ├── ProfileCard.tsx
│   │   ├── StatsGrid.tsx
│   │   └── SessionList.tsx
│   └── ProfileScreen.tsx       # 主页面
├── components/profile/          # 可选：独立组件目录
│   ├── ProfileCard/
│   ├── StatsGrid/
│   └── SessionList/
```

## 8. 设计令牌

遵循 `mobile/src/styles/` 中的设计系统：

- 背景：#F8F5ED (background), #FCFAF5 (backgroundCard)
- 主色调：#537D96 (accent)
- 文字：#3B3D3F (text), #6B6F73 (textLight)
- 圆角：16px (radiusLg), 12px (radiusMd)
- 间距：16px (标准间距)
