# Phase 1 Frontend Skeleton - Implementation Design

## 1. Overview

Establish the foundational infrastructure for CampusMind frontend: routing, auth flow, layout shell, and API client base. This phase delivers a **functional skeleton** — app boots, navigates between pages, and authenticates users, but chat streaming and knowledge operations are out of scope.

## 2. Dependencies to Add

| Package | Version | Purpose |
|---------|---------|---------|
| `react-router-dom` | ^6.x | Routing |
| `zustand` | ^4.x | State management |

## 3. Directory Structure

```
src/
├── api/
│   ├── client.ts          # Base fetch wrapper with JWT injection
│   ├── auth.ts            # Auth endpoints (login/logout/refresh)
│   └── types.ts           # Shared API types (User, ApiError)
├── features/
│   ├── auth/
│   │   ├── authStore.ts       # Zustand store: user, token, isAuthenticated
│   │   ├── LoginPage.tsx      # Login form (username/password)
│   │   └── ProtectedRoute.tsx # Route guard (redirects to /login)
│   ├── chat/
│   │   ├── ChatPage.tsx       # Placeholder chat page (empty, for Phase 2)
│   │   └── chatStore.ts       # Placeholder store (empty, for Phase 2)
│   └── knowledge/
│       └── KnowledgeListPage.tsx  # Placeholder page (empty, for Phase 3)
├── components/
│   └── layout/
│       └── Sidebar/
│           ├── Sidebar.tsx    # Container with toggle logic
│           └── Sidebar.css    # Plain CSS, uses var(--color-xxx)
├── styles/
│   └── global/
│       └── global.css         # Reset + base styles (or extend existing)
├── App.tsx                    # Root: providers + routes + layout
├── routes.tsx                 # Route definitions
└── main.tsx                   # Entry: render App
```

**CSS Strategy**: All components use global CSS Custom Properties (no CSS Modules). Files reference design tokens directly: `var(--color-bg-surface)`, `var(--spacing-md)`, etc.

## 4. Component Specifications

### 4.1 API Client (`src/api/client.ts`)

```typescript
class ApiClient {
  private baseUrl = '/api/v1';

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = authStore.getState().token;
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
    if (response.status === 401) {
      authStore.getState().logout();
      throw new ApiError(401, 'Unauthorized');
    }
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(response.status, error.detail || 'Request failed');
    }
    return response.json();
  }

  get<T>(url: string) { return this.request<T>(url, { method: 'GET' }); }
  post<T>(url: string, data?: unknown) {
    return this.request<T>(url, { method: 'POST', body: data ? JSON.stringify(data) : undefined });
  }
  delete<T>(url: string) { return this.request<T>(url, { method: 'DELETE' }); }
}
```

### 4.2 Auth Store (`src/features/auth/authStore.ts`)

```typescript
interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  initAuth: () => Promise<void>;
}
```

- `login`: POST `/api/v1/auth/login` → store `{ token, user_id }` in sessionStorage
- `logout`: DELETE `/api/v1/auth/logout` → clear state + sessionStorage
- `initAuth`: Read token from sessionStorage on app load

### 4.3 ProtectedRoute (`src/features/auth/ProtectedRoute.tsx`)

```typescript
// Wraps auth-gated pages. Redirects to /login if not authenticated.
<ProtectedRoute>
  <KnowledgeBuildPage />
</ProtectedRoute>
```

### 4.4 Routes (`src/routes.tsx`)

| Route | Component | Auth Required |
|-------|-----------|---------------|
| `/` | `ChatPage` | No |
| `/login` | `LoginPage` | No (redirects if already logged in) |
| `/knowledge` | `KnowledgeListPage` | No |
| `/knowledge/build` | `KnowledgeBuildPage` | Yes |
| `/profile` | `ProfilePage` | Yes |

### 4.5 App Layout (`App.tsx`)

```
Root
├── AuthProvider
├── Sidebar (persistent)
└── MainViewport
    └── <Outlet /> (renders matched route)
```

Sidebar is always visible on desktop; hidden on mobile (hamburger trigger, out of scope for Phase 1 — hardcode sidebar visible).

## 5. Out of Scope (Future Phases)

- SSE streaming chat (Phase 2)
- Tool event rendering (Phase 2)
- Message history loading (Phase 2)
- Knowledge base CRUD operations (Phase 3)
- Crawl/upload/index workflow (Phase 4)
- Responsive sidebar toggle (Phase 5)
- Token refresh mechanism (Phase 5)

## 6. Implementation Order

1. Add dependencies (`react-router-dom`, `zustand`)
2. Create `api/client.ts` and `api/types.ts`
3. Create `authStore.ts` and `LoginPage.tsx`
4. Create `ProtectedRoute.tsx`
5. Create `Sidebar.tsx` and `Sidebar.css`
6. Create `routes.tsx` and update `App.tsx`
7. Create placeholder pages (ChatPage, KnowledgeListPage, ProfilePage)
8. Verify app boots with `npm run dev`
