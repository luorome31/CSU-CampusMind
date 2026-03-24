// frontend/src/routes.tsx
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { ProtectedRoute } from './features/auth/ProtectedRoute';
import { LoginPage } from './features/auth/LoginPage';
import { ChatPage } from './features/chat/ChatPage';
import { KnowledgeListPage } from './features/knowledge/KnowledgeListPage';
import { KnowledgeFileListPage } from './features/knowledge/KnowledgeFileListPage';
import { KnowledgeFileDetailPage } from './features/knowledge/KnowledgeFileDetailPage';
import { KnowledgeBuildPage } from './features/build/KnowledgeBuildPage';
import { ProfilePage } from './features/profile/ProfilePage';
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
      {
        path: 'knowledge',
        element: (
          <ProtectedRoute>
            <KnowledgeListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'knowledge/:kbId',
        element: (
          <ProtectedRoute>
            <KnowledgeFileListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'knowledge/:kbId/files/:fileId',
        element: (
          <ProtectedRoute>
            <KnowledgeFileDetailPage />
          </ProtectedRoute>
        ),
      },
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
