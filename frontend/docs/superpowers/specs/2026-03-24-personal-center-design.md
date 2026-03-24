# Personal Center Design Specification

**Date:** 2026-03-24
**Status:** Approved
**Author:** Claude

---

## 1. Overview

Personal Center (个人中心) is a protected route (`/profile`) providing users with profile management, usage statistics, and session management for CampusMind.

---

## 2. Page Structure

```
┌─────────────────────────────────────────────────────┐
│  Header: "个人中心"                                  │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌────────────────────────────┐  │
│  │   Avatar    │  │  Profile Section            │  │
│  │   Upload    │  │  - Display name (editable)  │  │
│  │             │  │  - Username (readonly)       │  │
│  └──────────────┘  │  - Email (editable)        │  │
│                    │  - Phone (editable)        │  │
│                    └────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  Usage Statistics                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │对话数   │ │消息数   │ │知识库数 │ │注册时间 │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
├─────────────────────────────────────────────────────┤
│  Active Sessions                                    │
│  ┌─────────────────────────────────────────────────┐│
│  │ Device • Location • Time                    [登出]││
│  └─────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────┤
│  [退出登录]                                         │
└─────────────────────────────────────────────────────┘
```

---

## 3. Backend Changes

### 3.1 New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user profile |
| PATCH | `/api/v1/users/me` | Update profile (display_name, email, phone) |
| GET | `/api/v1/auth/sessions` | List active sessions |
| DELETE | `/api/v1/auth/sessions/{session_id}` | Revoke specific session |

### 3.2 Data Models

**User Profile Update Schema:**
```python
class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
```

**Session Schema:**
```python
class SessionResponse(BaseModel):
    session_id: str
    device: str
    location: str
    created_at: str
    is_current: bool
```

### 3.3 Repository Changes

- Add `UserRepository.get_by_id()` method
- Add `UserRepository.update()` method
- Add session tracking to JWT/session management

---

## 4. Frontend Components

### 4.1 File Structure

```
src/features/profile/
├── ProfilePage.tsx              # Main page
├── ProfilePage.css              # Page styles
├── profileStore.ts              # Zustand store
├── profileStore.test.ts         # Store tests
├── components/
│   ├── ProfileCard.tsx          # Avatar + profile form
│   ├── ProfileCard.css
│   ├── StatsGrid.tsx            # Usage statistics
│   ├── StatsGrid.css
│   ├── SessionList.tsx          # Sessions list
│   ├── SessionList.css
│   └── SessionItem.tsx          # Single session row
├── api/
│   └── profile.ts               # API client
└── types.ts                    # TypeScript types
```

### 4.2 State Management

**profileStore:**
```typescript
interface ProfileState {
  user: User | null;
  stats: UsageStats | null;
  sessions: Session[];
  isLoading: boolean;
  error: string | null;
}
```

**Types:**
```typescript
interface User {
  user_id: string;
  username: string;
  display_name: string;
  email: string;
  phone: string;
  avatar_url: string | null;
  created_at: string;
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
  created_at: string;
  is_current: boolean;
}
```

---

## 5. API Endpoints (Frontend)

| Method | Function | Description |
|--------|----------|-------------|
| GET | `getProfile()` | Fetch user profile |
| PATCH | `updateProfile(data)` | Update profile fields |
| GET | `getSessions()` | List active sessions |
| DELETE | `revokeSession(id)` | Sign out specific session |

---

## 6. Design Tokens

Use existing design tokens from `src/styles/tokens/`:

| Token | Usage |
|-------|-------|
| `--color-bg-surface` | Card backgrounds |
| `--color-accent` | Active states, buttons |
| `--color-text-primary` | Headings |
| `--color-text-secondary` | Body text |
| `--radius-lg` | Card border radius |
| `--space-4` | Card padding |

---

## 7. Acceptance Criteria

| # | Criteria |
|---|----------|
| 1 | Profile displays with avatar, display name, username, email, phone |
| 2 | Display name is editable inline |
| 3 | Email and phone are editable |
| 4 | Username is read-only |
| 5 | Stats show conversation count, message count, knowledge base count, join date |
| 6 | Sessions list shows device, location, time for each session |
| 7 | Per-session sign out button works |
| 8 | "Sign out all" or individual session revocation |
| 9 | Logout button clears session and redirects to login |
| 10 | All text in Chinese |
| 11 | Responsive layout (mobile-friendly) |
| 12 | All new code has unit tests |
| 13 | Build passes without errors |

---

## 8. Implementation Order

1. Backend: Add user profile endpoints
2. Backend: Add session management endpoints
3. Frontend: Add profile API client
4. Frontend: Add profileStore
5. Frontend: Build ProfileCard component
6. Frontend: Build StatsGrid component
7. Frontend: Build SessionList component
8. Frontend: Build ProfilePage and routing
9. Frontend: Add unit tests
10. Integration testing and styling polish
