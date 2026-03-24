# Personal Center Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Personal Center feature with profile management, usage statistics, and session management.

**Architecture:**
- Backend: Add `/api/v1/users/me` and `/api/v1/auth/sessions` endpoints following existing repository patterns
- Frontend: Create `src/features/profile/` with ProfilePage, profileStore, and components following existing feature patterns

**Tech Stack:** React + TypeScript + Zustand + FastAPI + SQLModel

---

## Chunk 1: Backend - User Repository & Profile API

### Files

- Create: `backend/app/repositories/user_repository.py`
- Modify: `backend/app/api/v1/__init__.py` (add router)
- Create: `backend/app/api/v1/user.py`
- Modify: `backend/app/database/models/user.py` (already exists)

### Steps

- [ ] **Step 1: Create UserRepository**

```python
# backend/app/repositories/user_repository.py
"""
User Repository - User profile access with authorization.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User


class UserRepository:
    """Repository for user profile operations."""

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID."""
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        session: AsyncSession,
        user_id: str,
        display_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Optional[User]:
        """Update user profile fields."""
        user = await UserRepository.get_by_id(session, user_id)
        if not user:
            return None

        if display_name is not None:
            user.display_name = display_name
        if email is not None:
            user.email = email
        if phone is not None:
            user.phone = phone

        user.updated_at = datetime.now()
        await session.commit()
        await session.refresh(user)
        return user
```

- [ ] **Step 2: Create user API router**

```python
# backend/app/api/v1/user.py
"""
User API - User profile management endpoints
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.repositories.user_repository import UserRepository
from app.api.dependencies import get_current_user
from app.database.session import async_session_maker


router = APIRouter(prefix="/users", tags=["User"])


class UserProfileResponse(BaseModel):
    id: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


@router.get("/me", response_model=UserProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile."""
    user_id = current_user["user_id"]
    async with async_session_maker() as session:
        user = await UserRepository.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserProfileResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
        )


@router.patch("/me", response_model=UserProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile."""
    user_id = current_user["user_id"]
    async with async_session_maker() as session:
        user = await UserRepository.update(
            session,
            user_id,
            display_name=request.display_name,
            email=request.email,
            phone=request.phone,
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserProfileResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
        )
```

- [ ] **Step 3: Register router in API v1**

Modify `backend/app/api/v1/__init__.py` to include the user router:
```python
from app.api.v1.user import router as user_router
# ... in create_database():
router.include_router(user_router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/repositories/user_repository.py backend/app/api/v1/user.py backend/app/api/v1/__init__.py
git commit -m "feat(backend): add user profile API endpoints"
```

---

## Chunk 2: Backend - Session Management API

### Files

- Modify: `backend/app/core/session/factory.py` (add session tracking)
- Create: `backend/app/api/v1/session.py`

### Steps

- [ ] **Step 1: Check existing session factory**

Read `backend/app/core/session/factory.py` to understand current session management:

```python
# backend/app/core/session/factory.py
# Check if there's session storage mechanism we can leverage
# Likely uses Redis for session storage
```

- [ ] **Step 2: Create session API router**

```python
# backend/app/api/v1/session.py
"""
Session API - Active session management endpoints
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.api.dependencies import get_current_user


router = APIRouter(prefix="/auth/sessions", tags=["Session"])


class SessionResponse(BaseModel):
    session_id: str
    device: str
    location: str
    created_at: str
    is_current: bool


# Placeholder - actual implementation depends on session factory
async def get_user_sessions(user_id: str) -> List[SessionResponse]:
    """Get active sessions for user from session storage."""
    # TODO: Implement based on actual session storage
    return []


async def revoke_session(user_id: str, session_id: str) -> bool:
    """Revoke a specific session."""
    # TODO: Implement based on actual session storage
    return True


@router.get("", response_model=List[SessionResponse])
async def list_sessions(current_user: dict = Depends(get_current_user)):
    """List all active sessions for current user."""
    user_id = current_user["user_id"]
    sessions = await get_user_sessions(user_id)
    return sessions


@router.delete("/{session_id}")
async def revoke_session_endpoint(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Revoke a specific session."""
    user_id = current_user["user_id"]
    success = await revoke_session(user_id, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}
```

- [ ] **Step 2b: Check how sessions are tracked in factory**

Read `backend/app/core/session/factory.py` and related files to understand session storage.

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/session.py
git commit -m "feat(backend): add session management API endpoints"
```

---

## Chunk 3: Frontend - Profile API Client

### Files

- Create: `frontend/src/features/profile/api/profile.ts`
- Create: `frontend/src/features/profile/types.ts`

### Steps

- [ ] **Step 1: Create types**

```typescript
# frontend/src/features/profile/types.ts
export interface User {
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

export interface UsageStats {
  conversation_count: number;
  message_count: number;
  knowledge_base_count: number;
  join_date: string;
}

export interface Session {
  session_id: string;
  device: string;
  location: string;
  created_at: string;
  is_current: boolean;
}

export interface UpdateProfileData {
  display_name?: string;
  email?: string;
  phone?: string;
}
```

- [ ] **Step 2: Create API client**

```typescript
# frontend/src/features/profile/api/profile.ts
import { apiClient } from '../../../api/client';
import { User, Session, UpdateProfileData } from '../types';

export const profileApi = {
  getProfile: () =>
    apiClient.get<User>('/users/me'),

  updateProfile: (data: UpdateProfileData) =>
    apiClient.patch<User>('/users/me', data),

  getSessions: () =>
    apiClient.get<Session[]>('/auth/sessions'),

  revokeSession: (sessionId: string) =>
    apiClient.delete<{ success: boolean }>(`/auth/sessions/${sessionId}`),
};
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/profile/api/profile.ts frontend/src/features/profile/types.ts
git commit -m "feat(profile): add profile API client"
```

---

## Chunk 4: Frontend - profileStore

### Files

- Create: `frontend/src/features/profile/profileStore.ts`
- Create: `frontend/src/features/profile/profileStore.test.ts`

### Steps

- [ ] **Step 1: Write the failing test**

```typescript
# frontend/src/features/profile/profileStore.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { profileStore } from './profileStore';

describe('profileStore', () => {
  beforeEach(() => {
    profileStore.setState({
      user: null,
      stats: null,
      sessions: [],
      isLoading: false,
      error: null,
    });
  });

  it('should have initial state', () => {
    const state = profileStore.getState();
    expect(state.user).toBeNull();
    expect(state.stats).toBeNull();
    expect(state.sessions).toEqual([]);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('should load profile', async () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      display_name: 'Test User',
      avatar_url: null,
      email: 'test@example.com',
      phone: '1234567890',
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    };

    // Mock API
    vi.mock('../api/profile', () => ({
      profileApi: {
        getProfile: vi.fn().mockResolvedValue(mockUser),
      },
    }));

    await profileStore.getState().loadProfile();
    expect(profileStore.getState().user).toEqual(mockUser);
  });
});
```

- [ ] **Step 2: Create store**

```typescript
# frontend/src/features/profile/profileStore.ts
import { create } from 'zustand';
import { profileApi } from './api/profile';
import { User, UsageStats, Session } from './types';

interface ProfileState {
  user: User | null;
  stats: UsageStats | null;
  sessions: Session[];
  isLoading: boolean;
  error: string | null;
}

interface ProfileActions {
  loadProfile: () => Promise<void>;
  updateProfile: (data: { display_name?: string; email?: string; phone?: string }) => Promise<void>;
  loadStats: () => Promise<void>;
  loadSessions: () => Promise<void>;
  revokeSession: (sessionId: string) => Promise<void>;
  clearError: () => void;
}

type ProfileStore = ProfileState & ProfileActions;

export const profileStore = create<ProfileStore>((set) => ({
  user: null,
  stats: null,
  sessions: [],
  isLoading: false,
  error: null,

  loadProfile: async () => {
    set({ isLoading: true, error: null });
    try {
      const user = await profileApi.getProfile();
      set({ user, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  updateProfile: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const user = await profileApi.updateProfile(data);
      set({ user, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  loadStats: async () => {
    // TODO: Implement when backend provides stats endpoint
    set({ stats: { conversation_count: 0, message_count: 0, knowledge_base_count: 0, join_date: '' } });
  },

  loadSessions: async () => {
    set({ isLoading: true, error: null });
    try {
      const sessions = await profileApi.getSessions();
      set({ sessions, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  revokeSession: async (sessionId: string) => {
    try {
      await profileApi.revokeSession(sessionId);
      set((state) => ({
        sessions: state.sessions.filter((s) => s.session_id !== sessionId),
      }));
    } catch (err) {
      set({ error: (err as Error).message });
    }
  },

  clearError: () => set({ error: null }),
}));
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/profile/profileStore.ts frontend/src/features/profile/profileStore.test.ts
git commit -m "feat(profile): add profileStore with state management"
```

---

## Chunk 5: Frontend - ProfileCard Component

### Files

- Create: `frontend/src/features/profile/components/ProfileCard.tsx`
- Create: `frontend/src/features/profile/components/ProfileCard.css`

### Steps

- [ ] **Step 1: Create ProfileCard**

```tsx
// frontend/src/features/profile/components/ProfileCard.tsx
import { useState } from 'react';
import { Camera, Check, X } from 'lucide-react';
import { profileStore } from '../profileStore';
import './ProfileCard.css';

export function ProfileCard() {
  const { user, updateProfile, isLoading } = profileStore();
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

  return (
    <div className="profile-card">
      <div className="profile-avatar-section">
        <div className="profile-avatar">
          {user.avatar_url ? (
            <img src={user.avatar_url} alt={user.display_name || user.username} />
          ) : (
            <div className="profile-avatar-placeholder">
              {(user.display_name || user.username).charAt(0).toUpperCase()}
            </div>
          )}
          <button className="profile-avatar-upload" aria-label="上传头像">
            <Camera size={16} />
          </button>
        </div>
      </div>

      <div className="profile-info">
        <div className="profile-field">
          <label>显示名称</label>
          {editingField === 'display_name' ? (
            <div className="profile-field-edit">
              <input
                type="text"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                autoFocus
              />
              <button onClick={handleSave} disabled={isLoading}><Check size={16} /></button>
              <button onClick={handleCancel}><X size={16} /></button>
            </div>
          ) : (
            <div className="profile-field-display" onClick={() => handleStartEdit('display_name', user.display_name || '')}>
              {user.display_name || '未设置'} <span className="edit-hint">点击编辑</span>
            </div>
          )}
        </div>

        <div className="profile-field">
          <label>用户名</label>
          <div className="profile-field-display readonly">{user.username}</div>
        </div>

        <div className="profile-field">
          <label>邮箱</label>
          {editingField === 'email' ? (
            <div className="profile-field-edit">
              <input
                type="email"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                autoFocus
              />
              <button onClick={handleSave} disabled={isLoading}><Check size={16} /></button>
              <button onClick={handleCancel}><X size={16} /></button>
            </div>
          ) : (
            <div className="profile-field-display" onClick={() => handleStartEdit('email', user.email || '')}>
              {user.email || '未设置'} <span className="edit-hint">点击编辑</span>
            </div>
          )}
        </div>

        <div className="profile-field">
          <label>手机号</label>
          {editingField === 'phone' ? (
            <div className="profile-field-edit">
              <input
                type="tel"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                autoFocus
              />
              <button onClick={handleSave} disabled={isLoading}><Check size={16} /></button>
              <button onClick={handleCancel}><X size={16} /></button>
            </div>
          ) : (
            <div className="profile-field-display" onClick={() => handleStartEdit('phone', user.phone || '')}>
              {user.phone || '未设置'} <span className="edit-hint">点击编辑</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create CSS**

```css
/* frontend/src/features/profile/components/ProfileCard.css */
.profile-card {
  background: var(--color-bg-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  display: flex;
  gap: var(--space-6);
}

.profile-avatar-section {
  flex-shrink: 0;
}

.profile-avatar {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: var(--radius-full);
  overflow: hidden;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-avatar-placeholder {
  width: 100%;
  height: 100%;
  background: var(--color-accent-bg);
  color: var(--color-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-4xl);
  font-weight: var(--font-semibold);
}

.profile-avatar-upload {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  padding: var(--space-2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.profile-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.profile-field label {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  font-weight: var(--font-medium);
}

.profile-field-display {
  font-size: var(--text-base);
  color: var(--color-text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.profile-field-display:hover .edit-hint {
  opacity: 1;
}

.profile-field-display.readonly {
  cursor: default;
  color: var(--color-text-secondary);
}

.edit-hint {
  font-size: var(--text-xs);
  color: var(--color-accent);
  opacity: 0;
  transition: opacity var(--duration-fast) var(--ease-default);
}

.profile-field-edit {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.profile-field-edit input {
  flex: 1;
  height: var(--input-height);
  background: var(--color-bg-inset);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0 var(--space-3);
  font-size: var(--text-base);
  color: var(--color-text-primary);
}

.profile-field-edit input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: var(--shadow-inset-focus);
}

.profile-field-edit button {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-field-edit button:hover {
  color: var(--color-accent);
  background: var(--color-accent-bg);
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/profile/components/ProfileCard.tsx frontend/src/features/profile/components/ProfileCard.css
git commit -m "feat(profile): add ProfileCard component"
```

---

## Chunk 6: Frontend - StatsGrid Component

### Files

- Create: `frontend/src/features/profile/components/StatsGrid.tsx`
- Create: `frontend/src/features/profile/components/StatsGrid.css`

### Steps

- [ ] **Step 1: Create StatsGrid**

```tsx
// frontend/src/features/profile/components/StatsGrid.tsx
import { MessageSquare, MessageCircle, BookOpen, Calendar } from 'lucide-react';
import { profileStore } from '../profileStore';
import './StatsGrid.css';

export function StatsGrid() {
  const { stats, user } = profileStore();

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
      value: stats?.join_date ?? user?.created_at?.split('T')[0] ?? '-',
    },
  ];

  return (
    <div className="stats-grid">
      <h3 className="stats-title">使用统计</h3>
      <div className="stats-cards">
        {items.map((item) => (
          <div key={item.label} className="stat-card">
            <item.icon size={24} className="stat-icon" />
            <div className="stat-value">{item.value}</div>
            <div className="stat-label">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create CSS**

```css
/* frontend/src/features/profile/components/StatsGrid.css */
.stats-grid {
  margin-top: var(--space-6);
}

.stats-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--space-4);
}

.stat-card {
  background: var(--color-bg-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  text-align: center;
}

.stat-icon {
  color: var(--color-accent);
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/profile/components/StatsGrid.tsx frontend/src/features/profile/components/StatsGrid.css
git commit -m "feat(profile): add StatsGrid component"
```

---

## Chunk 7: Frontend - SessionList Component

### Files

- Create: `frontend/src/features/profile/components/SessionList.tsx`
- Create: `frontend/src/features/profile/components/SessionList.css`

### Steps

- [ ] **Step 1: Create SessionList**

```tsx
// frontend/src/features/profile/components/SessionList.tsx
import { Monitor, Smartphone, LogOut } from 'lucide-react';
import { profileStore } from '../profileStore';
import './SessionList.css';

export function SessionList() {
  const { sessions, revokeSession } = profileStore();

  const getDeviceIcon = (device: string) => {
    if (device.toLowerCase().includes('mobile') || device.toLowerCase().includes('iphone') || device.toLowerCase().includes('android')) {
      return Smartphone;
    }
    return Monitor;
  };

  const formatTime = (time: string) => {
    const date = new Date(time);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor(diff / (1000 * 60));

    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    return date.toLocaleDateString('zh-CN');
  };

  return (
    <div className="session-list">
      <h3 className="session-title">活跃会话</h3>
      <div className="session-items">
        {sessions.length === 0 ? (
          <div className="session-empty">暂无活跃会话</div>
        ) : (
          sessions.map((session) => {
            const DeviceIcon = getDeviceIcon(session.device);
            return (
              <div key={session.session_id} className="session-item">
                <div className="session-device">
                  <DeviceIcon size={20} />
                  <span>{session.device}</span>
                </div>
                <div className="session-meta">
                  <span className="session-location">{session.location}</span>
                  <span className="session-separator">•</span>
                  <span className="session-time">{formatTime(session.created_at)}</span>
                  {session.is_current && <span className="session-current-badge">当前</span>}
                </div>
                {!session.is_current && (
                  <button
                    className="session-revoke"
                    onClick={() => revokeSession(session.session_id)}
                    aria-label="退出此会话"
                  >
                    <LogOut size={16} />
                    登出
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create CSS**

```css
/* frontend/src/features/profile/components/SessionList.css */
.session-list {
  margin-top: var(--space-6);
}

.session-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
}

.session-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.session-empty {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-tertiary);
  background: var(--color-bg-surface);
  border-radius: var(--radius-lg);
}

.session-item {
  background: var(--color-bg-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.session-device {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-primary);
  font-weight: var(--font-medium);
  min-width: 140px;
}

.session-meta {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

.session-separator {
  color: var(--color-text-tertiary);
}

.session-current-badge {
  background: var(--color-accent-bg);
  color: var(--color-accent);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.session-revoke {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.session-revoke:hover {
  border-color: var(--color-error);
  color: var(--color-error);
  background: rgba(207, 34, 46, 0.1);
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/profile/components/SessionList.tsx frontend/src/features/profile/components/SessionList.css
git commit -m "feat(profile): add SessionList component"
```

---

## Chunk 8: Frontend - ProfilePage

### Files

- Create: `frontend/src/features/profile/ProfilePage.tsx`
- Create: `frontend/src/features/profile/ProfilePage.css`
- Modify: `frontend/src/routes.tsx` (update ProfilePage import)

### Steps

- [ ] **Step 1: Create ProfilePage**

```tsx
// frontend/src/features/profile/ProfilePage.tsx
import { useEffect } from 'react';
import { LogOut } from 'lucide-react';
import { profileStore } from './profileStore';
import { authStore } from '../auth/authStore';
import { ProfileCard } from './components/ProfileCard';
import { StatsGrid } from './components/StatsGrid';
import { SessionList } from './components/SessionList';
import { useNavigate } from 'react-router-dom';
import './ProfilePage.css';

export function ProfilePage() {
  const navigate = useNavigate();
  const { loadProfile, loadSessions, loadStats, error, clearError } = profileStore();
  const { logout } = authStore();

  useEffect(() => {
    loadProfile();
    loadSessions();
    loadStats();
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="profile-page">
      <header className="profile-header">
        <h1>个人中心</h1>
      </header>

      <main className="profile-content">
        {error && (
          <div className="profile-error">
            <span>{error}</span>
            <button onClick={clearError}>关闭</button>
          </div>
        )}

        <ProfileCard />
        <StatsGrid />
        <SessionList />

        <div className="profile-logout">
          <button className="logout-button" onClick={handleLogout}>
            <LogOut size={18} />
            退出登录
          </button>
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Create CSS**

```css
/* frontend/src/features/profile/ProfilePage.css */
.profile-page {
  height: 100%;
  overflow-y: auto;
  padding: var(--space-6);
  background: var(--color-bg-base);
}

.profile-header {
  margin-bottom: var(--space-6);
}

.profile-header h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.profile-content {
  max-width: 800px;
  margin: 0 auto;
}

.profile-error {
  background: rgba(207, 34, 46, 0.1);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--color-error);
}

.profile-error button {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-error);
  font-size: var(--text-sm);
}

.profile-logout {
  margin-top: var(--space-8);
  padding-top: var(--space-6);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: center;
}

.logout-button {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: none;
  border: 1px solid var(--color-error);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-6);
  color: var(--color-error);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.logout-button:hover {
  background: rgba(207, 34, 46, 0.1);
}

/* Responsive */
@media (max-width: 640px) {
  .profile-page {
    padding: var(--space-4);
  }

  .profile-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .session-item {
    flex-wrap: wrap;
  }
}
```

- [ ] **Step 3: Update routes**

Modify `frontend/src/routes.tsx`:
```typescript
// Add import
import { ProfilePage } from './features/profile/ProfilePage';

// Replace placeholder ProfilePage function with import
// Remove the placeholder function at line 33-36
function ProfilePage() {
  return <PlaceholderPage title="Profile" />;
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/features/profile/ProfilePage.tsx frontend/src/features/profile/ProfilePage.css frontend/src/routes.tsx
git commit -m "feat(profile): add ProfilePage with routing"
```

---

## Chunk 9: Frontend - Unit Tests

### Files

- Create tests for ProfileCard, StatsGrid, SessionList components

### Steps

- [ ] **Step 1: Write ProfileCard test**

```tsx
# frontend/src/features/profile/components/ProfileCard.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ProfileCard } from './ProfileCard';
import { profileStore } from '../profileStore';

vi.mock('../profileStore', () => ({
  profileStore: vi.fn(() => ({
    user: {
      id: '1',
      username: 'testuser',
      display_name: 'Test User',
      avatar_url: null,
      email: 'test@example.com',
      phone: '1234567890',
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
    updateProfile: vi.fn(),
    isLoading: false,
  })),
}));

describe('ProfileCard', () => {
  it('renders user information', () => {
    render(<ProfileCard />);
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('testuser')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
    expect(screen.getByText('1234567890')).toBeInTheDocument();
  });

  it('shows avatar placeholder with first letter', () => {
    render(<ProfileCard />);
    expect(screen.getByText('T')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Write StatsGrid test**

```tsx
# frontend/src/features/profile/components/StatsGrid.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { StatsGrid } from './StatsGrid';
import { profileStore } from '../profileStore';

vi.mock('../profileStore', () => ({
  profileStore: vi.fn(() => ({
    stats: {
      conversation_count: 42,
      message_count: 156,
      knowledge_base_count: 3,
      join_date: '2026-01',
    },
    user: null,
  })),
}));

describe('StatsGrid', () => {
  it('renders all stat cards', () => {
    render(<StatsGrid />);
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('156')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('2026-01')).toBeInTheDocument();
    expect(screen.getByText('对话数')).toBeInTheDocument();
    expect(screen.getByText('消息数')).toBeInTheDocument();
    expect(screen.getByText('知识库数')).toBeInTheDocument();
    expect(screen.getByText('注册时间')).toBeInTheDocument();
  });
});
```

- [ ] **Step 3: Write SessionList test**

```tsx
# frontend/src/features/profile/components/SessionList.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { SessionList } from './SessionList';
import { profileStore } from '../profileStore';

vi.mock('../profileStore', () => ({
  profileStore: vi.fn(() => ({
    sessions: [
      {
        session_id: '1',
        device: 'Chrome on Windows',
        location: '北京市',
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
        is_current: true,
      },
      {
        session_id: '2',
        device: 'Safari on iPhone',
        location: '北京市',
        created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 minutes ago
        is_current: false,
      },
    ],
    revokeSession: vi.fn(),
  })),
}));

describe('SessionList', () => {
  it('renders sessions', () => {
    render(<SessionList />);
    expect(screen.getByText('Chrome on Windows')).toBeInTheDocument();
    expect(screen.getByText('Safari on iPhone')).toBeInTheDocument();
    expect(screen.getByText('当前')).toBeInTheDocument();
  });

  it('shows revoke button for non-current sessions', () => {
    render(<SessionList />);
    const revokeButtons = screen.getAllByText('登出');
    expect(revokeButtons).toHaveLength(1);
  });
});
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && npm run test:run -- --reporter=verbose 2>&1 | head -100
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/profile/components/*.test.tsx
git commit -m "test(profile): add unit tests for profile components"
```

---

## Chunk 10: Integration - Build & Verify

### Steps

- [ ] **Step 1: Run build**

```bash
cd frontend && npm run build 2>&1
```

- [ ] **Step 2: Fix any TypeScript errors**

- [ ] **Step 3: Run all tests**

```bash
cd frontend && npm run test:run 2>&1
```

- [ ] **Step 3: Update frontend progress log**

Update `frontend/docs/frontend-progress-log.md` with the completed Personal Center feature.

- [ ] **Step 4: Final commit**

```bash
git add -A && git commit -m "feat(profile): complete Personal Center feature"
```

---

**Plan complete and saved to `docs/superpowers/plans/2026-03-24-personal-center-plan.md`. Ready to execute?**
