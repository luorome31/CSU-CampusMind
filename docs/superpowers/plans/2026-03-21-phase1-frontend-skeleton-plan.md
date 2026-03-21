# Phase 1 Frontend Skeleton - Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish foundational infrastructure: routing, auth flow, layout shell, and API client base. App boots, navigates, authenticates — but chat streaming and knowledge operations are out of scope.

**Architecture:** React Router v6 for routing with a persistent sidebar layout. Zustand for global auth state. API client as a thin fetch wrapper with JWT injection. All components use global CSS Custom Properties (no CSS Modules).

**Tech Stack:** React 18, Vite, TypeScript, react-router-dom ^6, zustand ^4

---

## File Map

```
src/
├── api/
│   ├── client.ts          # Create: Base fetch wrapper
│   ├── auth.ts            # Create: Auth endpoint helpers
│   └── types.ts           # Create: User, ApiError types
├── features/
│   ├── auth/
│   │   ├── authStore.ts       # Create: Zustand auth store
│   │   ├── LoginPage.tsx      # Create: Login form page
│   │   └── ProtectedRoute.tsx # Create: Route guard component
│   ├── chat/
│   │   ├── ChatPage.tsx       # Create: Placeholder (empty for Phase 2)
│   │   └── chatStore.ts       # Create: Placeholder store (empty for Phase 2)
│   └── knowledge/
│       └── KnowledgeListPage.tsx  # Create: Placeholder page
├── components/
│   └── layout/
│       └── Sidebar/
│           ├── Sidebar.tsx    # Create: Sidebar container
│           └── Sidebar.css    # Create: Sidebar styles
├── styles/
│   └── global/
│       └── global.css         # Modify: Add reset + base styles
├── App.tsx                    # Modify: Add routes + layout
├── routes.tsx                 # Create: Route definitions
└── main.tsx                  # Modify: Import router
```

---

## Chunk 1: Dependencies & Base Setup

### Task 1: Add dependencies

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: Add react-router-dom and zustand**

```bash
cd /home/luorome/software/CampusMind/frontend
npm install react-router-dom zustand
```

---

### Task 2: Create global CSS reset and base styles

**Files:**
- Modify: `frontend/src/index.css` (append global styles)

- [ ] **Step 1: Append reset and base styles to index.css**

Add to the end of `frontend/src/index.css`:

```css
/* === Global Reset === */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #root {
  height: 100%;
}

body {
  font-family: var(--font-family, system-ui, -apple-system, sans-serif);
  color: var(--color-text-primary);
  background: var(--color-bg-base);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  cursor: pointer;
  border: none;
  background: none;
  font: inherit;
}

/* === Layout Variables === */
:root {
  --sidebar-width: 260px;
  --header-height: 56px;
}
```

---

## Chunk 2: API Layer

### Task 3: Create API types

**Files:**
- Create: `frontend/src/api/types.ts`

- [ ] **Step 1: Write API shared types**

```typescript
// frontend/src/api/types.ts

export interface User {
  user_id: string;
  username: string;
  // Add other user fields as needed from backend response
}

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
  expires_in: number;
}
```

---

### Task 4: Create API client

**Files:**
- Create: `frontend/src/api/client.ts`

- [ ] **Step 1: Write base API client**

```typescript
// frontend/src/api/client.ts
import { ApiError } from './types';

// Token helper reads directly from sessionStorage — avoids circular import with authStore
function getToken(): string | null {
  return sessionStorage.getItem('token');
}

class ApiClient {
  private baseUrl = '/api/v1';

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = getToken();

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });

    if (response.status === 401) {
      // Clear session and reload to trigger auth re-init
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      window.location.href = '/login';
      throw new ApiError(401, 'Unauthorized');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(response.status, error.detail || 'Request failed');
    }

    // Handle empty responses
    const text = await response.text();
    if (!text) return {} as T;
    return JSON.parse(text) as T;
  }

  get<T>(url: string) {
    return this.request<T>(url, { method: 'GET' });
  }

  post<T>(url: string, data?: unknown) {
    return this.request<T>(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  delete<T>(url: string) {
    return this.request<T>(url, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
```

---

### Task 5: Create Auth API helpers

**Files:**
- Create: `frontend/src/api/auth.ts`

- [ ] **Step 1: Write auth API helpers**

```typescript
// frontend/src/api/auth.ts
import { apiClient } from './client';
import { LoginResponse } from './types';

export const authApi = {
  login: (username: string, password: string) =>
    apiClient.post<LoginResponse>('/auth/login', { username, password }),

  logout: () => apiClient.post<{ message: string }>('/auth/logout'),

  refresh: () => apiClient.post<LoginResponse>('/auth/refresh'),
};
```

---

## Chunk 3: Auth Feature

### Task 6: Create Auth Store

**Files:**
- Create: `frontend/src/features/auth/authStore.ts`

- [ ] **Step 1: Write auth Zustand store**

```typescript
// frontend/src/features/auth/authStore.ts
import { create } from 'zustand';
import { authApi } from '../../api/auth';
import { User } from '../../api/types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  initAuth: () => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

export const authStore = create<AuthStore>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,

  login: async (username: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authApi.login(username, password);
      const user: User = { user_id: response.user_id, username };
      const token = response.token;

      sessionStorage.setItem('token', token);
      sessionStorage.setItem('user', JSON.stringify(user));

      set({ user, token, isAuthenticated: true, isLoading: false });
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
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      set({ user: null, token: null, isAuthenticated: false });
    }
  },

  initAuth: async () => {
    const token = sessionStorage.getItem('token');
    const userStr = sessionStorage.getItem('user');

    if (token && userStr) {
      try {
        const user = JSON.parse(userStr) as User;
        set({ user, token, isAuthenticated: true });
      } catch {
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
      }
    }
  },
}));
```

---

### Task 7: Create LoginPage

**Files:**
- Create: `frontend/src/features/auth/LoginPage.tsx`

- [ ] **Step 1: Write LoginPage component**

```typescript
// frontend/src/features/auth/LoginPage.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authStore } from './authStore';
import { Button } from '../../components/ui';
import { Input } from '../../components/ui';

export function LoginPage() {
  const navigate = useNavigate();
  const login = authStore((s) => s.login);
  const isLoading = authStore((s) => s.isLoading);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--color-bg-base)',
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: 'var(--color-bg-surface)',
          padding: 'var(--spacing-xl, 2rem)',
          borderRadius: '12px',
          boxShadow: 'var(--shadow-card)',
          width: '100%',
          maxWidth: '360px',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--spacing-md, 1rem)',
        }}
      >
        <h1
          style={{
            fontSize: 'var(--font-size-xl, 1.5rem)',
            fontWeight: 600,
            color: 'var(--color-text-primary)',
            marginBottom: 'var(--spacing-sm, 0.5rem)',
          }}
        >
          Sign In
        </h1>

        <Input
          label="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter username"
          required
        />

        <Input
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter password"
          required
        />

        {error && (
          <p style={{ color: '#dc2626', fontSize: 'var(--font-size-sm, 0.875rem)' }}>
            {error}
          </p>
        )}

        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Signing in...' : 'Sign In'}
        </Button>
      </form>
    </div>
  );
}
```

---

### Task 8: Create ProtectedRoute

**Files:**
- Create: `frontend/src/features/auth/ProtectedRoute.tsx`

- [ ] **Step 1: Write ProtectedRoute component**

```typescript
// frontend/src/features/auth/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { authStore } from './authStore';
import type { ReactNode } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const location = useLocation();
  const isAuthenticated = authStore((s) => s.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
```

---

## Chunk 4: Layout - Sidebar

### Task 9: Create Sidebar CSS

**Files:**
- Create: `frontend/src/components/layout/Sidebar/Sidebar.css`

- [ ] **Step 1: Write Sidebar styles**

```css
/* frontend/src/components/layout/Sidebar/Sidebar.css */

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: var(--sidebar-width, 260px);
  background: var(--color-bg-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.sidebar-header {
  padding: var(--spacing-lg, 1.5rem);
  border-bottom: 1px solid var(--color-border-subtle);
}

.sidebar-logo {
  font-size: var(--font-size-lg, 1.125rem);
  font-weight: 600;
  color: var(--color-text-primary);
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-md, 1rem);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs, 0.25rem);
  overflow-y: auto;
}

.sidebar-nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  border-radius: 8px;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm, 0.875rem);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.sidebar-nav-item:hover {
  background: var(--color-accent-bg);
  color: var(--color-text-primary);
}

.sidebar-nav-item.active {
  background: var(--color-accent-bg);
  color: var(--color-text-primary);
  font-weight: 500;
}

.sidebar-nav-item svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: var(--spacing-md, 1rem);
  border-top: 1px solid var(--color-border-subtle);
}

.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm, 0.5rem);
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  background: var(--color-accent-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-primary);
  font-size: var(--font-size-sm, 0.875rem);
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.new-chat-btn:hover {
  background: var(--color-accent-bg-hover);
}
```

---

### Task 10: Create Sidebar component

**Files:**
- Create: `frontend/src/components/layout/Sidebar/Sidebar.tsx`

- [ ] **Step 1: Write Sidebar component**

```typescript
// frontend/src/components/layout/Sidebar/Sidebar.tsx
import { NavLink, useNavigate } from 'react-router-dom';
import { MessageSquare, BookOpen, Wrench, User } from 'lucide-react';
import { authStore } from '../../features/auth/authStore';
import './Sidebar.css';

const navItems = [
  { to: '/', icon: MessageSquare, label: 'Chat', end: true },
  { to: '/knowledge', icon: BookOpen, label: 'Knowledge Base' },
  { to: '/knowledge/build', icon: Wrench, label: 'Build', requiresAuth: true },
  { to: '/profile', icon: User, label: 'Profile', requiresAuth: true },
];

export function Sidebar() {
  const navigate = useNavigate();
  const isAuthenticated = authStore((s) => s.isAuthenticated);

  const handleNewChat = () => {
    // Phase 2: clear current dialog
    navigate('/');
  };

  const visibleItems = navItems.filter((item) => {
    if (item.requiresAuth && !isAuthenticated) return false;
    return true;
  });

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-logo">CampusMind</span>
      </div>

      <nav className="sidebar-nav">
        {visibleItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `sidebar-nav-item${isActive ? ' active' : ''}`
            }
          >
            <item.icon />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button className="new-chat-btn" onClick={handleNewChat}>
          <MessageSquare size={16} />
          New Chat
        </button>
      </div>
    </aside>
  );
}
```

---

## Chunk 5: Routes & App Shell

### Task 11: Create Routes definition

**Files:**
- Create: `frontend/src/routes.tsx`

- [ ] **Step 1: Write route definitions**

```typescript
// frontend/src/routes.tsx
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { ProtectedRoute } from './features/auth/ProtectedRoute';
import { LoginPage } from './features/auth/LoginPage';
import { ChatPage } from './features/chat/ChatPage';
import { KnowledgeListPage } from './features/knowledge/KnowledgeListPage';
import { KnowledgeBuildPage } from './features/build/KnowledgeBuildPage';
import { Sidebar } from './components/layout/Sidebar/Sidebar';

function LayoutWithSidebar() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main
        style={{
          marginLeft: 'var(--sidebar-width, 260px)',
          flex: 1,
          padding: 'var(--spacing-xl, 2rem)',
        }}
      >
        <Outlet />
      </main>
    </div>
  );
}

// Placeholder pages (empty for Phase 1, filled in later phases)
function PlaceholderPage({ title }: { title: string }) {
  return (
    <div style={{ color: 'var(--color-text-secondary)' }}>
      <h2 style={{ marginBottom: 'var(--spacing-md, 1rem)' }}>{title}</h2>
      <p>Component coming in a later phase.</p>
    </div>
  );
}

// ProfilePage placeholder (filled in Phase 2+)
function ProfilePage() {
  return <PlaceholderPage title="Profile" />;
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <LayoutWithSidebar />,
    children: [
      { index: true, element: <ChatPage /> },
      { path: 'knowledge', element: <KnowledgeListPage /> },
      {
        path: 'knowledge/build',
        element: (
          <ProtectedRoute>
            <KnowledgeBuildPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'profile',
        element: (
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        ),
      },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
]);
```

---

### Task 12: Create ChatPage placeholder

**Files:**
- Create: `frontend/src/features/chat/ChatPage.tsx`

- [ ] **Step 1: Write ChatPage placeholder**

```typescript
// frontend/src/features/chat/ChatPage.tsx
export function ChatPage() {
  return (
    <div
      style={{
        maxWidth: '800px',
        margin: '0 auto',
        color: 'var(--color-text-secondary)',
      }}
    >
      <h2 style={{ marginBottom: 'var(--spacing-md, 1rem)' }}>Chat</h2>
      <p>Streaming chat coming in Phase 2.</p>
    </div>
  );
}
```

- [ ] **Step 2: Create placeholder chatStore**

```typescript
// frontend/src/features/chat/chatStore.ts
import { create } from 'zustand';

export const chatStore = create((set) => ({
  // Placeholder for Phase 2
}));
```

---

### Task 13: Create KnowledgeListPage placeholder

**Files:**
- Create: `frontend/src/features/knowledge/KnowledgeListPage.tsx`

- [ ] **Step 1: Write KnowledgeListPage placeholder**

```typescript
// frontend/src/features/knowledge/KnowledgeListPage.tsx
export function KnowledgeListPage() {
  return (
    <div
      style={{
        maxWidth: '800px',
        margin: '0 auto',
        color: 'var(--color-text-secondary)',
      }}
    >
      <h2 style={{ marginBottom: 'var(--spacing-md, 1rem)' }}>Knowledge Base</h2>
      <p>Knowledge list coming in Phase 3.</p>
    </div>
  );
}
```

---

### Task 14: Create placeholder KnowledgeBuildPage

**Files:**
- Create: `frontend/src/features/build/KnowledgeBuildPage.tsx`

- [ ] **Step 1: Write KnowledgeBuildPage placeholder**

```typescript
// frontend/src/features/build/KnowledgeBuildPage.tsx
export function KnowledgeBuildPage() {
  return (
    <div
      style={{
        maxWidth: '800px',
        margin: '0 auto',
        color: 'var(--color-text-secondary)',
      }}
    >
      <h2 style={{ marginBottom: 'var(--spacing-md, 1rem)' }}>Build Knowledge Base</h2>
      <p>Build workflow coming in Phase 4.</p>
    </div>
  );
}
```

---

### Task 15: Update App.tsx

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Replace App.tsx with router setup**

```tsx
// frontend/src/App.tsx
import { useEffect } from 'react';
import { RouterProvider } from 'react-router-dom';
import { router } from './routes';
import { authStore } from './features/auth/authStore';

export function App() {
  const initAuth = authStore((s) => s.initAuth);

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  return <RouterProvider router={router} />;
}

export default App;
```

---

### Task 16: Update main.tsx

**Files:**
- Modify: `frontend/src/main.tsx`

- [ ] **Step 1: Verify main.tsx imports App correctly**

The existing main.tsx is fine — it already imports App from './App' and './index.css'. No changes needed unless you want to ensure auth init happens here.

---

## Chunk 6: Verify & Test

### Task 17: Verify app boots

**Files:**
- (No file changes)

- [ ] **Step 1: Run dev server and verify no errors**

```bash
cd /home/luorome/software/CampusMind/frontend
npm run dev
```

Expected: Vite dev server starts without TypeScript or runtime errors.

- [ ] **Step 2: Verify routes load**

Navigate to:
- `/` → Chat placeholder
- `/login` → Login form
- `/knowledge` → Knowledge placeholder
- `/knowledge/build` → Redirects to `/login` (not authenticated)
- `/profile` → Redirects to `/login` (not authenticated)

---

## Implementation Order Summary

```
Chunk 1: Dependencies & Base Setup
  → Task 1: Add react-router-dom, zustand
  → Task 2: Add global CSS reset + layout vars

Chunk 2: API Layer
  → Task 3: Create api/types.ts
  → Task 4: Create api/client.ts
  → Task 5: Create api/auth.ts

Chunk 3: Auth Feature
  → Task 6: Create authStore.ts
  → Task 7: Create LoginPage.tsx
  → Task 8: Create ProtectedRoute.tsx

Chunk 4: Layout - Sidebar
  → Task 9: Create Sidebar.css
  → Task 10: Create Sidebar.tsx

Chunk 5: Routes & App Shell
  → Task 11: Create routes.tsx
  → Task 12: Create ChatPage.tsx + chatStore.ts
  → Task 13: Create KnowledgeListPage.tsx
  → Task 14: Create KnowledgeBuildPage.tsx
  → Task 15: Update App.tsx

Chunk 6: Verify & Test
  → Task 17: Run dev server, verify routes
```
