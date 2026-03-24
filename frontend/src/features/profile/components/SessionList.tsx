import { Monitor, Smartphone, LogOut } from 'lucide-react';
import { profileStore } from '../profileStore';
import './SessionList.css';

export function SessionList() {
  const { sessions, revokeSession } = profileStore();

  const getDeviceIcon = (device: string) => {
    const d = device.toLowerCase();
    if (d.includes('mobile') || d.includes('iphone') || d.includes('android') || d.includes('ipad')) {
      return Smartphone;
    }
    return Monitor;
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));

    if (minutes < 1) return '刚刚';
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
