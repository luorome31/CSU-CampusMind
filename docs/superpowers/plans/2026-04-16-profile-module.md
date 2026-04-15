# Profile 模块实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成 Profile 模块开发（F-035~F-039），包括 ProfileStore、ProfileCard、StatsGrid、SessionList、ProfileScreen

**Architecture:** 基于 Zustand 状态管理 + React Native 组件化结构，遵循暖纸主题设计规范

**Tech Stack:** React Native, Zustand, lucide-react-native, React Navigation

---

## 文件结构

```
mobile/src/
├── features/profile/
│   ├── api/
│   │   └── profile.ts          # API 调用 (新建)
│   ├── profileStore.ts         # Zustand store (新建)
│   ├── components/
│   │   ├── ProfileCard.tsx     # 信息编辑卡片 (新建)
│   │   ├── StatsGrid.tsx       # 用量统计网格 (新建)
│   │   └── SessionList.tsx     # 活跃会话列表 (新建)
│   └── __tests__/
│       └── profileStore.test.ts
├── screens/
│   └── ProfileScreen.tsx       # 主页面 (新建)
└── navigation/
    └── TabNavigator.tsx        # 修改: 注册 ProfileScreen
```

---

## Chunk 1: 基础设施（API + Store）

### Task 1: 创建 profile API 模块

**Files:**
- Create: `mobile/src/features/profile/api/profile.ts`

- [ ] **Step 1: 创建目录和 API 文件**

```typescript
// mobile/src/features/profile/api/profile.ts
import { apiClient } from '../../../api/client';
import type { User, UsageStats, Session } from '../../../types/user';

export interface UpdateProfileData {
  display_name?: string;
  email?: string;
  phone?: string;
}

export const profileApi = {
  getProfile: () => apiClient.get<User>('/users/me'),

  updateProfile: (data: UpdateProfileData) =>
    apiClient.patch<User>('/users/me', data),

  getStats: () => apiClient.get<UsageStats>('/users/me/stats'),

  getSessions: () => apiClient.get<Session[]>('/auth/sessions'),
};
```

- [ ] **Step 2: 提交**

```bash
git add mobile/src/features/profile/api/profile.ts
git commit -m "feat(mobile): 添加 profile API 模块"
```

### Task 2: 更新类型定义

**Files:**
- Modify: `mobile/src/types/user.ts`

- [ ] **Step 1: 检查并补充 User 类型**

检查 `mobile/src/types/user.ts` 是否包含：
- `User` interface (id, username, display_name, avatar_url, email, phone, is_active, created_at, updated_at)
- `UsageStats` interface (conversation_count, message_count, knowledge_base_count, join_date)
- `Session` interface (session_id, device, location, created_at, is_current)
- `UpdateProfileData` interface

如果缺少则补充。

- [ ] **Step 2: 提交**

```bash
git add mobile/src/types/user.ts
git commit -m "feat(mobile): 补充 profile 模块类型定义"
```

### Task 3: 创建 ProfileStore

**Files:**
- Create: `mobile/src/features/profile/profileStore.ts`
- Create: `mobile/src/features/profile/__tests__/profileStore.test.ts`

- [ ] **Step 1: 编写 ProfileStore 测试**

```typescript
// mobile/src/features/profile/__tests__/profileStore.test.ts
import { renderHook, act, waitFor } from '@testing-library/react-native';
import { useProfileStore } from '../profileStore';

// Mock profileApi
jest.mock('../api/profile', () => ({
  profileApi: {
    getProfile: jest.fn(),
    updateProfile: jest.fn(),
    getStats: jest.fn(),
    getSessions: jest.fn(),
  },
}));

describe('useProfileStore', () => {
  beforeEach(() => {
    // Reset store state
    useProfileStore.setState({
      user: null,
      stats: null,
      sessions: [],
      isLoading: false,
      error: null,
    });
  });

  it('should have initial state', () => {
    const { result } = renderHook(() => useProfileStore());
    expect(result.current.user).toBeNull();
    expect(result.current.stats).toBeNull();
    expect(result.current.sessions).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should load profile successfully', async () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      display_name: 'Test User',
    };
    require('../api/profile').profileApi.getProfile.mockResolvedValue({ data: mockUser });

    const { result } = renderHook(() => useProfileStore());

    await act(async () => {
      await result.current.loadProfile();
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isLoading).toBe(false);
  });
});
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd mobile && npm run test -- --testPathPattern="profileStore" --watch=false`
Expected: FAIL (profileStore not yet implemented)

- [ ] **Step 3: 实现 ProfileStore**

```typescript
// mobile/src/features/profile/profileStore.ts
import { create } from 'zustand';
import { profileApi, type UpdateProfileData } from './api/profile';

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

type ProfileStore = ProfileState & ProfileActions;

export const useProfileStore = create<ProfileStore>((set) => ({
  user: null,
  stats: null,
  sessions: [],
  isLoading: false,
  error: null,

  loadProfile: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await profileApi.getProfile();
      set({ user: response.data, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  updateProfile: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await profileApi.updateProfile(data);
      set({ user: response.data, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  loadStats: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await profileApi.getStats();
      set({ stats: response.data, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  loadSessions: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await profileApi.getSessions();
      set({ sessions: response.data, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd mobile && npm run test -- --testPathPattern="profileStore" --watch=false`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add mobile/src/features/profile/profileStore.ts mobile/src/features/profile/__tests__/profileStore.test.ts
git commit -m "feat(mobile): 添加 ProfileStore 状态管理"
```

---

## Chunk 2: UI 组件

### Task 4: 创建 ProfileCard 组件

**Files:**
- Create: `mobile/src/features/profile/components/ProfileCard.tsx`

- [ ] **Step 1: 编写 ProfileCard 组件**

```tsx
// mobile/src/features/profile/components/ProfileCard.tsx
import React, { useState } from 'react';
import { View, Text, StyleSheet, Pressable, TextInput } from 'react-native';
import { Camera, Check, X } from 'lucide-react-native';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { colors, typography, spacing, elevation } from '../../styles';
import { useProfileStore } from '../profileStore';

export function ProfileCard() {
  const { user, updateProfile, isLoading } = useProfileStore();
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');

  if (!user) return null;

  const handleStartEdit = (field: string, value: string) => {
    setEditingField(field);
    setEditValue(value || '');
  };

  const handleSave = async () => {
    if (!editingField) return;
    await updateProfile({ [editingField]: editValue });
    setEditingField(null);
  };

  const handleCancel = () => {
    setEditingField(null);
    setEditValue('');
  };

  const renderField = (
    label: string,
    field: string,
    value: string | null | undefined,
    editable: boolean = true
  ) => (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      {editingField === field ? (
        <View style={styles.fieldEdit}>
          <TextInput
            style={styles.input}
            value={editValue}
            onChangeText={setEditValue}
            autoFocus
          />
          <Pressable onPress={handleSave} disabled={isLoading} style={styles.iconButton}>
            <Check size={18} color={colors.success} />
          </Pressable>
          <Pressable onPress={handleCancel} style={styles.iconButton}>
            <X size={18} color={colors.error} />
          </Pressable>
        </View>
      ) : (
        <Pressable
          style={styles.fieldDisplay}
          onPress={() => editable && handleStartEdit(field, value || '')}
          disabled={!editable}
        >
          <Text style={[styles.fieldValue, !editable && styles.fieldReadonly]}>
            {value || '未设置'}
          </Text>
          {editable && <Text style={styles.editHint}>点击编辑</Text>}
        </Pressable>
      )}
    </View>
  );

  return (
    <Card variant="elevated" padding="md" style={styles.card}>
      <View style={styles.header}>
        <View style={styles.avatar}>
          <View style={styles.avatarPlaceholder}>
            <Text style={styles.avatarText}>
              {(user.display_name || user.username || 'U').charAt(0).toUpperCase()}
            </Text>
          </View>
          <Pressable style={styles.avatarUpload}>
            <Camera size={14} color="#fff" />
          </Pressable>
        </View>
        <View style={styles.nameSection}>
          {renderField('显示名称', 'display_name', user.display_name)}
          {renderField('用户名', 'username', user.username, false)}
        </View>
      </View>
      <View style={styles.fields}>
        {renderField('邮箱', 'email', user.email)}
        {renderField('手机号', 'phone', user.phone)}
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing[4],
    marginTop: spacing[4],
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing[4],
  },
  avatar: {
    width: 64,
    height: 64,
    marginRight: spacing[4],
  },
  avatarPlaceholder: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.accent,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: typography.fontBold,
  },
  avatarUpload: {
    position: 'absolute',
    right: 0,
    bottom: 0,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  nameSection: {
    flex: 1,
  },
  fields: {
    gap: spacing[3],
  },
  field: {
    marginBottom: spacing[2],
  },
  fieldLabel: {
    fontSize: typography.textSm,
    color: colors.textLight,
    marginBottom: spacing[1],
  },
  fieldDisplay: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  fieldValue: {
    fontSize: typography.textMd,
    color: colors.text,
  },
  fieldReadonly: {
    color: colors.textMuted,
  },
  editHint: {
    fontSize: typography.textSm,
    color: colors.accent,
    marginLeft: spacing[2],
  },
  fieldEdit: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    height: 40,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: elevation.radiusMd,
    paddingHorizontal: spacing[3],
    fontSize: typography.textMd,
    color: colors.text,
    backgroundColor: colors.background,
  },
  iconButton: {
    padding: spacing[2],
    marginLeft: spacing[1],
  },
});

export default ProfileCard;
```

- [ ] **Step 2: 提交**

```bash
git add mobile/src/features/profile/components/ProfileCard.tsx
git commit -m "feat(mobile): 添加 ProfileCard 组件"
```

### Task 5: 创建 StatsGrid 组件

**Files:**
- Create: `mobile/src/features/profile/components/StatsGrid.tsx`

- [ ] **Step 1: 编写 StatsGrid 组件**

```tsx
// mobile/src/features/profile/components/StatsGrid.tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { MessageSquare, MessageCircle, BookOpen, Calendar } from 'lucide-react-native';
import { Card } from '../../components/ui/Card';
import { colors, typography, spacing, elevation } from '../../styles';
import { useProfileStore } from '../profileStore';

export function StatsGrid() {
  const { stats, user } = useProfileStore();

  const joinDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
      })
    : '-';

  const items = [
    {
      icon: MessageSquare,
      label: '对话数',
      value: stats?.conversation_count ?? '-',
    },
    {
      icon: MessageCircle,
      label: '消息数',
      value: stats?.message_count ?? '-',
    },
    {
      icon: BookOpen,
      label: '知识库数',
      value: stats?.knowledge_base_count ?? '-',
    },
    {
      icon: Calendar,
      label: '注册时间',
      value: stats?.join_date || joinDate,
    },
  ];

  return (
    <Card variant="elevated" padding="md" style={styles.card}>
      <Text style={styles.title}>使用统计</Text>
      <View style={styles.grid}>
        {items.map((item) => (
          <View key={item.label} style={styles.statCard}>
            <item.icon size={24} color={colors.accent} style={styles.icon} />
            <Text style={styles.value}>{item.value}</Text>
            <Text style={styles.label}>{item.label}</Text>
          </View>
        ))}
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing[4],
    marginTop: spacing[4],
  },
  title: {
    fontSize: typography.textLg,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    marginBottom: spacing[4],
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing[3],
  },
  statCard: {
    width: '47%',
    backgroundColor: colors.background,
    borderRadius: elevation.radiusMd,
    padding: spacing[3],
    alignItems: 'center',
  },
  icon: {
    marginBottom: spacing[2],
  },
  value: {
    fontSize: typography.textLg,
    fontWeight: typography.fontBold,
    color: colors.text,
    marginBottom: spacing[1],
  },
  label: {
    fontSize: typography.textSm,
    color: colors.textLight,
  },
});

export default StatsGrid;
```

- [ ] **Step 2: 提交**

```bash
git add mobile/src/features/profile/components/StatsGrid.tsx
git commit -m "feat(mobile): 添加 StatsGrid 组件"
```

### Task 6: 创建 SessionList 组件

**Files:**
- Create: `mobile/src/features/profile/components/SessionList.tsx`

- [ ] **Step 1: 编写 SessionList 组件**

```tsx
// mobile/src/features/profile/components/SessionList.tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Monitor, Smartphone } from 'lucide-react-native';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { colors, typography, spacing, elevation } from '../../styles';
import { useProfileStore } from '../profileStore';

const getDeviceIcon = (device: string) => {
  const d = device.toLowerCase();
  if (
    d.includes('mobile') ||
    d.includes('iphone') ||
    d.includes('android') ||
    d.includes('ipad')
  ) {
    return Smartphone;
  }
  return Monitor;
};

const formatTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));

  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  return date.toLocaleDateString('zh-CN');
};

export function SessionList() {
  const { sessions } = useProfileStore();

  return (
    <Card variant="elevated" padding="md" style={styles.card}>
      <Text style={styles.title}>活跃会话</Text>
      <View style={styles.list}>
        {sessions.length === 0 ? (
          <Text style={styles.empty}>暂无活跃会话</Text>
        ) : (
          sessions.map((session) => {
            const DeviceIcon = getDeviceIcon(session.device);
            return (
              <View key={session.session_id} style={styles.item}>
                <View style={styles.deviceIcon}>
                  <DeviceIcon size={20} color={colors.accent} />
                </View>
                <View style={styles.info}>
                  <Text style={styles.deviceName}>{session.device}</Text>
                  <Text style={styles.meta}>
                    {session.location} • {formatTime(session.created_at)}
                  </Text>
                </View>
                {session.is_current && (
                  <Badge variant="info" style={styles.badge}>当前</Badge>
                )}
              </View>
            );
          })
        )}
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing[4],
    marginTop: spacing[4],
  },
  title: {
    fontSize: typography.textLg,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    marginBottom: spacing[4],
  },
  list: {
    gap: spacing[3],
  },
  empty: {
    fontSize: typography.textMd,
    color: colors.textMuted,
    textAlign: 'center',
    paddingVertical: spacing[4],
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.background,
    borderRadius: elevation.radiusMd,
    padding: spacing[3],
  },
  deviceIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.accentLight,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing[3],
  },
  info: {
    flex: 1,
  },
  deviceName: {
    fontSize: typography.textMd,
    fontWeight: typography.fontMedium,
    color: colors.text,
    marginBottom: spacing[1],
  },
  meta: {
    fontSize: typography.textSm,
    color: colors.textLight,
  },
  badge: {
    marginLeft: spacing[2],
  },
});

export default SessionList;
```

- [ ] **Step 2: 提交**

```bash
git add mobile/src/features/profile/components/SessionList.tsx
git commit -m "feat(mobile): 添加 SessionList 组件"
```

---

## Chunk 3: ProfileScreen 与集成

### Task 7: 创建 ProfileScreen 页面

**Files:**
- Create: `mobile/src/screens/ProfileScreen.tsx`

- [ ] **Step 1: 编写 ProfileScreen**

```tsx
// mobile/src/screens/ProfileScreen.tsx
import React, { useEffect } from 'react';
import {
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  View,
  Text,
  Pressable,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Info, FileText, LogOut } from 'lucide-react-native';
import { ProfileCard, StatsGrid, SessionList } from '../features/profile/components';
import { useProfileStore } from '../features/profile/profileStore';
import { useAuthStore } from '../features/auth/authStore';
import { colors, typography, spacing } from '../styles';

export function ProfileScreen() {
  const { user, isLoading, loadProfile, loadStats, loadSessions } = useProfileStore();
  const { logout } = useAuthStore();

  useEffect(() => {
    loadProfile();
    loadStats();
    loadSessions();
  }, []);

  const handleLogout = () => {
    Alert.alert('退出登录', '确定要退出登录吗？', [
      { text: '取消', style: 'cancel' },
      {
        text: '确定',
        style: 'destructive',
        onPress: () => logout(),
      },
    ]);
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>个人中心</Text>
      </View>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {isLoading && !user ? (
          <View style={styles.loading}>
            <ActivityIndicator size="small" color={colors.accent} />
          </View>
        ) : (
          <>
            <ProfileCard />
            <StatsGrid />
            <SessionList />

            <View style={styles.section}>
              <Pressable style={styles.aboutItem}>
                <Info size={20} color={colors.textLight} />
                <Text style={styles.aboutText}>关于我们</Text>
              </Pressable>
              <Pressable style={styles.aboutItem}>
                <FileText size={20} color={colors.textLight} />
                <Text style={styles.aboutText}>版本信息</Text>
                <Text style={styles.versionText}>v1.0.0</Text>
              </Pressable>
            </View>

            <Pressable style={styles.logoutButton} onPress={handleLogout}>
              <LogOut size={20} color="#fff" />
              <Text style={styles.logoutText}>退出登录</Text>
            </Pressable>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[3],
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: typography.fontBold,
    color: colors.text,
  },
  scroll: {
    flex: 1,
  },
  content: {
    paddingBottom: spacing[8],
  },
  loading: {
    marginTop: spacing[8],
    alignItems: 'center',
  },
  section: {
    marginHorizontal: spacing[4],
    marginTop: spacing[4],
    backgroundColor: colors.backgroundCard,
    borderRadius: 16,
    overflow: 'hidden',
  },
  aboutItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[4],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  aboutText: {
    flex: 1,
    fontSize: typography.textMd,
    color: colors.text,
    marginLeft: spacing[3],
  },
  versionText: {
    fontSize: typography.textMd,
    color: colors.textMuted,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: spacing[4],
    marginTop: spacing[6],
    height: 48,
    backgroundColor: colors.coral,
    borderRadius: 12,
  },
  logoutText: {
    fontSize: typography.textMd,
    fontWeight: typography.fontMedium,
    color: '#fff',
    marginLeft: spacing[2],
  },
});

export default ProfileScreen;
```

- [ ] **Step 2: 提交**

```bash
git add mobile/src/screens/ProfileScreen.tsx
git commit -m "feat(mobile): 添加 ProfileScreen 页面"
```

### Task 8: 注册 ProfileScreen 到 TabNavigator

**Files:**
- Modify: `mobile/src/navigation/TabNavigator.tsx:63-69`

- [ ] **Step 1: 替换 ProfileStackNavigator 中的 PlaceholderScreen**

找到这段代码：
```tsx
function ProfileStackNavigator() {
  return (
    <ProfileStack.Navigator screenOptions={{ headerShown: false }}>
      <ProfileStack.Screen name="Profile" component={PlaceholderScreen} />
    </ProfileStack.Navigator>
  );
}
```

替换为：
```tsx
import { ProfileScreen } from '../screens/ProfileScreen';

function ProfileStackNavigator() {
  return (
    <ProfileStack.Navigator screenOptions={{ headerShown: false }}>
      <ProfileStack.Screen name="Profile" component={ProfileScreen} />
    </ProfileStack.Navigator>
  );
}
```

同时删除第 28 行的 PlaceholderScreen 定义：
```tsx
// 删除这行:
// const PlaceholderScreen = () => <View style={styles.placeholder}><Text>Screen</Text></View>;
```

- [ ] **Step 2: 提交**

```bash
git add mobile/src/navigation/TabNavigator.tsx
git commit -m "feat(mobile): 集成 ProfileScreen 到 TabNavigator"
```

---

## Chunk 4: 组件测试

### Task 9: 添加组件测试

**Files:**
- Create: `mobile/src/features/profile/components/__tests__/ProfileCard.test.tsx`
- Create: `mobile/src/features/profile/components/__tests__/StatsGrid.test.tsx`
- Create: `mobile/src/features/profile/components/__tests__/SessionList.test.tsx`

- [ ] **Step 1: 编写 ProfileCard 测试**

```tsx
// mobile/src/features/profile/components/__tests__/ProfileCard.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { ProfileCard } from '../ProfileCard';

// Mock useProfileStore
jest.mock('../../profileStore', () => ({
  useProfileStore: () => ({
    user: {
      id: '1',
      username: 'testuser',
      display_name: 'Test User',
      email: 'test@example.com',
      phone: '13800138000',
    },
    updateProfile: jest.fn(),
    isLoading: false,
  }),
}));

describe('ProfileCard', () => {
  it('should render user info correctly', () => {
    const { getByText } = render(<ProfileCard />);

    expect(getByText('Test User')).toBeTruthy();
    expect(getByText('testuser')).toBeTruthy();
    expect(getByText('test@example.com')).toBeTruthy();
  });

  it('should show edit hint on fields', () => {
    const { getAllByText } = render(<ProfileCard />);
    const editHints = getAllByText('点击编辑');
    expect(editHints.length).toBe(2); // display_name and email are editable
  });
});
```

- [ ] **Step 2: 提交**

```bash
git add mobile/src/features/profile/components/__tests__/
git commit -m "test(mobile): 添加 ProfileCard 组件测试"
```

---

## 验证清单

完成所有任务后，运行以下验证：

```bash
# 1. 类型检查
cd mobile && npm run typecheck

# 2. 运行测试
npm run test -- --watch=false

# 3. 验证 TabNavigator 中 ProfileScreen 已注册
grep -n "ProfileScreen" mobile/src/navigation/TabNavigator.tsx
```

预期输出：
- 类型检查通过
- 所有测试通过
- TabNavigator.tsx 中 ProfileScreen 已正确注册

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-16-profile-module.md`. Ready to execute?**
