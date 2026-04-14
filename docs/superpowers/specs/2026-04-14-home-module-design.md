# Home Module Design - CampusMind Mobile

**Date**: 2026-04-14
**Module**: Home (首页)
**Status**: Approved

## Overview

Implements the Home Tab of CampusMind mobile app: HeroBanner + FeatureGrid + HistoryList.

## Components

### HeroBanner

| Property | Value |
|----------|-------|
| Layout | Card (radius: 16px), full-width |
| Content | Placeholder image, "CampusMind" title, "你的智能校园助手" subtitle, 3 feature bullets |
| Image | Gradient placeholder (accent color → background) |
| Spacing | `cardPadding: 16px` |

**Reference**: `frontend/src/components/chat/EmptyState/index.tsx`

### FeatureGrid

| Property | Value |
|----------|-------|
| Layout | 2-column grid, gap: 12px |
| Tiles | 4 tiles: 新建对话, 知识库, 知识构建, 个人中心 |
| Icon | lucide-react-native: MessageCircle, BookOpen, FilePlus, User |
| Tile Style | Pressable, icon + text, rounded card |

**Navigation**:
- 新建对话 → `ChatsTab` (Chats screen)
- 知识库 → `KnowledgeTab` (KnowledgeList screen)
- 知识构建 → `HomeTab` → `KnowledgeBuild`
- 个人中心 → `ProfileTab`

### HistoryList

| Property | Value |
|----------|-------|
| Layout | FlatList, vertical |
| Item | MessageSquare icon + title + relative timestamp |
| Empty State | "暂无对话记录" placeholder |
| Click Action | Navigate to `ChatsTab` → `ChatDetail`, pass `dialogId` |

**Data**: `listDialogs()` from `GET /dialogs`

### HomeScreen

| Property | Value |
|----------|-------|
| Layout | SafeAreaView + ScrollView |
| Order | HeroBanner → FeatureGrid → HistoryList |
| API | Fetch dialog list on mount |

## File Structure

```
mobile/src/
├── components/home/
│   ├── HeroBanner.tsx
│   ├── FeatureGrid.tsx
│   ├── HistoryList.tsx
│   └── index.ts
├── screens/
│   └── HomeScreen.tsx
└── api/
    └── dialog.ts          # listDialogs, deleteDialog
```

## Dependencies

| Package | Purpose |
|---------|---------|
| lucide-react-native | Icons |
| date-fns + date-fns/locale/zh_cn | Time formatting |
| gradient (placeholder image) | Brand logo |

## Navigation Integration

`TabNavigator.tsx` HomeStackNavigator:
```tsx
<HomeStack.Screen name="Home" component={HomeScreen} />
<HomeStack.Screen name="KnowledgeBuild" component={PlaceholderScreen} />
```

## Design Tokens (from existing)

- `colors.background`: #F8F5ED
- `colors.accent`: #537D96
- `colors.text`: #3B3D3F
- `spacing[4]`: 16px
- `typography.textLg`: 18px
