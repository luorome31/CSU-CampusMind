// frontend/src/components/layout/Sidebar/Sidebar.tsx
import { useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { MessageSquare, BookOpen, Wrench, User, LogIn } from 'lucide-react';
import { authStore } from '../../../features/auth/authStore';
import { chatStore } from '../../../features/chat/chatStore';
import { listDialogs, getDialogMessages, deleteDialog } from '../../../api/dialog';
import { HistoryItem } from './HistoryItem';
import './Sidebar.css';

const navItems = [
  { to: '/', icon: MessageSquare, label: '聊天', end: true },
  { to: '/knowledge', icon: BookOpen, label: '知识库', end: true, requiresAuth: true },
  { to: '/knowledge/build', icon: Wrench, label: '知识库构建', requiresAuth: true },
  { to: '/profile', icon: User, label: '个人中心', requiresAuth: true },
];

export function Sidebar() {
  const navigate = useNavigate();
  const isAuthenticated = authStore((s) => s.isAuthenticated);
  const {
    dialogs,
    setDialogs,
    currentDialogId,
    loadDialog,
    removeDialog,
    clearMessages
  } = chatStore();

  useEffect(() => {
    if (isAuthenticated) {
      listDialogs().then(setDialogs).catch(console.error);
    }
  }, [isAuthenticated, setDialogs]);

  const handleNewChat = () => {
    clearMessages();
    navigate('/');
  };

  const handleSelectHistory = async (id: string) => {
    try {
      const messages = await getDialogMessages(id);
      loadDialog(id, messages);
      navigate('/');
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const handleDeleteHistory = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      try {
        await deleteDialog(id);
        removeDialog(id);
      } catch (err) {
        console.error('Failed to delete history:', err);
      }
    }
  };

  const visibleItems = navItems.filter((item) => {
    if (item.requiresAuth && !isAuthenticated) return false;
    return true;
  });

  const showLoginPrompt = !isAuthenticated;

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-logo">CampusMind</span>
      </div>

      <nav className="sidebar-nav">
        <div className="sidebar-section-label">导航</div>
        {showLoginPrompt ? (
          <NavLink
            to="/login"
            className={({ isActive }) =>
              `sidebar-nav-item${isActive ? ' active' : ''}`
            }
          >
            <LogIn size={18} />
            登录
          </NavLink>
        ) : (
          visibleItems.map((item) => (
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
          ))
        )}

        {isAuthenticated && dialogs.length > 0 && (
          <>
            <div className="sidebar-divider" />
            <div className="sidebar-section-label">历史会话</div>
            <div className="sidebar-history-list">
              {dialogs.map((dialog) => (
                <HistoryItem
                  key={dialog.id}
                  id={dialog.id}
                  title={dialog.title}
                  updatedAt={dialog.updated_at}
                  isActive={currentDialogId === dialog.id}
                  onClick={() => handleSelectHistory(dialog.id)}
                  onDelete={(e) => handleDeleteHistory(e, dialog.id)}
                />
              ))}
            </div>
          </>
        )}
      </nav>

      <div className="sidebar-footer">
        <button className="new-chat-btn" onClick={handleNewChat}>
          <MessageSquare size={16} />
          新建对话
        </button>
      </div>
    </aside>
  );
}
