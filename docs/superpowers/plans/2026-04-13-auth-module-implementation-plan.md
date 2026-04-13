# Auth 模块实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现移动端认证模块：AuthStore 状态管理、LoginScreen 登录页、ProtectedRoute 路由保护

**Architecture:** 采用 Zustand 状态管理 + React Navigation 条件渲染。AuthStore 负责登录/登出/会话恢复，LoginScreen 提供登录表单，ProtectedRoute 根据认证状态控制路由访问。

**Tech Stack:** Zustand 5, React Navigation 7, Axios, react-native-keychain

---

## Chunk 1: AuthStore (F-007)

**Files:**
- Create: `mobile/src/features/auth/api/auth.ts`
- Create: `mobile/src/features/auth/authStore.ts`
- Modify: `mobile/src/stores/index.ts` (添加 re-export)
- Test: `mobile/src/features/auth/__tests__/authStore.test.ts`

- [ ] **Step 1: 创建 API 模块**

Create: `mobile/src/features/auth/api/auth.ts`

```typescript
/**
 * 认证 API 调用
 */
import { api } from '../../../api/client';
import { LoginResponse } from '../../../types/api';

export const authApi = {
  login: (username: string, password: string) =>
    api.post<LoginResponse>('/auth/login', { username, password }),

  logout: () => api.post<{ message: string }>('/auth/logout'),
};
```

- [ ] **Step 2: 创建 AuthStore**

Create: `mobile/src/features/auth/authStore.ts`

```typescript
/**
 * AuthStore - 认证状态管理
 */
import { create } from 'zustand';
import { authApi } from './api/auth';
import { storage } from '../../utils/storage';
import { setUnauthorizedCallback } from '../../api/client';
import type { User } from '../../types/api';

interface AuthState {
  user: User | null;
  token: string | null;
  sessionId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  initAuth: () => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  sessionId: null,
  isAuthenticated: false,
  isLoading: false,

  login: async (username: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authApi.login(username, password);
      const user: User = {
        id: response.user_id,
        username,
      };
      const token = response.token;
      const sessionId = response.session_id;

      await storage.setToken(token);
      await storage.setSessionId(sessionId);

      set({ user, token, sessionId, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignore logout errors — clear state anyway
    } finally {
      await storage.clear();
      set({ user: null, token: null, sessionId: null, isAuthenticated: false });
    }
  },

  initAuth: async () => {
    set({ isLoading: true });
    const token = await storage.getToken();
    const sessionId = await storage.getSessionId();

    if (token && sessionId) {
      // Restore session without server validation
      set({
        token,
        sessionId,
        isAuthenticated: true,
        isLoading: false
      });
    } else {
      set({ isLoading: false });
    }
  },
}));

// Setup 401 callback
setUnauthorizedCallback(() => {
  useAuthStore.getState().logout();
});
```

- [ ] **Step 3: 更新 stores/index.ts**

Modify: `mobile/src/stores/index.ts`

```typescript
export { useAuthStore } from '../features/auth/authStore';
```

- [ ] **Step 4: 编写 AuthStore 测试**

Create: `mobile/src/features/auth/__tests__/authStore.test.ts`

```typescript
import { renderHook, act, waitFor } from '@testing-library/react-native';
import { useAuthStore } from '../authStore';

// Mock dependencies
jest.mock('../api/auth', () => ({
  authApi: {
    login: jest.fn(),
    logout: jest.fn(),
  },
}));

jest.mock('../../utils/storage', () => ({
  storage: {
    setToken: jest.fn(),
    setSessionId: jest.fn(),
    getToken: jest.fn(),
    getSessionId: jest.fn(),
    clear: jest.fn(),
  },
}));

jest.mock('../../api/client', () => ({
  setUnauthorizedCallback: jest.fn(),
}));

const { authApi } = require('../api/auth');
const { storage } = require('../../utils/storage');

describe('useAuthStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should login successfully', async () => {
      const mockResponse = {
        user_id: '123',
        token: 'mock-token',
        session_id: 'mock-session',
      };
      authApi.login.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login('student123', 'password');
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.token).toBe('mock-token');
      expect(result.current.user?.id).toBe('123');
      expect(storage.setToken).toHaveBeenCalledWith('mock-token');
      expect(storage.setSessionId).toHaveBeenCalledWith('mock-session');
    });

    it('should handle login failure', async () => {
      authApi.login.mockRejectedValue(new Error('Invalid credentials'));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        try {
          await result.current.login('student123', 'wrong');
        } catch (e) {
          // Expected
        }
      });

      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('logout', () => {
    it('should logout successfully', async () => {
      authApi.logout.mockResolvedValue({ message: 'ok' });

      const { result } = renderHook(() => useAuthStore());

      // Setup logged in state
      await act(async () => {
        result.current.login('student123', 'password');
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(storage.clear).toHaveBeenCalled();
    });
  });

  describe('initAuth', () => {
    it('should restore session from storage', async () => {
      storage.getToken.mockResolvedValue('stored-token');
      storage.getSessionId.mockResolvedValue('stored-session');

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.initAuth();
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.token).toBe('stored-token');
    });

    it('should not authenticate without token', async () => {
      storage.getToken.mockResolvedValue(null);
      storage.getSessionId.mockResolvedValue(null);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.initAuth();
      });

      expect(result.current.isAuthenticated).toBe(false);
    });
  });
});
```

- [ ] **Step 5: 运行测试验证**

Run: `cd /home/luorome/software/CampusMind/mobile && npm run test:run -- --testPathPattern="authStore" --passWithNoTests`
Expected: 测试应通过或报告无测试文件（尚未配置 Jest）

- [ ] **Step 6: 提交 Chunk 1**

```bash
cd /home/luorome/software/CampusMind
git add mobile/src/features/auth/api/auth.ts mobile/src/features/auth/authStore.ts mobile/src/stores/index.ts mobile/src/features/auth/__tests__/authStore.test.ts
git commit -m "feat(mobile): 实现 AuthStore 认证状态管理"
```

---

## Chunk 2: LoginScreen (F-008)

**Files:**
- Create: `mobile/src/features/auth/LoginScreen.tsx`
- Create: `mobile/src/features/auth/__tests__/LoginScreen.test.tsx`
- Reference: `mobile/src/styles/` (colors, typography, spacing)

- [ ] **Step 1: 创建 LoginScreen 组件**

Create: `mobile/src/features/auth/LoginScreen.tsx`

```typescript
/**
 * LoginScreen - 登录页面
 * 参考 Web 端 LoginPage.tsx 实现
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { useAuthStore } from './authStore';
import { colors, typography, spacing } from '../../styles';

export function LoginScreen() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const login = useAuthStore((s) => s.login);
  const isLoading = useAuthStore((s) => s.isLoading);

  const handleSubmit = async () => {
    setError('');
    try {
      await login(username, password);
      // Navigation will be handled by RootNavigator state change
    } catch (err) {
      setError('登录失败，请检查学号和密码');
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        {/* Decorative leaves */}
        <View style={styles.leavesContainer}>
          <Text style={styles.leaf1}>🍃</Text>
          <Text style={styles.leaf2}>🍃</Text>
          <Text style={styles.leaf3}>🍂</Text>
          <Text style={styles.leaf4}>🍃</Text>
        </View>

        <View style={styles.compassDecoration}>🧭</View>

        {/* Login Card */}
        <View style={styles.card}>
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.logoContainer}>
              <Text style={styles.logoEmoji}>🎓</Text>
            </View>
            <Text style={styles.title}>CampusMind</Text>
            <Text style={styles.subtitle}>
              欢迎回来{'\n'}请使用中南大学统一身份认证登录
            </Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
            {/* Username */}
            <View style={styles.inputField}>
              <Text style={styles.label}>学号</Text>
              <View style={styles.inputWithIcon}>
                <Text style={styles.inputIcon}>👤</Text>
                <TextInput
                  style={styles.input}
                  value={username}
                  onChangeText={setUsername}
                  placeholder="请输入学号"
                  placeholderTextColor={colors.textMuted}
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>
            </View>

            {/* Password */}
            <View style={styles.inputField}>
              <Text style={styles.label}>密码</Text>
              <View style={styles.inputWithIcon}>
                <Text style={styles.inputIcon}>🔒</Text>
                <TextInput
                  style={styles.input}
                  value={password}
                  onChangeText={setPassword}
                  placeholder="请输入密码"
                  placeholderTextColor={colors.textMuted}
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                  autoCorrect={false}
                />
                <TouchableOpacity
                  style={styles.passwordToggle}
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <Text>{showPassword ? '👁️' : '👁️‍🗨️'}</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Error */}
            {error ? <Text style={styles.error}>{error}</Text> : null}

            {/* Submit */}
            <TouchableOpacity
              style={[styles.button, isLoading && styles.buttonDisabled]}
              onPress={handleSubmit}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text style={styles.buttonText}>登录</Text>
              )}
            </TouchableOpacity>
          </View>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              © 2026 CampusMind · 中南大学智能校园助手
            </Text>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing[6],
  },
  leavesContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 0,
  },
  leaf1: { position: 'absolute', top: '10%', left: '10%', fontSize: 24, opacity: 0.6 },
  leaf2: { position: 'absolute', top: '20%', right: '15%', fontSize: 24, opacity: 0.6, transform: [{ rotate: '45deg' }] },
  leaf3: { position: 'absolute', bottom: '15%', left: '15%', fontSize: 24, opacity: 0.6, transform: [{ rotate: '-30deg' }] },
  leaf4: { position: 'absolute', bottom: '25%', right: '10%', fontSize: 24, opacity: 0.6, transform: [{ rotate: '15deg' }] },
  compassDecoration: {
    position: 'absolute',
    bottom: '10%',
    left: '5%',
    fontSize: 40,
    opacity: 0.3,
    transform: [{ rotate: '-15deg' }],
  },
  card: {
    width: '100%',
    maxWidth: 440,
    backgroundColor: colors.backgroundCard,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing[8],
    zIndex: 1,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 1,
    shadowRadius: 32,
    elevation: 8,
  },
  header: {
    alignItems: 'center',
    marginBottom: spacing[8],
  },
  logoContainer: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 20,
    marginBottom: spacing[4],
  },
  logoEmoji: { fontSize: 48 },
  title: {
    fontSize: typography.text3xl,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    marginBottom: spacing[2],
  },
  subtitle: {
    fontSize: typography.textSm,
    color: colors.textLight,
    textAlign: 'center',
    lineHeight: typography.textSm * typography.leadingRelaxed,
  },
  form: {
    gap: spacing[5],
  },
  inputField: {
    gap: spacing[2],
  },
  label: {
    fontSize: 13,
    fontWeight: typography.fontMedium,
    color: colors.textLight,
  },
  inputWithIcon: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderWidth: 1.5,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: spacing[3],
  },
  inputIcon: {
    fontSize: 18,
    marginRight: spacing[2],
  },
  input: {
    flex: 1,
    height: 44,
    fontSize: 15,
    color: colors.text,
  },
  passwordToggle: {
    padding: spacing[1],
  },
  error: {
    color: colors.coral,
    fontSize: 13,
    textAlign: 'center',
  },
  button: {
    backgroundColor: colors.accent,
    height: 48,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing[2],
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: '#fff',
    fontSize: typography.textBase,
    fontWeight: typography.fontMedium,
  },
  footer: {
    marginTop: spacing[8],
    paddingTop: spacing[4],
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 11,
    color: colors.textMuted,
  },
});
```

- [ ] **Step 2: 编写 LoginScreen 测试**

Create: `mobile/src/features/auth/__tests__/LoginScreen.test.tsx`

```typescript
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { LoginScreen } from '../LoginScreen';
import { useAuthStore } from '../authStore';

// Mock the auth store
jest.mock('../authStore', () => ({
  useAuthStore: jest.fn(),
}));

const mockLogin = jest.fn();
const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

describe('LoginScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuthStore.mockReturnValue({
      login: mockLogin,
      isLoading: false,
      isAuthenticated: false,
      user: null,
      token: null,
      sessionId: null,
      initAuth: jest.fn(),
      logout: jest.fn(),
    });
  });

  it('should render login form', () => {
    const { getByPlaceholderText, getByText } = render(<LoginScreen />);

    expect(getByPlaceholderText('请输入学号')).toBeTruthy();
    expect(getByPlaceholderText('请输入密码')).toBeTruthy();
    expect(getByText('登录')).toBeTruthy();
  });

  it('should update username and password inputs', () => {
    const { getByPlaceholderText } = render(<LoginScreen />);

    const usernameInput = getByPlaceholderText('请输入学号');
    const passwordInput = getByPlaceholderText('请输入密码');

    fireEvent.changeText(usernameInput, 'student123');
    fireEvent.changeText(passwordInput, 'password123');

    expect(usernameInput.props.value).toBe('student123');
    expect(passwordInput.props.value).toBe('password123');
  });

  it('should call login on submit', async () => {
    mockLogin.mockResolvedValue(undefined);

    const { getByPlaceholderText, getByText } = render(<LoginScreen />);

    fireEvent.changeText(getByPlaceholderText('请输入学号'), 'student123');
    fireEvent.changeText(getByPlaceholderText('请输入密码'), 'password123');
    fireEvent.press(getByText('登录'));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('student123', 'password123');
    });
  });

  it('should show error on login failure', async () => {
    mockLogin.mockRejectedValue(new Error('Invalid'));

    const { getByPlaceholderText, getByText, findByText } = render(<LoginScreen />);

    fireEvent.changeText(getByPlaceholderText('请输入学号'), 'student123');
    fireEvent.changeText(getByPlaceholderText('请输入密码'), 'wrongpassword');
    fireEvent.press(getByText('登录'));

    const errorText = await findByText('登录失败，请检查学号和密码');
    expect(errorText).toBeTruthy();
  });

  it('should show loading indicator when isLoading is true', () => {
    mockUseAuthStore.mockReturnValue({
      login: mockLogin,
      isLoading: true,
      isAuthenticated: false,
      user: null,
      token: null,
      sessionId: null,
      initAuth: jest.fn(),
      logout: jest.fn(),
    });

    const { getByTestId } = render(<LoginScreen />);
    // ActivityIndicator should be present
    expect(getByTestId('activity-indicator')).toBeTruthy();
  });

  it('should toggle password visibility', () => {
    const { getByPlaceholderText, getByText } = render(<LoginScreen />);

    const passwordInput = getByPlaceholderText('请输入密码');
    const toggleButton = getByText('👁️‍🗨️');

    fireEvent.press(toggleButton);
    // After toggle, should show different icon
    expect(getByText('👁️')).toBeTruthy();
  });
});
```

- [ ] **Step 3: 提交 Chunk 2**

```bash
git add mobile/src/features/auth/LoginScreen.tsx mobile/src/features/auth/__tests__/LoginScreen.test.tsx
git commit -m "feat(mobile): 实现 LoginScreen 登录页面"
```

---

## Chunk 3: ProtectedRoute & RootNavigator 集成 (F-009)

**Files:**
- Create: `mobile/src/features/auth/ProtectedRoute.tsx`
- Modify: `mobile/src/navigation/RootNavigator.tsx`
- Modify: `mobile/src/navigation/types.ts` (添加 AuthStack 类型)

- [ ] **Step 1: 添加 AuthStack 类型**

Modify: `mobile/src/navigation/types.ts` (在文件末尾添加)

```typescript
// === Auth Stack (未登录) ===
export type AuthStackParamList = {
  Login: undefined;
};

// === Screen Props ===
export type LoginScreenProps = NativeStackScreenProps<AuthStackParamList, 'Login'>;
```

- [ ] **Step 2: 创建 ProtectedRoute 组件**

Create: `mobile/src/features/auth/ProtectedRoute.tsx`

```typescript
/**
 * ProtectedRoute - 路由保护组件
 * 未登录时重定向到 LoginScreen
 */
import React from 'react';
import { useAuthStore } from './authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  if (!isAuthenticated) {
    // This component is used within NavigationContainer
    // Actual redirect is handled by conditional rendering in RootNavigator
    return null;
  }

  return <>{children}</>;
}
```

- [ ] **Step 3: 更新 RootNavigator 集成认证状态**

Modify: `mobile/src/navigation/RootNavigator.tsx`

```typescript
/**
 * 根导航器
 * 根据认证状态显示 AuthStack 或 MainTabs
 */
import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore } from '../features/auth/authStore';
import { TabNavigator } from './TabNavigator';
import { LoginScreen } from '../features/auth/LoginScreen';
import type { AuthStackParamList } from './types';

const AuthStack = createNativeStackNavigator<AuthStackParamList>();

function AuthStackNavigator() {
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="Login" component={LoginScreen} />
    </AuthStack.Navigator>
  );
}

function MainTabs() {
  return <TabNavigator />;
}

export function RootNavigator() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const initAuth = useAuthStore((s) => s.initAuth);

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainTabs /> : <AuthStackNavigator />}
    </NavigationContainer>
  );
}
```

- [ ] **Step 4: 提交 Chunk 3**

```bash
git add mobile/src/features/auth/ProtectedRoute.tsx mobile/src/navigation/RootNavigator.tsx mobile/src/navigation/types.ts
git commit -m "feat(mobile): 集成 ProtectedRoute 和 RootNavigator 认证状态"
```

---

## Chunk 4: 最终验证与文档更新

**Files:**
- Modify: `mobile/docs/feature-list.json`
- Modify: `mobile/docs/progress-log.md`
- Modify: `mobile/docs/problems-log.md`

- [ ] **Step 1: 更新 feature-list.json**

找到 auth 模块的三个 features，将 status 改为 "completed"：
- F-007: AuthStore
- F-008: LoginScreen
- F-009: ProtectedRoute

- [ ] **Step 2: 更新 progress-log.md**

添加新条目记录 auth 模块完成情况

- [ ] **Step 3: 更新 problems-log.md**

如有遇到的问题，在此记录

- [ ] **Step 4: 合并到 main**

```bash
git checkout main
git merge --no-ff feat/mobile/auth
git push origin main
git branch -d feat/mobile/auth
```

---

## 执行后检查清单

- [ ] AuthStore: login/logout/initAuth 功能正常
- [ ] LoginScreen: 表单渲染、输入、提交、错误提示正常
- [ ] RootNavigator: 根据认证状态正确切换 AuthStack 和 MainTabs
- [ ] 401 回调: API 401 时自动触发登出
- [ ] feature-list.json: auth 模块状态为 completed
- [ ] progress-log.md: 记录完成情况
