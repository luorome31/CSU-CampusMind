# Knowledge Build Module Design (Mobile)

## 1. Navigation Structure

```
HomeStack:
├── Home (HeroBanner + FeatureGrid + HistoryList)
└── KnowledgeBuild (BuildScreen - full screen push)
```

- Back gesture returns to Home
- Screen header contains only back arrow and segmented control (no title text)
- Tab Bar remains on HomeTab visually

---

## 2. BuildScreen Layout

```
┌─────────────────────────────────────┐
│ ←back  [ 爬取任务 | 审核队列 ]      │  ← Header
├─────────────────────────────────────┤
│                                     │
│  Phase Content (Crawl or Review)   │
│                                     │
│                                     │
└─────────────────────────────────────┘
```

**Header structure:**
- Left: Back chevron/arrow
- Center: Segmented Control (the two tabs)
- No title text - the tabs serve as navigation

---

## 3. Crawl Phase

```
┌─────────────────────────────────────┐
│ [ 爬取任务 | 审核队列 ]             │
├─────────────────────────────────────┤
│                                     │
│  知识库选择                         │
│  ┌─────────────────────────────┐   │
│  │ 选择知识库            ▼    │   │
│  └─────────────────────────────┘   │
│                                     │
│  URL列表                            │
│  ┌─────────────────────────────┐   │
│  │ 输入URL，每行一个           │   │
│  │                             │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  [开始爬取]  [批量导入]  [清空]    │
│                                     │
├─────────────────────────────────────┤
│  任务列表                          │
│  ┌─────────────────────────────┐   │
│  │ Task Card 1        成功    │   │
│  │ ████████████░░░░  8/10     │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Task Card 2        处理中   │   │
│  │ ██████░░░░░░░░░░  3/10     │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Components:**
- **KB Selector**: Dropdown/picker with knowledge bases
- **URL TextArea**: Multi-line input for URLs
- **Action Buttons**: Primary "开始爬取", Secondary "批量导入", Ghost "清空"
- **TaskList**: Scrollable list of TaskCards

---

## 4. Review Phase

**Default state (has pending files - auto-select first file):**
```
┌─────────────────────────────────────┐
│ [ 爬取任务 | 审核队列 ]             │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 📋 待审核文件 (3)           │ ← 点击弹出Modal │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 文件名.md           [编辑][预览]│
│  ├─────────────────────────────┤   │
│  │                             │   │
│  │   文件内容...                │   │
│  │                             │   │
│  ├─────────────────────────────┤   │
│  │ [保存]           [确认索引] │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Empty state (no pending files):**
```
┌─────────────────────────────────────┐
│ [ 爬取任务 | 审核队列 ]             │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 📋 待审核文件 (0)           │ ← badge为0时不可点击 │
│  └─────────────────────────────┘   │
│                                     │
│                                     │
│         暂无待审核文件               │
│                                     │
│                                     │
└─────────────────────────────────────┘
```

**File Selection Modal:**
```
┌─────────────────────────────────────┐
│                                     │
│  选择文件                    ✕      │
│  ─────────────────────────────────  │
│                                     │
│  📄 文件1.md                  04-14│
│  ─────────────────────────────────  │
│  📄 文件2.md                  04-13│
│  ─────────────────────────────────  │
│  📄 文件3.md                  04-12│
│                                     │
│  ─────────────────────────────────  │
│           [取消]                    │
│                                     │
└─────────────────────────────────────┘
```

---

## 5. Interaction Flow

### Crawl Tab
1. User selects a knowledge base from dropdown
2. User enters URLs (one per line) in textarea
3. Clicks "开始爬取" → creates crawl task, starts polling
4. Task cards appear showing progress (3s polling interval)
5. "批量导入" → opens modal for batch URL import
6. "清空" → clears URL textarea

### Review Tab
1. Click "审核队列" tab → auto-fetches pending files, displays first file
2. "待审核文件 (N)" button shows badge with count
3. Click button → opens modal with full file list
4. Select file from list → modal closes, selected file content shown
5. Edit/Preview toggle switches between edit mode and rendered markdown
6. "保存" → saves edited content
7. "确认索引" → triggers indexing, removes file from pending list

---

## 6. Component Structure

```
features/build/
├── buildStore.ts          # Zustand store (poll interval, file state)
├── api/
│   └── crawl.ts          # Crawl API client
screens/
└── BuildScreen.tsx        # Main screen with segmented control
components/build/
├── SegmentedControl.tsx   # Tab switcher (Crawl | Review)
├── CrawlTab/
│   ├── CrawlPanel.tsx     # Form (KB select + URL textarea)
│   ├── UrlImportModal.tsx  # Batch URL import modal
│   ├── TaskList.tsx       # Task cards container
│   └── TaskCard.tsx       # Individual task with progress
└── ReviewTab/
    ├── FileSelectModal.tsx # Modal for selecting pending files
    ├── ReviewInbox.tsx    # Pending files button with badge
    └── ReviewEditor.tsx    # Content editor with save/index
```

---

## 7. API Integration

Based on `frontend/src/api/crawl.ts` and `buildStore.ts`:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/crawl/batch-with-knowledge` | Submit crawl task |
| GET | `/crawl/tasks` | List all tasks |
| GET | `/crawl/tasks/{taskId}` | Poll task progress |
| DELETE | `/crawl/tasks/{taskId}` | Delete task |
| POST | `/crawl/tasks/{taskId}/retry-failed` | Retry failed URLs |
| GET | `/knowledge_file/pending_verify` | List pending review files |
| GET | `/knowledge_file/{fileId}/content` | Get file content |
| PUT | `/knowledge_file/{fileId}/content` | Update file content |
| POST | `/knowledge_file/{fileId}/trigger_index` | Trigger indexing |

---

## 8. Mobile-Specific Adaptations

| Web Feature | Mobile Adaptation |
|-------------|------------------|
| Side-by-side Review layout | Stacked: File button → Modal → Editor below |
| Hover states | Press feedback with opacity |
| Large textarea | Full-width, 6-8 rows visible |
| Batch import modal | Full-screen modal with URL list |
| Markdown toolbar | Simple icon buttons row above editor |

---

## 9. Design Tokens

Using existing mobile design system:

- **Colors**: `colors.background`, `colors.accent`, `colors.text`, etc.
- **Spacing**: `spacing[4]` (16px) for padding, `spacing[3]` (12px) for gaps
- **Radius**: `elevation.radiusLg` (16px) for cards and pills
- **Shadows**: `elevation.shadowCard` for cards

---

## 10. Status



- [x] Design approved by user
- [ ] Implementation plan created
- [ ] Build module implemented
- [ ] Tests written
