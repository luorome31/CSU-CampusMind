# Knowledge 模块实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 mobile 端 Knowledge 模块（F-023 ~ F-029），包括知识库浏览、RAG 控制和文件查看功能

**Architecture:**
- 使用 Zustand 状态管理（与 Web 端一致）
- 嵌套 Stack Navigator 实现 KB→文件列表→文件详情的层级导航
- RAG 控制采用折叠收起方式，Header 按钮展开
- 复用现有 UI 组件（Card, Badge, Button）

**Tech Stack:** React Native, Zustand, React Navigation, react-native-markdown-display, lucide-react-native

---

## Chunk 1: KnowledgeListStore (F-023)

**Files:**
- Create: `mobile/src/features/knowledge/knowledgeStore.ts`
- Test: `mobile/src/features/knowledge/__tests__/knowledgeStore.test.ts`
- Modify: `mobile/src/features/index.ts` (export store)

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p mobile/src/features/knowledge/__tests__
```

- [ ] **Step 2: 编写测试文件**

```typescript
// mobile/src/features/knowledge/__tests__/knowledgeStore.test.ts
import { renderHook, act } from '@testing-library/react-native';
import { useKnowledgeStore } from '../knowledgeStore';

describe('useKnowledgeStore', () => {
  it('should have initial state', () => {
    const { result } = renderHook(() => useKnowledgeStore());
    expect(result.current.knowledgeBases).toEqual([]);
    expect(result.current.files).toEqual([]);
    expect(result.current.currentFileContent).toBe('');
    expect(result.current.isLoadingKBs).toBe(false);
  });
});
```

- [ ] **Step 3: 运行测试验证失败**

Run: `npm run test:run -- --testPathPattern="knowledgeStore" --testNamePattern="should have initial state"`
Expected: FAIL - store has undefined properties

- [ ] **Step 4: 实现 KnowledgeListStore**

```typescript
// mobile/src/features/knowledge/knowledgeStore.ts
import { create } from 'zustand';
import { knowledgeApi, KnowledgeBase, KnowledgeFile } from '../../api/knowledge';

interface KnowledgeState {
  knowledgeBases: KnowledgeBase[];
  currentKB: KnowledgeBase | null;
  files: KnowledgeFile[];
  currentFile: KnowledgeFile | null;
  currentFileContent: string;
  isLoadingKBs: boolean;
  isLoadingFiles: boolean;
  isLoadingContent: boolean;
  error: string | null;
}

interface KnowledgeActions {
  fetchKnowledgeBases: () => Promise<void>;
  fetchFiles: (kbId: string) => Promise<void>;
  fetchFileContent: (fileId: string) => Promise<void>;
  setCurrentKB: (kb: KnowledgeBase | null) => void;
  clearError: () => void;
}

type KnowledgeStore = KnowledgeState & KnowledgeActions;

export const useKnowledgeStore = create<KnowledgeStore>((set, get) => ({
  knowledgeBases: [],
  currentKB: null,
  files: [],
  currentFile: null,
  currentFileContent: '',
  isLoadingKBs: false,
  isLoadingFiles: false,
  isLoadingContent: false,
  error: null,

  fetchKnowledgeBases: async () => {
    set({ isLoadingKBs: true, error: null });
    try {
      const kb = await knowledgeApi.fetchKnowledgeBases();
      set({ knowledgeBases: kb, isLoadingKBs: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch', isLoadingKBs: false });
    }
  },

  fetchFiles: async (kbId: string) => {
    set({ isLoadingFiles: true, error: null });
    try {
      // API 暂缺，用空数组代替，等后端实现
      set({ files: [], isLoadingFiles: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch files', isLoadingFiles: false });
    }
  },

  fetchFileContent: async (fileId: string) => {
    set({ isLoadingContent: true, error: null });
    const file = get().files.find(f => f.id === fileId) || null;
    try {
      const content = await knowledgeApi.getFileContent(fileId);
      set({ currentFile: file, currentFileContent: content, isLoadingContent: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch content', isLoadingContent: false });
    }
  },

  setCurrentKB: (kb) => set({ currentKB: kb }),
  clearError: () => set({ error: null }),
}));
```

- [ ] **Step 5: 运行测试验证通过**

Run: `npm run test:run -- --testPathPattern="knowledgeStore"`
Expected: PASS

- [ ] **Step 6: 更新 features/index.ts 导出**

```typescript
// mobile/src/features/index.ts
export { useKnowledgeStore } from './knowledge/knowledgeStore';
```

- [ ] **Step 7: 提交**

```bash
git add mobile/src/features/knowledge/knowledgeStore.ts mobile/src/features/knowledge/__tests__/knowledgeStore.test.ts mobile/src/features/index.ts
git commit -m "feat(mobile): 添加 KnowledgeListStore 状态管理"
```

---

## Chunk 2: KnowledgeCard Component (F-024)

**Files:**
- Create: `mobile/src/components/knowledge/KnowledgeCard/KnowledgeCard.tsx`
- Create: `mobile/src/components/knowledge/KnowledgeCard/index.ts`
- Create: `mobile/src/components/knowledge/KnowledgeCard/__tests__/KnowledgeCard.test.tsx`

- [ ] **Step 1: 创建组件目录**

```bash
mkdir -p mobile/src/components/knowledge/KnowledgeCard/__tests__
```

- [ ] **Step 2: 编写测试**

```typescript
// mobile/src/components/knowledge/KnowledgeCard/__tests__/KnowledgeCard.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { KnowledgeCard } from '../KnowledgeCard';

describe('KnowledgeCard', () => {
  const mockKB = {
    id: '1',
    name: '测试知识库',
    description: '这是一个测试知识库',
    file_count: 5,
  };

  it('should render KB name and description', () => {
    const { getByText } = render(
      <KnowledgeCard
        knowledge={mockKB}
        fileCount={mockKB.file_count}
        onClick={() => {}}
      />
    );
    expect(getByText('测试知识库')).toBeTruthy();
    expect(getByText('这是一个测试知识库')).toBeTruthy();
    expect(getByText('5 个文件')).toBeTruthy();
  });

  it('should call onClick when pressed', () => {
    const onClick = jest.fn();
    const { getByText } = render(
      <KnowledgeCard
        knowledge={mockKB}
        fileCount={mockKB.file_count}
        onClick={onClick}
      />
    );
    fireEvent.press(getByText('测试知识库'));
    expect(onClick).toHaveBeenCalled();
  });
});
```

- [ ] **Step 3: 运行测试验证失败**

Run: `npm run test:run -- --testPathPattern="KnowledgeCard.test"`
Expected: FAIL - module not found

- [ ] **Step 4: 实现 KnowledgeCard**

```typescript
// mobile/src/components/knowledge/KnowledgeCard/KnowledgeCard.tsx
import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Card } from '../../ui';
import { Badge } from '../../ui/Badge';
import { colors, typography, spacing, elevation } from '../../../styles';

export interface KnowledgeCardProps {
  knowledge: {
    id: string;
    name: string;
    description?: string;
  };
  fileCount: number;
  onClick: () => void;
}

export const KnowledgeCard: React.FC<KnowledgeCardProps> = ({
  knowledge,
  fileCount,
  onClick,
}) => {
  return (
    <Pressable onPress={onClick}>
      <Card variant="elevated" padding="md" style={styles.card}>
        <View style={styles.header}>
          <Text style={styles.title} numberOfLines={1}>
            {knowledge.name}
          </Text>
          <Badge variant="info" style={styles.badge}>
            {fileCount} 个文件
          </Badge>
        </View>
        {knowledge.description && (
          <Text style={styles.description} numberOfLines={2}>
            {knowledge.description}
          </Text>
        )}
      </Card>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  card: {
    marginBottom: spacing[3],
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing[2],
  },
  title: {
    flex: 1,
    fontSize: typography.textLg,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    marginRight: spacing[2],
  },
  badge: {
    marginLeft: spacing[2],
  },
  description: {
    fontSize: typography.textSm,
    color: colors.textLight,
    lineHeight: typography.textSm * 1.5,
  },
});

export default KnowledgeCard;
```

```typescript
// mobile/src/components/knowledge/KnowledgeCard/index.ts
export { KnowledgeCard } from './KnowledgeCard';
export type { KnowledgeCardProps } from './KnowledgeCard';
```

- [ ] **Step 5: 运行测试验证通过**

Run: `npm run test:run -- --testPathPattern="KnowledgeCard.test"`
Expected: PASS

- [ ] **Step 6: 更新 components/index.ts 导出**

```typescript
// mobile/src/components/index.ts
export { KnowledgeCard } from './knowledge/KnowledgeCard';
```

- [ ] **Step 7: 提交**

```bash
git add mobile/src/components/knowledge/KnowledgeCard/
git commit -m "feat(mobile): 添加 KnowledgeCard 组件"
```

---

## Chunk 3: FileTable Component (F-025)

**Files:**
- Create: `mobile/src/components/knowledge/FileTable/FileTable.tsx`
- Create: `mobile/src/components/knowledge/FileTable/index.ts`
- Create: `mobile/src/components/knowledge/FileTable/__tests__/FileTable.test.tsx`

- [ ] **Step 1: 创建组件目录**

```bash
mkdir -p mobile/src/components/knowledge/FileTable/__tests__
```

- [ ] **Step 2: 编写测试**

```typescript
// mobile/src/components/knowledge/FileTable/__tests__/FileTable.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { FileTable } from '../FileTable';
import type { KnowledgeFile } from '../../../../api/knowledge';

describe('FileTable', () => {
  const mockFiles: KnowledgeFile[] = [
    {
      id: '1',
      kb_id: 'kb1',
      file_name: '测试文件.pdf',
      status: 'ready',
      create_time: '2024-01-01T00:00:00Z',
      update_time: '2024-01-01T00:00:00Z',
    },
    {
      id: '2',
      kb_id: 'kb1',
      file_name: '处理中文件.pdf',
      status: 'processing',
      create_time: '2024-01-02T00:00:00Z',
      update_time: '2024-01-02T00:00:00Z',
    },
  ];

  it('should render empty state when no files', () => {
    const { getByText } = render(
      <FileTable files={[]} onFileClick={() => {}} />
    );
    expect(getByText('暂无文件')).toBeTruthy();
  });

  it('should render file list', () => {
    const { getByText } = render(
      <FileTable files={mockFiles} onFileClick={() => {}} />
    );
    expect(getByText('测试文件.pdf')).toBeTruthy();
    expect(getByText('处理中文件.pdf')).toBeTruthy();
  });

  it('should render status badges', () => {
    const { getByText } = render(
      <FileTable files={mockFiles} onFileClick={() => {}} />
    );
    expect(getByText('就绪')).toBeTruthy();
    expect(getByText('处理中')).toBeTruthy();
  });

  it('should call onFileClick when file pressed', () => {
    const onFileClick = jest.fn();
    const { getByText } = render(
      <FileTable files={mockFiles} onFileClick={onFileClick} />
    );
    fireEvent.press(getByText('测试文件.pdf'));
    expect(onFileClick).toHaveBeenCalledWith(mockFiles[0]);
  });
});
```

- [ ] **Step 3: 运行测试验证失败**

Run: `npm run test:run -- --testPathPattern="FileTable.test"`
Expected: FAIL - module not found

- [ ] **Step 4: 实现 FileTable**

```typescript
// mobile/src/components/knowledge/FileTable/FileTable.tsx
import React from 'react';
import { View, Text, StyleSheet, FlatList, Pressable } from 'react-native';
import { Badge } from '../../ui/Badge';
import { colors, typography, spacing } from '../../../styles';
import type { KnowledgeFile } from '../../../api/knowledge';

export interface FileTableProps {
  files: KnowledgeFile[];
  onFileClick: (file: KnowledgeFile) => void;
}

const STATUS_LABELS: Record<KnowledgeFile['status'], string> = {
  pending: '待处理',
  processing: '处理中',
  ready: '就绪',
  verified: '已验证',
  error: '失败',
};

const STATUS_VARIANT: Record<KnowledgeFile['status'], 'success' | 'error' | 'warning' | 'info'> = {
  pending: 'warning',
  processing: 'info',
  ready: 'success',
  verified: 'success',
  error: 'error',
};

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

export const FileTable: React.FC<FileTableProps> = ({ files, onFileClick }) => {
  if (files.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>暂无文件</Text>
      </View>
    );
  }

  const renderItem = ({ item }: { item: KnowledgeFile }) => (
    <Pressable
      style={styles.row}
      onPress={() => onFileClick(item)}
      accessibilityRole="button"
      accessibilityLabel={`文件 ${item.file_name}`}
    >
      <View style={styles.nameCell}>
        <Text style={styles.fileName} numberOfLines={1}>
          {item.file_name}
        </Text>
      </View>
      <View style={styles.statusCell}>
        <Badge variant={STATUS_VARIANT[item.status]} size="sm">
          {STATUS_LABELS[item.status]}
        </Badge>
      </View>
      <View style={styles.dateCell}>
        <Text style={styles.dateText}>{formatDate(item.update_time)}</Text>
      </View>
    </Pressable>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerText}>文件名</Text>
        <Text style={styles.headerText}>状态</Text>
        <Text style={styles.headerText}>更新时间</Text>
      </View>
      {/* Body */}
      <FlatList
        data={files}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        scrollEnabled={false}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusLg,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    backgroundColor: colors.moodBg,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerText: {
    flex: 1,
    fontSize: typography.textXs,
    fontWeight: typography.fontMedium,
    color: colors.textLight,
  },
  row: {
    flexDirection: 'row',
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
    alignItems: 'center',
  },
  nameCell: {
    flex: 1,
    marginRight: spacing[2],
  },
  fileName: {
    fontSize: typography.textSm,
    color: colors.text,
  },
  statusCell: {
    width: 70,
    alignItems: 'center',
  },
  dateCell: {
    width: 80,
    alignItems: 'flex-end',
  },
  dateText: {
    fontSize: typography.textXs,
    color: colors.textMuted,
  },
  emptyContainer: {
    padding: spacing[8],
    alignItems: 'center',
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
});

export default FileTable;
```

```typescript
// mobile/src/components/knowledge/FileTable/index.ts
export { FileTable } from './FileTable';
export type { FileTableProps } from './FileTable';
```

- [ ] **Step 5: 运行测试验证通过**

Run: `npm run test:run -- --testPathPattern="FileTable.test"`
Expected: PASS

- [ ] **Step 6: 更新 components/index.ts 导出**

- [ ] **Step 7: 提交**

```bash
git add mobile/src/components/knowledge/FileTable/
git commit -m "feat(mobile): 添加 FileTable 组件"
```

---

## Chunk 4: FileContentViewer Component (F-026)

**Files:**
- Create: `mobile/src/components/knowledge/FileContentViewer/FileContentViewer.tsx`
- Create: `mobile/src/components/knowledge/FileContentViewer/index.ts`
- Create: `mobile/src/components/knowledge/FileContentViewer/__tests__/FileContentViewer.test.tsx`

- [ ] **Step 1: 创建组件目录**

```bash
mkdir -p mobile/src/components/knowledge/FileContentViewer/__tests__
```

- [ ] **Step 2: 编写测试**

```typescript
// mobile/src/components/knowledge/FileContentViewer/__tests__/FileContentViewer.test.tsx
import React from 'react';
import { render } from '@testing-library/react-native';
import { FileContentViewer } from '../FileContentViewer';

describe('FileContentViewer', () => {
  it('should render empty state when no content', () => {
    const { getByText } = render(
      <FileContentViewer content="" />
    );
    expect(getByText('暂无内容')).toBeTruthy();
  });

  it('should render content', () => {
    const { getByText } = render(
      <FileContentViewer content="# Hello World" />
    );
    expect(getByText('Hello World')).toBeTruthy();
  });

  it('should render filename if provided', () => {
    const { getByText } = render(
      <FileContentViewer content="test" fileName="test.txt" />
    );
    expect(getByText('test.txt')).toBeTruthy();
  });
});
```

- [ ] **Step 3: 运行测试验证失败**

Run: `npm run test:run -- --testPathPattern="FileContentViewer.test"`
Expected: FAIL - module not found

- [ ] **Step 4: 实现 FileContentViewer**

```typescript
// mobile/src/components/knowledge/FileContentViewer/FileContentViewer.tsx
import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Badge } from '../../ui/Badge';
import { colors, typography, spacing } from '../../../styles';

export interface FileContentViewerProps {
  content: string;
  fileName?: string;
}

export const FileContentViewer: React.FC<FileContentViewerProps> = ({
  content,
  fileName,
}) => {
  if (!content) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>暂无内容</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        {fileName && <Text style={styles.fileName}>{fileName}</Text>}
        <Badge variant="info" size="sm">只读</Badge>
      </View>
      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        <Text style={styles.markdownText}>{content}</Text>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusLg,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  fileName: {
    flex: 1,
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: spacing[4],
  },
  markdownText: {
    fontSize: typography.textSm,
    color: colors.text,
    lineHeight: typography.textSm * 1.8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing[8],
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
});

export default FileContentViewer;
```

```typescript
// mobile/src/components/knowledge/FileContentViewer/index.ts
export { FileContentViewer } from './FileContentViewer';
export type { FileContentViewerProps } from './FileContentViewer';
```

- [ ] **Step 5: 运行测试验证通过**

Run: `npm run test:run -- --testPathPattern="FileContentViewer.test"`
Expected: PASS

- [ ] **Step 6: 更新 components/index.ts 导出**

- [ ] **Step 7: 提交**

```bash
git add mobile/src/components/knowledge/FileContentViewer/
git commit -m "feat(mobile): 添加 FileContentViewer 组件"
```

---

## Chunk 5: RAGSwitch Component (F-027)

**Files:**
- Create: `mobile/src/components/knowledge/RAGSwitch/RAGSwitch.tsx`
- Create: `mobile/src/components/knowledge/RAGSwitch/index.ts`
- Create: `mobile/src/components/knowledge/RAGSwitch/__tests__/RAGSwitch.test.tsx`

- [ ] **Step 1: 创建组件目录**

```bash
mkdir -p mobile/src/components/knowledge/RAGSwitch/__tests__
```

- [ ] **Step 2: 编写测试**

```typescript
// mobile/src/components/knowledge/RAGSwitch/__tests__/RAGSwitch.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { RAGSwitch } from '../RAGSwitch';
import type { KnowledgeBase } from '../../../../api/knowledge';

describe('RAGSwitch', () => {
  const mockKBs: KnowledgeBase[] = [
    { id: '1', name: 'KB1', description: '', user_id: 'u1', create_time: '', update_time: '', file_count: 3 },
    { id: '2', name: 'KB2', description: '', user_id: 'u1', create_time: '', update_time: '', file_count: 5 },
  ];

  it('should render RAG toggle', () => {
    const { getByText } = render(
      <RAGSwitch
        enabled={true}
        selectedIds={[]}
        knowledgeBases={mockKBs}
        onToggle={() => {}}
        onSelect={() => {}}
      />
    );
    expect(getByText('RAG 检索')).toBeTruthy();
  });

  it('should render knowledge bases', () => {
    const { getByText } = render(
      <RAGSwitch
        enabled={true}
        selectedIds={[]}
        knowledgeBases={mockKBs}
        onToggle={() => {}}
        onSelect={() => {}}
      />
    );
    expect(getByText('KB1')).toBeTruthy();
    expect(getByText('KB2')).toBeTruthy();
  });

  it('should call onToggle when switch pressed', () => {
    const onToggle = jest.fn();
    const { getByText } = render(
      <RAGSwitch
        enabled={true}
        selectedIds={[]}
        knowledgeBases={mockKBs}
        onToggle={onToggle}
        onSelect={() => {}}
      />
    );
    fireEvent(getByText('RAG 检索'), 'press');
    expect(onToggle).toHaveBeenCalled();
  });
});
```

- [ ] **Step 3: 运行测试验证失败**

Run: `npm run test:run -- --testPathPattern="RAGSwitch.test"`
Expected: FAIL - module not found

- [ ] **Step 4: 实现 RAGSwitch**

```typescript
// mobile/src/components/knowledge/RAGSwitch/RAGSwitch.tsx
import React from 'react';
import { View, Text, StyleSheet, Pressable, ScrollView } from 'react-native';
import { ChevronDown, ChevronUp, Check } from 'lucide-react-native';
import { Card } from '../../ui';
import { colors, typography, spacing } from '../../../styles';
import type { KnowledgeBase } from '../../../api/knowledge';

export interface RAGSwitchProps {
  enabled: boolean;
  selectedIds: string[];
  knowledgeBases: KnowledgeBase[];
  onToggle: () => void;
  onSelect: (id: string) => void;
}

export const RAGSwitch: React.FC<RAGSwitchProps> = ({
  enabled,
  selectedIds,
  knowledgeBases,
  onToggle,
  onSelect,
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false);

  return (
    <Card variant="default" padding="sm" style={styles.container}>
      <View style={styles.header}>
        <Pressable style={styles.toggleRow} onPress={onToggle}>
          <View style={[styles.switch, enabled && styles.switchEnabled]}>
            <View style={[styles.switchThumb, enabled && styles.switchThumbEnabled]} />
          </View>
          <Text style={styles.toggleLabel}>RAG 检索</Text>
        </Pressable>
        <Pressable
          style={styles.expandButton}
          onPress={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? (
            <ChevronUp size={20} color={colors.textLight} />
          ) : (
            <ChevronDown size={20} color={colors.textLight} />
          )}
        </Pressable>
      </View>

      {isExpanded && (
        <ScrollView style={styles.kbList}>
          {knowledgeBases.length === 0 ? (
            <Text style={styles.emptyText}>暂无可用知识库</Text>
          ) : (
            knowledgeBases.map((kb) => {
              const isSelected = selectedIds.includes(kb.id);
              return (
                <Pressable
                  key={kb.id}
                  style={[styles.kbItem, isSelected && styles.kbItemSelected]}
                  onPress={() => onSelect(kb.id)}
                >
                  <View style={styles.kbInfo}>
                    <Text style={styles.kbName} numberOfLines={1}>
                      {kb.name}
                    </Text>
                    <Text style={styles.kbFileCount}>{kb.file_count} 个文件</Text>
                  </View>
                  {isSelected && (
                    <Check size={18} color={colors.accent} />
                  )}
                </Pressable>
              );
            })
          )}
        </ScrollView>
      )}

      {selectedIds.length > 0 && (
        <Text style={styles.selectedText}>
          已选择 {selectedIds.length} 个知识库
        </Text>
      )}
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing[4],
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  switch: {
    width: 44,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.textMuted,
    padding: 2,
    marginRight: spacing[3],
  },
  switchEnabled: {
    backgroundColor: colors.accent,
  },
  switchThumb: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: colors.backgroundCard,
  },
  switchThumbEnabled: {
    transform: [{ translateX: 20 }],
  },
  toggleLabel: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
  },
  expandButton: {
    padding: spacing[2],
  },
  kbList: {
    marginTop: spacing[3],
    maxHeight: 200,
  },
  kbItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[2],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  kbItemSelected: {
    backgroundColor: colors.accentLight,
    borderRadius: elevation.radiusMd,
  },
  kbInfo: {
    flex: 1,
  },
  kbName: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
  },
  kbFileCount: {
    fontSize: typography.textXs,
    color: colors.textMuted,
    marginTop: 2,
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
    textAlign: 'center',
    padding: spacing[4],
  },
  selectedText: {
    fontSize: typography.textXs,
    color: colors.accent,
    marginTop: spacing[2],
  },
});

export default RAGSwitch;
```

```typescript
// mobile/src/components/knowledge/RAGSwitch/index.ts
export { RAGSwitch } from './RAGSwitch';
export type { RAGSwitchProps } from './RAGSwitch';
```

- [ ] **Step 5: 运行测试验证通过**

Run: `npm run test:run -- --testPathPattern="RAGSwitch.test"`
Expected: PASS

- [ ] **Step 6: 更新 components/index.ts 导出**

- [ ] **Step 7: 提交**

```bash
git add mobile/src/components/knowledge/RAGSwitch/
git commit -m "feat(mobile): 添加 RAGSwitch 组件"
```

---

## Chunk 6: Screen Components (F-028)

**Files:**
- Create: `mobile/src/screens/KnowledgeScreen.tsx`
- Create: `mobile/src/screens/KnowledgeDetailScreen.tsx`
- Create: `mobile/src/screens/FileDetailScreen.tsx`
- Modify: `mobile/src/screens/index.ts`

- [ ] **Step 1: 实现 KnowledgeScreen**

```typescript
// mobile/src/screens/KnowledgeScreen.tsx
import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, Text, Pressable, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Plus } from 'lucide-react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useKnowledgeStore } from '../features/knowledge/knowledgeStore';
import { useChatStore } from '../features/chat/chatStore';
import { KnowledgeCard } from '../components/knowledge/KnowledgeCard';
import { RAGSwitch } from '../components/knowledge/RAGSwitch';
import { colors, spacing } from '../styles';
import type { KnowledgeStackParamList } from '../navigation/types';
import type { KnowledgeBase } from '../api/knowledge';

type NavigationProp = NativeStackNavigationProp<KnowledgeStackParamList>;

export function KnowledgeScreen() {
  const navigation = useNavigation<NavigationProp>();
  const [isRagExpanded, setIsRagExpanded] = useState(false);

  const { knowledgeBases, isLoadingKBs, fetchKnowledgeBases } = useKnowledgeStore();
  const enableRag = useChatStore((s) => s.enableRag);
  const toggleRag = useChatStore((s) => s.toggleRag);
  const currentKnowledgeIds = useChatStore((s) => s.currentKnowledgeIds);
  const setCurrentKnowledgeIds = useChatStore((s) => s.setCurrentKnowledgeIds);

  useEffect(() => {
    fetchKnowledgeBases();
  }, [fetchKnowledgeBases]);

  const handleToggleRag = () => {
    toggleRag();
  };

  const handleSelectKB = (kbId: string) => {
    const isSelected = currentKnowledgeIds.includes(kbId);
    if (isSelected) {
      setCurrentKnowledgeIds(currentKnowledgeIds.filter(id => id !== kbId));
    } else {
      setCurrentKnowledgeIds([...currentKnowledgeIds, kbId]);
    }
  };

  const handleKBClick = (kb: KnowledgeBase) => {
    navigation.navigate('KnowledgeDetail', { kbId: kb.id });
  };

  const handleBuildPress = () => {
    // 跳转到 HomeTab 的 KnowledgeBuild
    navigation.getParent()?.navigate('HomeTab', {
      screen: 'KnowledgeBuild',
    });
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>知识库</Text>
        <Pressable style={styles.buildButton} onPress={handleBuildPress}>
          <Plus size={20} color={colors.accent} />
          <Text style={styles.buildButtonText}>构建</Text>
        </Pressable>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        {/* RAG Switch */}
        <RAGSwitch
          enabled={enableRag}
          selectedIds={currentKnowledgeIds}
          knowledgeBases={knowledgeBases}
          onToggle={handleToggleRag}
          onSelect={handleSelectKB}
        />

        {/* KB List */}
        {isLoadingKBs ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : knowledgeBases.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>暂无知识库</Text>
            <Text style={styles.emptySubtext}>点击右上角「构建」创建知识库</Text>
          </View>
        ) : (
          <View style={styles.kbList}>
            {knowledgeBases.map((kb) => (
              <KnowledgeCard
                key={kb.id}
                knowledge={kb}
                fileCount={kb.file_count}
                onClick={() => handleKBClick(kb)}
              />
            ))}
          </View>
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[3],
  },
  title: {
    fontSize: typography.textXl,
    fontWeight: typography.fontBold,
    color: colors.text,
  },
  buildButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing[3],
    paddingVertical: spacing[2],
    backgroundColor: colors.accentLight,
    borderRadius: elevation.radiusMd,
  },
  buildButtonText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.accent,
    marginLeft: spacing[1],
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: spacing[4],
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: spacing[8],
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: spacing[8],
  },
  emptyText: {
    fontSize: typography.textMd,
    color: colors.textLight,
    marginBottom: spacing[2],
  },
  emptySubtext: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
  kbList: {
    gap: spacing[3],
  },
});

export default KnowledgeScreen;
```

- [ ] **Step 2: 实现 KnowledgeDetailScreen**

```typescript
// mobile/src/screens/KnowledgeDetailScreen.tsx
import React, { useEffect } from 'react';
import { View, StyleSheet, Text, Pressable, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ChevronLeft } from 'lucide-react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { NativeStackNavigationProp, NativeStackScreenProps } from '@react-navigation/native-stack';
import { useKnowledgeStore } from '../features/knowledge/knowledgeStore';
import { FileTable } from '../components/knowledge/FileTable';
import { colors, typography, spacing } from '../styles';
import type { KnowledgeStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<KnowledgeStackParamList, 'KnowledgeDetail'>;

export function KnowledgeDetailScreen({ navigation, route }: Props) {
  const { kbId } = route.params;
  const { knowledgeBases, files, currentKB, isLoadingFiles, fetchFiles, setCurrentKB } = useKnowledgeStore();

  useEffect(() => {
    const kb = knowledgeBases.find(k => k.id === kbId);
    if (kb) {
      setCurrentKB(kb);
    }
    fetchFiles(kbId);
  }, [kbId, knowledgeBases, setCurrentKB, fetchFiles]);

  const handleBack = () => {
    navigation.goBack();
  };

  const handleFileClick = (file: { id: string }) => {
    navigation.navigate('FileDetail', { fileId: file.id });
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={handleBack} style={styles.backButton}>
          <ChevronLeft size={24} color={colors.text} />
        </Pressable>
        <Text style={styles.title} numberOfLines={1}>
          {currentKB?.name || '知识库'}
        </Text>
        <View style={styles.placeholder} />
      </View>

      {/* Content */}
      <View style={styles.content}>
        {isLoadingFiles ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FileTable files={files} onFileClick={handleFileClick} />
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[3],
  },
  backButton: {
    padding: spacing[2],
  },
  title: {
    flex: 1,
    fontSize: typography.textMd,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    textAlign: 'center',
  },
  placeholder: {
    width: 40,
  },
  content: {
    flex: 1,
    padding: spacing[4],
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default KnowledgeDetailScreen;
```

- [ ] **Step 3: 实现 FileDetailScreen**

```typescript
// mobile/src/screens/FileDetailScreen.tsx
import React, { useEffect } from 'react';
import { View, StyleSheet, Text, Pressable, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ChevronLeft } from 'lucide-react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useKnowledgeStore } from '../features/knowledge/knowledgeStore';
import { FileContentViewer } from '../components/knowledge/FileContentViewer';
import { colors, typography, spacing } from '../styles';
import type { KnowledgeStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<KnowledgeStackParamList, 'FileDetail'>;

export function FileDetailScreen({ navigation, route }: Props) {
  const { fileId } = route.params;
  const { currentFile, currentFileContent, isLoadingContent, fetchFileContent, files } = useKnowledgeStore();

  useEffect(() => {
    fetchFileContent(fileId);
  }, [fileId, fetchFileContent]);

  const handleBack = () => {
    navigation.goBack();
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={handleBack} style={styles.backButton}>
          <ChevronLeft size={24} color={colors.text} />
        </Pressable>
        <Text style={styles.title} numberOfLines={1}>
          {currentFile?.file_name || '文件详情'}
        </Text>
        <View style={styles.placeholder} />
      </View>

      {/* Content */}
      <View style={styles.content}>
        {isLoadingContent ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FileContentViewer content={currentFileContent} fileName={currentFile?.file_name} />
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[3],
  },
  backButton: {
    padding: spacing[2],
  },
  title: {
    flex: 1,
    fontSize: typography.textMd,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    textAlign: 'center',
  },
  placeholder: {
    width: 40,
  },
  content: {
    flex: 1,
    padding: spacing[4],
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default FileDetailScreen;
```

- [ ] **Step 4: 更新 screens/index.ts 导出**

```typescript
// mobile/src/screens/index.ts
export { KnowledgeScreen } from './KnowledgeScreen';
export { KnowledgeDetailScreen } from './KnowledgeDetailScreen';
export { FileDetailScreen } from './FileDetailScreen';
```

- [ ] **Step 5: 提交**

```bash
git add mobile/src/screens/KnowledgeScreen.tsx mobile/src/screens/KnowledgeDetailScreen.tsx mobile/src/screens/FileDetailScreen.tsx mobile/src/screens/index.ts
git commit -m "feat(mobile): 添加 Knowledge 模块页面组件"
```

---

## Chunk 7: Navigation Integration (F-028, F-029)

**Files:**
- Modify: `mobile/src/navigation/TabNavigator.tsx`

- [ ] **Step 1: 更新 TabNavigator 添加 Knowledge 导航栈**

```typescript
// mobile/src/navigation/TabNavigator.tsx
// ... existing imports ...
import { KnowledgeScreen } from '../screens/KnowledgeScreen';
import { KnowledgeDetailScreen } from '../screens/KnowledgeDetailScreen';
import { FileDetailScreen } from '../screens/FileDetailScreen';

function KnowledgeStackNavigator() {
  return (
    <KnowledgeStack.Navigator screenOptions={{ headerShown: false }}>
      <KnowledgeStack.Screen name="KnowledgeList" component={KnowledgeScreen} />
      <KnowledgeStack.Screen name="KnowledgeDetail" component={KnowledgeDetailScreen} />
      <KnowledgeStack.Screen name="FileDetail" component={FileDetailScreen} />
    </KnowledgeStack.Navigator>
  );
}

// ... rest of file remains the same ...
```

- [ ] **Step 2: 提交**

```bash
git add mobile/src/navigation/TabNavigator.tsx
git commit -m "feat(mobile): 集成 Knowledge 模块到 TabNavigator"
```

---

## 验证步骤

完成所有 Chunk 后，运行以下验证：

```bash
# 类型检查
npm run typecheck

# 运行所有测试
npm run test:run

# 构建验证
npm run build
```

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-15-knowledge-module-implementation.md`. Ready to execute?**
