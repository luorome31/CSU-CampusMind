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
