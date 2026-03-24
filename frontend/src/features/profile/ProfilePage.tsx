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
