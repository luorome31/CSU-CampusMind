// frontend/src/components/layout/Sidebar/Sidebar.tsx
import { NavLink, useNavigate } from 'react-router-dom';
import { MessageSquare, BookOpen, Wrench, User } from 'lucide-react';
import { authStore } from '../../../features/auth/authStore';
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
