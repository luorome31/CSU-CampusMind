// frontend/src/routes.tsx
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { ProtectedRoute } from './features/auth/ProtectedRoute';
import { LoginPage } from './features/auth/LoginPage';
import { ChatPage } from './features/chat/ChatPage';
import { KnowledgeListPage } from './features/knowledge/KnowledgeListPage';
import { KnowledgeFileListPage } from './features/knowledge/KnowledgeFileListPage';
import { KnowledgeFileDetailPage } from './features/knowledge/KnowledgeFileDetailPage';
import { KnowledgeBuildPage } from './features/build/KnowledgeBuildPage';
import { Sidebar } from './components/layout/Sidebar/Sidebar';

function LayoutWithSidebar() {
  return (
    <div className="layout-sidebar">
      <Sidebar />
      <main className="layout-main">
        <Outlet />
      </main>
    </div>
  );
}

// Placeholder pages (empty for Phase 1, filled in later phases)
function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="placeholder-page">
      <h2 className="placeholder-title">{title}</h2>
      <p className="placeholder-body">Component coming in a later phase.</p>
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
      { path: 'knowledge/:kbId', element: <KnowledgeFileListPage /> },
      { path: 'knowledge/:kbId/files/:fileId', element: <KnowledgeFileDetailPage /> },
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
