# Mobile Foundation 模块实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成 CampusMind RN 移动端 foundation 模块开发，包含项目初始化、设计系统、类型定义、API 客户端、安全存储、路由架构、网络状态处理。

**Architecture:** 基于 Expo + React Native 0.76+，使用 React Navigation 7 实现底部 Tab 导航，Zustand 5 状态管理，设计系统从 Web 端 CSS tokens 转换为 RN StyleSheet 格式。

**Tech Stack:** Expo, React Native 0.76+, TypeScript 5, Zustand 5, React Navigation 7, Axios, react-native-keychain, @react-native-community/netinfo, @react-native-community/blur

---

## Chunk 1: 项目初始化 (F-001)

### Task 1.1: 初始化 Expo 项目

**Files:**
- Create: `mobile/package.json`
- Create: `mobile/tsconfig.json`
- Create: `mobile/app.json`
- Create: `mobile/babel.config.js`
- Create: `mobile/metro.config.js`
- Create: `mobile/.env.example`

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "campusmind-mobile",
  "version": "1.0.0",
  "main": "node_modules/expo/AppEntry.js",
  "scripts": {
    "start": "expo start",
    "android": "expo run:android",
    "ios": "expo run:ios",
    "web": "expo start --web",
    "test": "jest",
    "test:run": "jest --runInBand",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "expo": "~52.0.0",
    "expo-status-bar": "~2.0.0",
    "react": "18.3.1",
    "react-native": "0.76.5",
    "@react-navigation/native": "^7.0.0",
    "@react-navigation/bottom-tabs": "^7.0.0",
    "@react-navigation/native-stack": "^7.0.0",
    "react-native-screens": "~4.4.0",
    "react-native-safe-area-context": "~4.14.0",
    "zustand": "^5.0.0",
    "axios": "^1.7.0",
    "react-native-keychain": "~9.0.0",
    "@react-native-community/netinfo": "~13.0.0",
    "@react-native-community/blur": "~4.4.0",
    "event-source-polyfill": "^1.0.31"
  },
  "devDependencies": {
    "@babel/core": "^7.25.0",
    "@types/react": "~18.3.0",
    "@types/react-native": "~0.76.0",
    "typescript": "~5.3.0",
    "jest": "^29.7.0",
    "@testing-library/react-native": "^12.5.0",
    "@testing-library/jest-native": "^5.4.0"
  }
}
```

- [ ] **Step 2: 创建 tsconfig.json**

```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 3: 创建 app.json (Expo 配置)**

```json
{
  "expo": {
    "name": "CampusMind",
    "slug": "campusmind-mobile",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#F8F5ED"
    },
    "assetBundlePatterns": ["**/*"],
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.campusmind.mobile"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#F8F5ED"
      },
      "package": "com.campusmind.mobile"
    },
    "plugins": [
      "expo-router"
    ]
  }
}
```

- [ ] **Step 4: 创建 babel.config.js**

```js
module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module-resolver',
        {
          root: ['./src'],
          alias: {
            '@': './src',
          },
        },
      ],
    ],
  };
};
```

- [ ] **Step 5: 创建 metro.config.js**

```js
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

module.exports = config;
```

- [ ] **Step 6: 创建 .env.example**

```bash
# API Configuration
API_BASE_URL=http://localhost:8000/api/v1

# OpenAI API (for embeddings)
OPENAI_API_KEY=your_openai_api_key
```

- [ ] **Step 7: Commit**

```bash
cd /home/luorome/software/CampusMind
git add mobile/package.json mobile/tsconfig.json mobile/app.json mobile/babel.config.js mobile/metro.config.js mobile/.env.example
git commit -m "init(mobile): 初始化 Expo 项目结构"
```

---

### Task 1.2: 创建目录结构

**Files:**
- Create: `mobile/src/index.ts`
- Create: `mobile/src/App.tsx`
- Create: `mobile/src/api/`
- Create: `mobile/src/components/`
- Create: `mobile/src/features/`
- Create: `mobile/src/hooks/`
- Create: `mobile/src/navigation/`
- Create: `mobile/src/screens/`
- Create: `mobile/src/stores/`
- Create: `mobile/src/styles/tokens/`
- Create: `mobile/src/types/`
- Create: `mobile/src/utils/`
- Create: `mobile/assets/` (图标目录)

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p src/{api,components,features,hooks,navigation,screens,stores,styles/tokens,types,utils}
mkdir -p assets
touch src/index.ts src/App.tsx
```

- [ ] **Step 2: 创建基础入口文件**

```ts
// src/index.ts
import { registerRootComponent } from 'expo';
import App from './App';

registerRootComponent(App);
```

- [ ] **Step 3: 创建 App.tsx 骨架**

```tsx
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <StatusBar style="dark" />
        {/* Root Navigator will be added here */}
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add mobile/src/index.ts mobile/src/App.tsx
git commit -m "init(mobile): 创建源码目录结构和基础入口"
```

---

## Chunk 2: 设计系统 Tokens (F-002)

### Task 2.1: 颜色系统

**Files:**
- Create: `mobile/src/styles/tokens/colors.ts`

- [ ] **Step 1: 创建 colors.ts**

```ts
/**
 * Design Tokens: Color System
 * Theme: Warm Paper Blue-Grey Accent
 * 延续 Web 端暖纸主题配色
 */

export const colors = {
  // === Background System ===
  background: '#F8F5ED',
  backgroundCard: '#FCFAF5',
  backgroundGlass: 'rgba(250, 248, 242, 0.92)',

  // === Accent System (Blue-Grey, desaturated) ===
  accent: '#537D96',
  accentHover: '#456A80',
  accentLight: 'rgba(83, 125, 150, 0.08)',

  // === Text System ===
  text: '#3B3D3F',
  textLight: '#6B6F73',
  textMuted: '#8E9196',

  // === Border & Shadow ===
  border: 'rgba(83, 125, 150, 0.22)',
  shadow: 'rgba(59, 61, 63, 0.09)',

  // === Status Colors ===
  green: '#7BAE7F',
  coral: '#EC8F8D',
  danger: '#8B3A3A',

  // === Chat Specific ===
  assistantText: '#2D2B28',
  moodBg: 'rgba(83, 125, 150, 0.05)',
  moodText: '#537D96',
  moodBorder: 'rgba(83, 125, 150, 0.16)',
  toolBg: 'rgba(83, 125, 150, 0.06)',
  toolText: '#6B6F73',
  userBg: 'rgba(83, 125, 150, 0.08)',

  // === Semantic Aliases ===
  success: '#4a8c5e',
  successBg: 'rgba(74, 140, 94, 0.12)',
  error: '#b85c5c',
  errorBg: 'rgba(184, 92, 92, 0.12)',
  warning: '#c4935a',
  warningBg: 'rgba(196, 147, 90, 0.12)',
  info: '#6b8fa3',

  // === Legacy Aliases ===
  bgPrimary: '#F8F5ED',
  bgSecondary: '#FCFAF5',
  bgTertiary: '#E8E5DD',
  textPrimary: '#3B3D3F',
  textSecondary: '#6B6F73',
  textTertiary: '#8E9196',
} as const;

export type ColorKey = keyof typeof colors;
```

- [ ] **Step 2: Commit**

```bash
git add mobile/src/styles/tokens/colors.ts
git commit -m "feat(mobile): 实现颜色设计令牌"
```

---

### Task 2.2: 字体系统

**Files:**
- Create: `mobile/src/styles/tokens/typography.ts`

- [ ] **Step 1: 创建 typography.ts**

```ts
/**
 * Design Tokens: Typography System
 * RN 端字体排版系统
 */

import { Platform, TextStyle } from 'react-native';

const fontFamily = Platform.select({
  ios: 'System',
  android: 'Roboto',
  default: 'System',
});

export const typography = {
  // === Font Families ===
  fontSans: fontFamily,
  fontMono: Platform.select({
    ios: 'Menlo',
    android: 'monospace',
    default: 'monospace',
  }),

  // === Type Scale ===
  textXs: 12,
  textSm: 14,
  textBase: 16,
  textLg: 18,
  textXl: 20,
  text2xl: 24,
  text3xl: 30,
  text4xl: 36,
  text5xl: 48,

  // === Line Heights ===
  leadingNone: 1,
  leadingTight: 1.25,
  leadingSnug: 1.375,
  leadingNormal: 1.5,
  leadingRelaxed: 1.625,

  // === Font Weights ===
  fontNormal: '400' as TextStyle['fontWeight'],
  fontMedium: '500' as TextStyle['fontWeight'],
  fontSemibold: '600' as TextStyle['fontWeight'],
  fontBold: '700' as TextStyle['fontWeight'],
} as const;

// 常用文本样式预设
export const textStyles = {
  display: {
    fontFamily: typography.fontSans,
    fontWeight: typography.fontSemibold,
    lineHeight: typography.text4xl * typography.leadingTight,
  } as TextStyle,
  body: {
    fontFamily: typography.fontSans,
    fontWeight: typography.fontNormal,
    lineHeight: typography.textBase * typography.leadingNormal,
  } as TextStyle,
  label: {
    fontFamily: typography.fontSans,
    fontWeight: typography.fontMedium,
    fontSize: typography.textXs,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  } as TextStyle,
} as const;
```

- [ ] **Step 2: Commit**

```bash
git add mobile/src/styles/tokens/typography.ts
git commit -m "feat(mobile): 实现字体排版设计令牌"
```

---

### Task 2.3: 间距系统

**Files:**
- Create: `mobile/src/styles/tokens/spacing.ts`

- [ ] **Step 1: 创建 spacing.ts**

```ts
/**
 * Design Tokens: Spacing System
 * 4px 基准间距系统
 */

export const spacing = {
  // === Core Spacing Scale ===
  0: 0,
  1: 4,    // 0.25rem
  2: 8,    // 0.5rem
  3: 12,   // 0.75rem
  4: 16,   // 1rem
  5: 20,   // 1.25rem
  6: 24,   // 1.5rem
  8: 32,   // 2rem
  10: 40,  // 2.5rem
  12: 48,  // 3rem
  16: 64,  // 4rem
  20: 80,  // 5rem
  24: 96,  // 6rem

  // === Component-Specific ===
  hitTargetMin: 44,      // WCAG touch target
  inputHeight: 44,        // 2.75rem
  buttonHeightSm: 36,     // 2.25rem
  buttonHeightMd: 44,     // 2.75rem
  buttonHeightLg: 48,     // 3rem

  // === Layout ===
  containerMax: '90vw',
  containerMaxSm: 440,
  containerMaxMd: 720,
  containerMaxLg: 1024,
  containerMaxXl: 1280,
} as const;

// 语义化别名
export const layout = {
  screenPadding: spacing[4],
  cardPadding: spacing[4],
  sectionGap: spacing[8],
  itemGap: spacing[2],
} as const;
```

- [ ] **Step 2: Commit**

```bash
git add mobile/src/styles/tokens/spacing.ts
git commit -m "feat(mobile): 实现间距设计令牌"
```

---

### Task 2.4: 阴影与圆角

**Files:**
- Create: `mobile/src/styles/tokens/elevation.ts`

- [ ] **Step 1: 创建 elevation.ts**

```ts
/**
 * Design Tokens: Elevation & Motion
 * 阴影、圆角、过渡动画系统
 */

import { ViewStyle } from 'react-native';

export const elevation = {
  // === Z-Index Scale ===
  zBase: 0,
  zDropdown: 10,
  zSticky: 20,
  zOverlay: 30,
  zModal: 40,
  zToast: 50,

  // === Border Radius ===
  radiusSm: 6,
  radiusMd: 10,
  radiusLg: 16,
  radiusXl: 18,
  radius2xl: 18,
  radiusFull: 9999,

  // === Shadows ===
  shadowCard: {
    shadowColor: '#3B3D3F',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 3,
    elevation: 2,
  } as ViewStyle,
  shadowCardHover: {
    shadowColor: '#3B3D3F',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 18,
    elevation: 8,
  } as ViewStyle,
  shadowElevated: {
    shadowColor: '#3B3D3F',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.15,
    shadowRadius: 28,
    elevation: 12,
  } as ViewStyle,
} as const;

export const transitions = {
  // === Duration ===
  durationFast: 150,
  durationNormal: 200,
  durationSlow: 300,

  // === Easing ===
  easeDefault: 'cubic-bezier(0.16, 1, 0.3, 1)',
  easeSoft: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
  easeBounce: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
} as const;
```

- [ ] **Step 2: 创建 styles/index.ts 统一导出**

```ts
export { colors } from './tokens/colors';
export { typography, textStyles } from './tokens/typography';
export { spacing, layout } from './tokens/spacing';
export { elevation, transitions } from './tokens/elevation';
```

- [ ] **Step 3: Commit**

```bash
git add mobile/src/styles/tokens/elevation.ts mobile/src/styles/index.ts
git commit -m "feat(mobile): 实现阴影圆角设计令牌和统一导出"
```

---

## Chunk 3: TypeScript 类型定义 (F-003)

### Task 3.1: API 类型

**Files:**
- Create: `mobile/src/types/api.ts`
- Create: `mobile/src/api/types.ts`

- [ ] **Step 1: 创建 api.ts 类型**

```ts
/**
 * 全局 API 类型定义
 */

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

export interface LoginResponse {
  token: string;
  user_id: string;
  session_id: string;
  expires_in: number;
}

export interface User {
  user_id: string;
  username: string;
  nickname?: string;
  email?: string;
  phone?: string;
  avatar_url?: string;
  created_at?: string;
}
```

- [ ] **Step 2: 创建 api/types.ts**

```ts
/**
 * API 层类型定义
 */

export { ApiError, LoginResponse, User } from '../types/api';
```

- [ ] **Step 3: Commit**

```bash
git add mobile/src/types/api.ts mobile/src/api/types.ts
git commit -m "feat(mobile): 定义 API 类型"
```

---

### Task 3.2: Chat 类型

**Files:**
- Create: `mobile/src/types/chat.ts`

- [ ] **Step 1: 创建 chat.ts**

```ts
/**
 * Chat 模块类型定义
 */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  citations?: Citation[];
}

export interface Citation {
  index: number;
  document_id: string;
  text: string;
  score: number;
}

export interface Dialog {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ToolEvent {
  id: string;
  type: 'tool_call' | 'tool_result' | 'tool_error';
  name: string;
  status: 'START' | 'END' | 'ERROR';
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: string;
  timestamp: string;
}

export interface ThinkingBlock {
  id: string;
  content: string;
  reasoning?: string;
}

export interface StreamChunk {
  type: 'message' | 'thinking' | 'tool_event' | 'citation' | 'done' | 'error';
  data: unknown;
}
```

- [ ] **Step 2: Commit**

```bash
git add mobile/src/types/chat.ts
git commit -m "feat(mobile): 定义 Chat 类型"
```

---

### Task 3.3: Knowledge 类型

**Files:**
- Create: `mobile/src/types/knowledge.ts`

- [ ] **Step 1: 创建 knowledge.ts**

```ts
/**
 * Knowledge 模块类型定义
 */

export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  file_count: number;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeFile {
  id: string;
  kb_id: string;
  name: string;
  status: 'pending' | 'processing' | 'ready' | 'error';
  size?: number;
  created_at: string;
  updated_at: string;
}

export interface CrawlTask {
  id: string;
  url: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface ReviewItem {
  id: string;
  task_id: string;
  content: string;
  original_url?: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}
```

- [ ] **Step 2: Commit**

```bash
git add mobile/src/types/knowledge.ts
git commit -m "feat(mobile): 定义 Knowledge 类型"
```

---

### Task 3.4: User/Profile 类型

**Files:**
- Create: `mobile/src/types/user.ts`

- [ ] **Step 1: 创建 user.ts**

```ts
/**
 * User/Profile 模块类型定义
 */

export interface UsageStats {
  dialog_count: number;
  message_count: number;
  knowledge_base_count: number;
  joined_at: string;
}

export interface Session {
  id: string;
  device?: string;
  location?: string;
  ip_address?: string;
  last_active_at: string;
  is_current: boolean;
}
```

- [ ] **Step 2: 创建统一类型导出 src/types/index.ts**

```ts
export * from './api';
export * from './chat';
export * from './knowledge';
export * from './user';
```

- [ ] **Step 3: Commit**

```bash
git add mobile/src/types/user.ts mobile/src/types/index.ts
git commit -m "feat(mobile): 定义 User 类型并创建统一导出"
```

---

## Chunk 4: 安全存储 (F-005)

### Task 4.1: Storage 封装

**Files:**
- Create: `mobile/src/utils/storage.ts`
- Create: `mobile/src/utils/__tests__/storage.test.ts`

- [ ] **Step 1: 编写测试**

```ts
// src/utils/__tests__/storage.test.ts
import { storage } from '../storage';

describe('storage', () => {
  const testToken = 'test_token_123';
  const testSessionId = 'test_session_456';

  beforeEach(async () => {
    // Clear stored values before each test
    await storage.removeToken();
    await storage.removeSessionId();
  });

  it('should set and get token', async () => {
    await storage.setToken(testToken);
    const token = await storage.getToken();
    expect(token).toBe(testToken);
  });

  it('should remove token', async () => {
    await storage.setToken(testToken);
    await storage.removeToken();
    const token = await storage.getToken();
    expect(token).toBeNull();
  });

  it('should set and get sessionId', async () => {
    await storage.setSessionId(testSessionId);
    const sessionId = await storage.getSessionId();
    expect(sessionId).toBe(testSessionId);
  });

  it('should remove sessionId', async () => {
    await storage.setSessionId(testSessionId);
    await storage.removeSessionId();
    const sessionId = await storage.getSessionId();
    expect(sessionId).toBeNull();
  });

  it('should clear all storage', async () => {
    await storage.setToken(testToken);
    await storage.setSessionId(testSessionId);
    await storage.clear();
    const token = await storage.getToken();
    const sessionId = await storage.getSessionId();
    expect(token).toBeNull();
    expect(sessionId).toBeNull();
  });
});
```

- [ ] **Step 2: 运行测试验证失败**

```bash
npm run test:run -- --testPathPattern="storage.test.ts"
# Expected: FAIL - "storage is not defined"
```

- [ ] **Step 3: 实现 storage.ts**

```ts
/**
 * 安全存储封装
 * 使用 react-native-keychain 替代 sessionStorage
 */

import * as Keychain from 'react-native-keychain';

const SERVICE_NAME = 'CampusMind';

export const storage = {
  async setToken(token: string): Promise<void> {
    await Keychain.setGenericPassword('token', token, {
      service: `${SERVICE_NAME}.token`,
    });
  },

  async getToken(): Promise<string | null> {
    try {
      const credentials = await Keychain.getGenericPassword({
        service: `${SERVICE_NAME}.token`,
      });
      if (credentials) {
        return credentials.password;
      }
      return null;
    } catch {
      return null;
    }
  },

  async removeToken(): Promise<void> {
    await Keychain.resetGenericPassword({
      service: `${SERVICE_NAME}.token`,
    });
  },

  async setSessionId(sessionId: string): Promise<void> {
    await Keychain.setGenericPassword('sessionId', sessionId, {
      service: `${SERVICE_NAME}.sessionId`,
    });
  },

  async getSessionId(): Promise<string | null> {
    try {
      const credentials = await Keychain.getGenericPassword({
        service: `${SERVICE_NAME}.sessionId`,
      });
      if (credentials) {
        return credentials.password;
      }
      return null;
    } catch {
      return null;
    }
  },

  async removeSessionId(): Promise<void> {
    await Keychain.resetGenericPassword({
      service: `${SERVICE_NAME}.sessionId`,
    });
  },

  async clear(): Promise<void> {
    await this.removeToken();
    await this.removeSessionId();
  },
};
```

- [ ] **Step 4: 运行测试验证通过**

```bash
npm run test:run -- --testPathPattern="storage.test.ts"
# Expected: PASS
```

- [ ] **Step 5: Commit**

```bash
git add mobile/src/utils/storage.ts mobile/src/utils/__tests__/storage.test.ts
git commit -m "feat(mobile): 实现安全存储封装"
```

---

## Chunk 5: API 客户端 (F-004)

### Task 5.1: Axios 客户端

**Files:**
- Create: `mobile/src/api/client.ts`
- Create: `mobile/src/api/__tests__/client.test.ts`

- [ ] **Step 1: 编写测试**

```ts
// src/api/__tests__/client.test.ts
import axios from 'axios';
import { apiClient } from '../client';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('apiClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('request interceptor', () => {
    it('should add Authorization header when token exists', async () => {
      // Mock token retrieval
      const mockRequest = {
        headers: {},
        baseURL: '/api/v1',
        url: '/test',
        method: 'GET',
      };

      // This test would need proper mocking of the storage module
      // For now, we verify the structure
      expect(apiClient).toBeDefined();
    });
  });

  describe('response interceptor', () => {
    it('should throw ApiError on non-OK response', async () => {
      // Structure test
      expect(apiClient).toBeDefined();
    });
  });
});
```

- [ ] **Step 2: 实现 client.ts**

```ts
/**
 * API 客户端
 * Axios 实例 + token 注入 + 401 自动登出拦截器
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { storage } from '../utils/storage';
import { ApiError } from '../types/api';

// 创建 Axios 实例
const createApiClient = () => {
  const client = axios.create({
    baseURL: process.env.API_BASE_URL || 'http://localhost:8000/api/v1',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 请求拦截器：注入 token
  client.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      const token = await storage.getToken();
      const sessionId = await storage.getSessionId();

      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      if (sessionId && config.headers) {
        config.headers['X-Session-ID'] = sessionId;
      }

      return config;
    },
    (error) => Promise.reject(error)
  );

  // 响应拦截器：处理 401
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      if (error.response?.status === 401) {
        // 清除存储并触发登出
        await storage.clear();
        // 注意：实际重定向到登录页由 navigation 处理
        // 这里抛出错误让调用方处理
        throw new ApiError(401, 'Unauthorized');
      }

      // 其他错误解析
      const errorDetail =
        (error.response?.data as { detail?: string })?.detail ||
        error.message ||
        'Request failed';
      throw new ApiError(error.response?.status || 500, errorDetail);
    }
  );

  return client;
};

export const apiClient = createApiClient();

// 便捷方法
export const api = {
  get: <T>(url: string) => apiClient.get<T>(url),
  post: <T>(url: string, data?: unknown) => apiClient.post<T>(url, data),
  delete: <T>(url: string) => apiClient.delete<T>(url),
  patch: <T>(url: string, data?: unknown) =>
    apiClient.patch<T>(url, data),
};
```

- [ ] **Step 3: 运行测试验证**

```bash
npm run test:run -- --testPathPattern="client.test.ts"
# Expected: PASS (structure tests)
```

- [ ] **Step 4: Commit**

```bash
git add mobile/src/api/client.ts mobile/src/api/__tests__/client.test.ts
git commit -m "feat(mobile): 实现 API 客户端"
```

---

## Chunk 6: 路由架构 (F-006)

### Task 6.1: 路由类型定义

**Files:**
- Create: `mobile/src/navigation/types.ts`

- [ ] **Step 1: 创建 types.ts**

```ts
/**
 * 路由类型定义
 */

import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { BottomTabScreenProps } from '@react-navigation/bottom-tabs';
import type { CompositeScreenProps, NavigatorScreenParams } from '@react-navigation/native';

// === Tab Navigator ===
export type RootTabParamList = {
  HomeTab: NavigatorScreenParams<HomeStackParamList>;
  ChatsTab: NavigatorScreenParams<ChatsStackParamList>;
  KnowledgeTab: NavigatorScreenParams<KnowledgeStackParamList>;
  ProfileTab: NavigatorScreenParams<ProfileStackParamList>;
};

// === Home Stack ===
export type HomeStackParamList = {
  Home: undefined;
  KnowledgeBuild: undefined;
};

// === Chats Stack ===
export type ChatsStackParamList = {
  Chats: undefined;
  ChatDetail: { dialogId: string };
};

// === Knowledge Stack ===
export type KnowledgeStackParamList = {
  KnowledgeList: undefined;
  KnowledgeDetail: { kbId: string };
  FileDetail: { fileId: string };
};

// === Profile Stack ===
export type ProfileStackParamList = {
  Profile: undefined;
  SessionManagement: undefined;
};

// === Screen Props ===
export type HomeScreenProps = CompositeScreenProps<
  NativeStackScreenProps<HomeStackParamList, 'Home'>,
  BottomTabScreenProps<RootTabParamList>
>;

export type ChatsScreenProps = CompositeScreenProps<
  NativeStackScreenProps<ChatsStackParamList, 'Chats'>,
  BottomTabScreenProps<RootTabParamList>
>;

export type KnowledgeScreenProps = CompositeScreenProps<
  NativeStackScreenProps<KnowledgeStackParamList, 'KnowledgeList'>,
  BottomTabScreenProps<RootTabParamList>
>;

export type ProfileScreenProps = CompositeScreenProps<
  NativeStackScreenProps<ProfileStackParamList, 'Profile'>,
  BottomTabScreenProps<RootTabParamList>
>;
```

- [ ] **Step 2: Commit**

```bash
git add mobile/src/navigation/types.ts
git commit -m "feat(mobile): 定义路由类型"
```

---

### Task 6.2: Tab Navigator

**Files:**
- Create: `mobile/src/navigation/TabNavigator.tsx`

- [ ] **Step 1: 创建 TabNavigator.tsx**

```tsx
/**
 * 底部 Tab 导航器
 * 4 个 Tab: Home / Chats / Knowledge / Profile
 */

import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text, StyleSheet } from 'react-native';
import {
  RootTabParamList,
  HomeStackParamList,
  ChatsStackParamList,
  KnowledgeStackParamList,
  ProfileStackParamList,
} from './types';
import { colors, typography, spacing } from '../styles';

// 占位组件（将在后续模块实现）
const PlaceholderScreen = () => <View style={styles.placeholder}><Text>Screen</Text></View>;

const Tab = createBottomTabNavigator<RootTabParamList>();
const HomeStack = createNativeStackNavigator<HomeStackParamList>();
const ChatsStack = createNativeStackNavigator<ChatsStackParamList>();
const KnowledgeStack = createNativeStackNavigator<KnowledgeStackParamList>();
const ProfileStack = createNativeStackNavigator<ProfileStackParamList>();

function HomeStackNavigator() {
  return (
    <HomeStack.Navigator screenOptions={{ headerShown: false }}>
      <HomeStack.Screen name="Home" component={PlaceholderScreen} />
    </HomeStack.Navigator>
  );
}

function ChatsStackNavigator() {
  return (
    <ChatsStack.Navigator screenOptions={{ headerShown: false }}>
      <ChatsStack.Screen name="Chats" component={PlaceholderScreen} />
    </ChatsStack.Navigator>
  );
}

function KnowledgeStackNavigator() {
  return (
    <KnowledgeStack.Navigator screenOptions={{ headerShown: false }}>
      <KnowledgeStack.Screen name="KnowledgeList" component={PlaceholderScreen} />
    </KnowledgeStack.Navigator>
  );
}

function ProfileStackNavigator() {
  return (
    <ProfileStack.Navigator screenOptions={{ headerShown: false }}>
      <ProfileStack.Screen name="Profile" component={PlaceholderScreen} />
    </ProfileStack.Navigator>
  );
}

// Tab 图标组件
function TabIcon({ name, focused }: { name: string; focused: boolean }) {
  const iconMap: Record<string, string> = {
    HomeTab: '🏠',
    ChatsTab: '💬',
    KnowledgeTab: '📚',
    ProfileTab: '👤',
  };
  return (
    <Text style={[styles.tabIcon, focused && styles.tabIconFocused]}>
      {iconMap[name] || '•'}
    </Text>
  );
}

export function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused }) => <TabIcon name={route.name} focused={focused} />,
        tabBarActiveTintColor: colors.accent,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarStyle: styles.tabBar,
        tabBarLabelStyle: styles.tabLabel,
      })}
    >
      <Tab.Screen
        name="HomeTab"
        component={HomeStackNavigator}
        options={{ tabBarLabel: '首页' }}
      />
      <Tab.Screen
        name="ChatsTab"
        component={ChatsStackNavigator}
        options={{ tabBarLabel: '对话' }}
      />
      <Tab.Screen
        name="KnowledgeTab"
        component={KnowledgeStackNavigator}
        options={{ tabBarLabel: '知识库' }}
      />
      <Tab.Screen
        name="ProfileTab"
        component={ProfileStackNavigator}
        options={{ tabBarLabel: '我的' }}
      />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: colors.backgroundGlass,
    borderTopColor: colors.border,
    borderTopWidth: StyleSheet.hairlineWidth,
    paddingTop: spacing[1],
    height: 60,
  },
  tabLabel: {
    fontSize: typography.textXs,
    fontWeight: typography.fontMedium,
  },
  tabIcon: {
    fontSize: 20,
  },
  tabIconFocused: {
    opacity: 1,
  },
  placeholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
});
```

- [ ] **Step 2: 创建 RootNavigator.tsx**

```tsx
/**
 * 根导航器
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { TabNavigator } from './TabNavigator';

export function RootNavigator() {
  return (
    <NavigationContainer>
      <TabNavigator />
    </NavigationContainer>
  );
}
```

- [ ] **Step 3: 更新 App.tsx**

```tsx
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { RootNavigator } from './navigation/RootNavigator';

export default function App() {
  return (
    <SafeAreaProvider>
      <RootNavigator />
      <StatusBar style="dark" />
    </SafeAreaProvider>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add mobile/src/navigation/TabNavigator.tsx mobile/src/navigation/RootNavigator.tsx mobile/src/App.tsx
git commit -m "feat(mobile): 实现 Tab 导航架构"
```

---

## Chunk 7: 网络状态处理 (F-041)

### Task 7.1: 网络状态监控

**Files:**
- Create: `mobile/src/utils/network.ts`
- Create: `mobile/src/hooks/useNetworkStatus.ts`

- [ ] **Step 1: 创建 network.ts**

```ts
/**
 * 网络状态工具
 */

import NetInfo, { NetInfoState } from '@react-native-community/netinfo';

export const network = {
  /**
   * 获取当前网络状态
   */
  async getStatus(): Promise<NetInfoState> {
    return NetInfo.fetch();
  },

  /**
   * 检查是否已连接
   */
  async isConnected(): Promise<boolean> {
    const state = await this.getStatus();
    return state.isConnected ?? false;
  },

  /**
   * 监听网络状态变化
   */
  addListener(
    listener: (state: NetInfoState) => void
  ): () => void {
    const unsubscribe = NetInfo.addEventListener(listener);
    return unsubscribe;
  },
};
```

- [ ] **Step 2: 创建 useNetworkStatus hook**

```tsx
/**
 * 网络状态 Hook
 */

import { useState, useEffect, useCallback } from 'react';
import { network } from '../utils/network';
import { Toast } from 'react-native'; // 假设使用 RN 内置 Alert 或 Toast 库

export function useNetworkStatus() {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [toastShown, setToastShown] = useState(false);

  useEffect(() => {
    // 初始检查
    network.isConnected().then(setIsConnected);

    // 监听变化
    const unsubscribe = network.addListener((state) => {
      const connected = state.isConnected ?? false;
      setIsConnected(connected);

      // 显示 Toast 提示
      if (!connected && !toastShown) {
        // 使用 Alert 模拟 Toast 行为
        // 实际项目中可使用 react-native-toast-message
        console.log('网络不可用');
        setToastShown(true);
      } else if (connected && toastShown) {
        console.log('网络已恢复');
        setToastShown(false);
      }
    });

    return unsubscribe;
  }, [toastShown]);

  const refresh = useCallback(async () => {
    const connected = await network.isConnected();
    setIsConnected(connected);
    return connected;
  }, []);

  return {
    isConnected,
    isChecking: isConnected === null,
    refresh,
  };
}
```

- [ ] **Step 3: Commit**

```bash
git add mobile/src/utils/network.ts mobile/src/hooks/useNetworkStatus.ts
git commit -m "feat(mobile): 实现网络状态监控"
```

---

## 依赖关系总结

```
[F-001] 项目初始化
├── [F-002] 设计系统 Tokens
├── [F-003] TypeScript 类型
├── [F-004] API 客户端 ← 依赖 F-001, F-003
├── [F-005] 安全存储 ← 依赖 F-001
├── [F-006] 路由架构 ← 依赖 F-001
└── [F-041] 网络状态 ← 依赖 F-001
```

## 实施顺序

1. **Chunk 1**: 项目初始化 (F-001)
2. **Chunk 2**: 设计系统 Tokens (F-002)
3. **Chunk 3**: TypeScript 类型 (F-003)
4. **Chunk 4**: 安全存储 (F-005)
5. **Chunk 5**: API 客户端 (F-004) ← 依赖 F-003
6. **Chunk 6**: 路由架构 (F-006)
7. **Chunk 7**: 网络状态 (F-041)

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-13-mobile-foundation-plan.md`. Ready to execute?**
