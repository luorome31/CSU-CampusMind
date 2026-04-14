# Home Module Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement CampusMind mobile Home Tab: HeroBanner + FeatureGrid + HistoryList + HomeScreen

**Architecture:** Components in `components/home/`, screen in `screens/`, API in `api/dialog.ts`. TDD: tests next to source files. Navigation integration via TabNavigator.

**Tech Stack:** React Native, lucide-react-native, date-fns, existing tokens/components

---

## Dependencies

```bash
cd /home/luorome/software/CampusMind/mobile
yarn add date-fns
```

---

## Chunk 1: API Layer - dialog.ts

**Files:**
- Create: `mobile/src/api/dialog.ts`
- Test: `mobile/src/api/__tests__/dialog.test.ts`

---

### Task 1: Create dialog API

- [ ] **Step 1: Write the failing test**

```typescript
// mobile/src/api/__tests__/dialog.test.ts
import { listDialogs, deleteDialog } from '../dialog';

describe('dialog API', () => {
  it('should be defined', () => {
    expect(listDialogs).toBeDefined();
    expect(deleteDialog).toBeDefined();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `yarn test:run src/api/__tests__/dialog.test.ts`
Expected: FAIL with "Cannot find module '../dialog'"

- [ ] **Step 3: Write minimal implementation**

```typescript
// mobile/src/api/dialog.ts
import { apiClient } from './client';

export interface Dialog {
  id: string;
  title?: string;
  updatedAt: string;
}

export async function listDialogs(limit = 50): Promise<Dialog[]> {
  return apiClient.get<Dialog[]>(`/dialogs?limit=${limit}`);
}

export async function deleteDialog(dialogId: string): Promise<void> {
  return apiClient.delete<void>(`/dialogs/${dialogId}`);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `yarn test:run src/api/__tests__/dialog.test.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/api/dialog.ts src/api/__tests__/dialog.test.ts
git commit -m "feat(mobile): 添加 dialog API (listDialogs, deleteDialog)"
```

---

## Chunk 2: Home Components

**Files:**
- Create: `mobile/src/components/home/HeroBanner.tsx`
- Create: `mobile/src/components/home/FeatureGrid.tsx`
- Create: `mobile/src/components/home/HistoryList.tsx`
- Create: `mobile/src/components/home/index.ts`
- Create: `mobile/src/components/home/__tests__/HeroBanner.test.tsx`
- Create: `mobile/src/components/home/__tests__/FeatureGrid.test.tsx`
- Create: `mobile/src/components/home/__tests__/HistoryList.test.tsx`

---

### Task 2: HeroBanner Component

- [ ] **Step 1: Write the failing test**

```typescript
// mobile/src/components/home/__tests__/HeroBanner.test.tsx
import React from 'react';
import { render } from '@testing-library/react-native';
import { HeroBanner } from '../HeroBanner';

describe('HeroBanner', () => {
  it('should render brand title', () => {
    const { getByText } = render(<HeroBanner />);
    expect(getByText('CampusMind')).toBeTruthy();
  });

  it('should render subtitle', () => {
    const { getByText } = render(<HeroBanner />);
    expect(getByText('你的智能校园助手')).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `yarn test:run src/components/home/__tests__/HeroBanner.test.tsx`
Expected: FAIL with "Cannot find module '../HeroBanner'"

- [ ] **Step 3: Write minimal implementation**

```typescript
// mobile/src/components/home/HeroBanner.tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card } from '../../ui/Card';
import { colors, typography, spacing } from '../../styles';

export function HeroBanner() {
  return (
    <Card style={styles.card}>
      <View style={styles.logoPlaceholder}>
        <Text style={styles.logoText}>CM</Text>
      </View>
      <Text style={styles.title}>CampusMind</Text>
      <Text style={styles.subtitle}>你的智能校园助手</Text>
      <View style={styles.features}>
        <Text style={styles.feature}>查询成绩和课表</Text>
        <Text style={styles.feature}>了解校园通知和活动</Text>
        <Text style={styles.feature}>获取选课和教务信息</Text>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing[4],
    marginTop: spacing[4],
    padding: spacing[4],
    backgroundColor: colors.backgroundCard,
    borderRadius: 16,
  },
  logoPlaceholder: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.accent,
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'center',
    marginBottom: spacing[3],
  },
  logoText: {
    fontSize: 24,
    fontWeight: '700',
    color: '#fff',
  },
  title: {
    fontSize: typography.text2xl,
    fontWeight: typography.fontBold,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing[1],
  },
  subtitle: {
    fontSize: typography.textMd,
    color: colors.textLight,
    textAlign: 'center',
    marginBottom: spacing[4],
  },
  features: {
    gap: spacing[1],
  },
  feature: {
    fontSize: typography.textSm,
    color: colors.textMuted,
    textAlign: 'center',
  },
});
```

- [ ] **Step 4: Run test to verify it passes**

Run: `yarn test:run src/components/home/__tests__/HeroBanner.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/components/home/HeroBanner.tsx src/components/home/__tests__/HeroBanner.test.tsx
git commit -m "feat(mobile): 添加 HeroBanner 组件"
```

---

### Task 3: FeatureGrid Component

- [ ] **Step 1: Write the failing test**

```typescript
// mobile/src/components/home/__tests__/FeatureGrid.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import { FeatureGrid } from '../FeatureGrid';

const mockNavigate = jest.fn();

jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({ navigate: mockNavigate }),
}));

describe('FeatureGrid', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('should render 4 feature tiles', () => {
    const { getByText } = render(<FeatureGrid />);
    expect(getByText('新建对话')).toBeTruthy();
    expect(getByText('知识库')).toBeTruthy();
    expect(getByText('知识构建')).toBeTruthy();
    expect(getByText('个人中心')).toBeTruthy();
  });

  it('should navigate to ChatsTab when pressing 新建对话', () => {
    const { getByText } = render(<FeatureGrid />);
    fireEvent.press(getByText('新建对话'));
    expect(mockNavigate).toHaveBeenCalledWith('ChatsTab');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `yarn test:run src/components/home/__tests__/FeatureGrid.test.tsx`
Expected: FAIL with "Cannot find module '../FeatureGrid'"

- [ ] **Step 3: Write minimal implementation**

```typescript
// mobile/src/components/home/FeatureGrid.tsx
import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';
import { MessageCircle, BookOpen, FilePlus, User } from 'lucide-react-native';
import { Card } from '../../ui/Card';
import { colors, typography, spacing } from '../../styles';
import type { RootTabParamList } from '../../navigation/types';

type NavigationProp = BottomTabNavigationProp<RootTabParamList>;

const features = [
  { label: '新建对话', icon: MessageCircle, tab: 'ChatsTab' },
  { label: '知识库', icon: BookOpen, tab: 'KnowledgeTab' },
  { label: '知识构建', icon: FilePlus, tab: 'HomeTab' },
  { label: '个人中心', icon: User, tab: 'ProfileTab' },
];

export function FeatureGrid() {
  const navigation = useNavigation<NavigationProp>();

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>快捷入口</Text>
      <View style={styles.grid}>
        {features.map(({ label, icon: Icon, tab }) => (
          <Pressable
            key={label}
            style={({ pressed }) => [styles.tile, pressed && styles.tilePressed]}
            onPress={() => navigation.navigate(tab)}
          >
            <Card style={styles.tileCard}>
              <Icon size={24} color={colors.accent} strokeWidth={2} />
              <Text style={styles.tileLabel}>{label}</Text>
            </Card>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: spacing[6],
    paddingHorizontal: spacing[4],
  },
  sectionTitle: {
    fontSize: typography.textLg,
    fontWeight: typography.fontMedium,
    color: colors.text,
    marginBottom: spacing[3],
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing[3],
  },
  tile: {
    width: '47%',
  },
  tilePressed: {
    opacity: 0.7,
  },
  tileCard: {
    padding: spacing[4],
    backgroundColor: colors.backgroundCard,
    borderRadius: 12,
    alignItems: 'center',
    gap: spacing[2],
  },
  tileLabel: {
    fontSize: typography.textSm,
    color: colors.text,
    fontWeight: typography.fontMedium,
  },
});
```

- [ ] **Step 4: Run test to verify it passes**

Run: `yarn test:run src/components/home/__tests__/FeatureGrid.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/components/home/FeatureGrid.tsx src/components/home/__tests__/FeatureGrid.test.tsx
git commit -m "feat(mobile): 添加 FeatureGrid 组件"
```

---

### Task 4: HistoryList Component

- [ ] **Step 1: Write the failing test**

```typescript
// mobile/src/components/home/__tests__/HistoryList.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import { HistoryList } from '../HistoryList';
import type { Dialog } from '../../../api/dialog';

const mockNavigate = jest.fn();

jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({ navigate: mockNavigate }),
}));

const mockDialogs: Dialog[] = [
  { id: '1', title: 'Test Dialog', updatedAt: new Date().toISOString() },
];

describe('HistoryList', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('should render empty state when no dialogs', () => {
    const { getByText } = render(<HistoryList dialogs={[]} />);
    expect(getByText('暂无对话记录')).toBeTruthy();
  });

  it('should render dialog items', () => {
    const { getByText } = render(<HistoryList dialogs={mockDialogs} />);
    expect(getByText('Test Dialog')).toBeTruthy();
  });

  it('should navigate to ChatDetail when pressing dialog', () => {
    const { getByText } = render(<HistoryList dialogs={mockDialogs} />);
    fireEvent.press(getByText('Test Dialog'));
    expect(mockNavigate).toHaveBeenCalledWith('ChatsTab', {
      screen: 'ChatDetail',
      params: { dialogId: '1' },
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `yarn test:run src/components/home/__tests__/HistoryList.test.tsx`
Expected: FAIL with "Cannot find module '../HistoryList'"

- [ ] **Step 3: Write minimal implementation**

```typescript
// mobile/src/components/home/HistoryList.tsx
import React from 'react';
import { View, Text, StyleSheet, FlatList, Pressable } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';
import { MessageSquare } from 'lucide-react-native';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { colors, typography, spacing } from '../../styles';
import type { RootTabParamList, ChatsStackParamList } from '../../navigation/types';
import type { Dialog } from '../../api/dialog';

type NavigationProp = BottomTabNavigationProp<RootTabParamList>;

interface HistoryListProps {
  dialogs: Dialog[];
}

function HistoryItem({ dialog }: { dialog: Dialog }) {
  const navigation = useNavigation<NavigationProp>();
  const title = dialog.title || '新对话';
  const time = formatDistanceToNow(new Date(dialog.updatedAt), {
    addSuffix: true,
    locale: zhCN,
  });

  return (
    <Pressable
      style={({ pressed }) => [styles.item, pressed && styles.itemPressed]}
      onPress={() =>
        navigation.navigate('ChatsTab', {
          screen: 'ChatDetail',
          params: { dialogId: dialog.id },
        })
      }
    >
      <MessageSquare size={16} color={colors.accent} strokeWidth={2} />
      <View style={styles.itemContent}>
        <Text style={styles.itemTitle} numberOfLines={1}>
          {title}
        </Text>
        <Text style={styles.itemTime}>{time}</Text>
      </View>
    </Pressable>
  );
}

export function HistoryList({ dialogs }: HistoryListProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>最近对话</Text>
      {dialogs.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>暂无对话记录</Text>
        </View>
      ) : (
        <FlatList
          data={dialogs}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => <HistoryItem dialog={item} />}
          scrollEnabled={false}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: spacing[6],
    paddingHorizontal: spacing[4],
  },
  sectionTitle: {
    fontSize: typography.textLg,
    fontWeight: typography.fontMedium,
    color: colors.text,
    marginBottom: spacing[3],
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing[3],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
    gap: spacing[3],
  },
  itemPressed: {
    opacity: 0.7,
  },
  itemContent: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  itemTitle: {
    fontSize: typography.textMd,
    color: colors.text,
    flex: 1,
    marginRight: spacing[2],
  },
  itemTime: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
  empty: {
    paddingVertical: spacing[8],
    alignItems: 'center',
  },
  emptyText: {
    fontSize: typography.textMd,
    color: colors.textMuted,
  },
});
```

- [ ] **Step 4: Run test to verify it passes**

Run: `yarn test:run src/components/home/__tests__/HistoryList.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/components/home/HistoryList.tsx src/components/home/__tests__/HistoryList.test.tsx
git commit -m "feat(mobile): 添加 HistoryList 组件"
```

---

### Task 5: Home Components Index

- [ ] **Step 1: Create index export**

```typescript
// mobile/src/components/home/index.ts
export { HeroBanner } from './HeroBanner';
export { FeatureGrid } from './FeatureGrid';
export { HistoryList } from './HistoryList';
```

- [ ] **Step 2: Commit**

```bash
git add src/components/home/index.ts
git commit -m "feat(mobile): 导出 home 组件 index"
```

---

## Chunk 3: HomeScreen

**Files:**
- Create: `mobile/src/screens/HomeScreen.tsx`
- Create: `mobile/src/screens/__tests__/HomeScreen.test.tsx`

---

### Task 6: HomeScreen

- [ ] **Step 1: Write the failing test**

```typescript
// mobile/src/screens/__tests__/HomeScreen.test.tsx
import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import { HomeScreen } from '../HomeScreen';
import * as dialogApi from '../../api/dialog';

jest.mock('../../api/dialog');

const mockDialogs: dialogApi.Dialog[] = [
  { id: '1', title: 'Dialog 1', updatedAt: new Date().toISOString() },
  { id: '2', title: 'Dialog 2', updatedAt: new Date().toISOString() },
];

describe('HomeScreen', () => {
  beforeEach(() => {
    (dialogApi.listDialogs as jest.Mock).mockResolvedValue(mockDialogs);
  });

  it('should render HeroBanner', async () => {
    const { getByText } = render(<HomeScreen />);
    await waitFor(() => {
      expect(getByText('CampusMind')).toBeTruthy();
    });
  });

  it('should render FeatureGrid', async () => {
    const { getByText } = render(<HomeScreen />);
    await waitFor(() => {
      expect(getByText('快捷入口')).toBeTruthy();
    });
  });

  it('should render HistoryList with dialogs', async () => {
    const { getByText } = render(<HomeScreen />);
    await waitFor(() => {
      expect(getByText('Dialog 1')).toBeTruthy();
      expect(getByText('Dialog 2')).toBeTruthy();
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `yarn test:run src/screens/__tests__/HomeScreen.test.tsx`
Expected: FAIL with "Cannot find module '../HomeScreen'"

- [ ] **Step 3: Write minimal implementation**

```typescript
// mobile/src/screens/HomeScreen.tsx
import React, { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, ActivityIndicator, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { HeroBanner, FeatureGrid, HistoryList } from '../components/home';
import { listDialogs } from '../api/dialog';
import { colors, spacing } from '../styles';
import type { Dialog } from '../api/dialog';

export function HomeScreen() {
  const [dialogs, setDialogs] = useState<Dialog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listDialogs(10)
      .then(setDialogs)
      .catch(() => setDialogs([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <HeroBanner />
        <FeatureGrid />
        {loading ? (
          <View style={styles.loading}>
            <ActivityIndicator size="small" color={colors.accent} />
          </View>
        ) : (
          <HistoryList dialogs={dialogs} />
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
});
```

- [ ] **Step 4: Run test to verify it passes**

Run: `yarn test:run src/screens/__tests__/HomeScreen.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/screens/HomeScreen.tsx src/screens/__tests__/HomeScreen.test.tsx
git commit -m "feat(mobile): 添加 HomeScreen 页面"
```

---

## Chunk 4: Navigation Integration

**Files:**
- Modify: `mobile/src/navigation/TabNavigator.tsx`

---

### Task 7: Update TabNavigator to use HomeScreen

- [ ] **Step 1: Modify TabNavigator.tsx**

Replace:
```tsx
function HomeStackNavigator() {
  return (
    <HomeStack.Navigator screenOptions={{ headerShown: false }}>
      <HomeStack.Screen name="Home" component={PlaceholderScreen} />
    </HomeStack.Navigator>
  );
}
```

With:
```tsx
import { HomeScreen } from '../screens/HomeScreen';

function HomeStackNavigator() {
  return (
    <HomeStack.Navigator screenOptions={{ headerShown: false }}>
      <HomeStack.Screen name="Home" component={HomeScreen} />
    </HomeStack.Navigator>
  );
}
```

Also need to update the `ChatsStackNavigator` to handle the `ChatDetail` screen properly. The current implementation only has `Chats` screen but we need to support `ChatDetail`. However, since ChatDetail is not implemented yet, we can use a simple approach:

For now, the HistoryList navigation to ChatDetail will navigate to the Chats tab. The ChatDetail screen will be implemented in the chat module.

- [ ] **Step 2: Commit**

```bash
git add src/navigation/TabNavigator.tsx
git commit -m "feat(mobile): 集成 HomeScreen 到 TabNavigator"
```

---

## Chunk 5: Verify and Run

- [ ] **Step 1: Run all tests**

```bash
cd /home/luorome/software/CampusMind/mobile
yarn test:run
```

Expected: All tests pass

- [ ] **Step 2: Run TypeScript check**

```bash
yarn typecheck
```

Expected: No errors

- [ ] **Step 3: Verify build**

```bash
yarn android 2>&1 | head -50
# OR for Expo
yarn start 2>&1 | head -50
```

Expected: Build starts without errors

---

## Chunk 6: Update feature-list.json and docs

- [ ] **Step 1: Update feature-list.json status**

Set F-010, F-011, F-012, F-013 to "completed"

- [ ] **Step 2: Update progress-log.md**

Add entry for Home module completion

- [ ] **Step 3: Commit**

```bash
git add mobile/docs/feature-list.json mobile/docs/progress-log.md
git commit -m "docs(mobile): 更新 feature-list 和 progress-log"
```

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-14-home-module-plan.md`. Ready to execute?**
