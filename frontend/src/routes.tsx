// frontend/src/routes.tsx
import { useState } from 'react';
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { PanelLeft } from 'lucide-react';
import { ProtectedRoute } from './features/auth/ProtectedRoute';
import { LoginPage } from './features/auth/LoginPage';
import { ChatPage } from './features/chat/ChatPage';
import { KnowledgeListPage } from './features/knowledge/KnowledgeListPage';
import { KnowledgeFileListPage } from './features/knowledge/KnowledgeFileListPage';
import { KnowledgeFileDetailPage } from './features/knowledge/KnowledgeFileDetailPage';
import { KnowledgeBuildPage } from './features/build/KnowledgeBuildPage';
import { ProfilePage } from './features/profile/ProfilePage';
import { Sidebar } from './components/layout/Sidebar/Sidebar';
import './routes.css';

function LayoutWithSidebar() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className={`layout-sidebar${sidebarCollapsed ? ' sidebar-collapsed' : ''}`}>
      <Sidebar
        isCollapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed((v) => !v)}
      />
      <main className="layout-main">
        {sidebarCollapsed && (
          <button
            className="sidebar-expand-btn"
            onClick={() => setSidebarCollapsed(false)}
            aria-label="展开侧边栏"
          >
            <PanelLeft size={18} />
          </button>
        )}
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
