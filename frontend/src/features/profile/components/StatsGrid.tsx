import { MessageSquare, MessageCircle, BookOpen, Calendar } from 'lucide-react';
import { profileStore } from '../profileStore';
import './StatsGrid.css';

export function StatsGrid() {
  const { stats, user } = profileStore();

  const joinDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit' })
    : '-';

  const items = [
    {
      icon: MessageSquare,
      label: '对话数',
      value: stats?.conversation_count ?? '-',
    },
    {
      icon: MessageCircle,
      label: '消息数',
      value: stats?.message_count ?? '-',
    },
    {
      icon: BookOpen,
      label: '知识库数',
      value: stats?.knowledge_base_count ?? '-',
    },
    {
      icon: Calendar,
      label: '注册时间',
      value: stats?.join_date || joinDate,
    },
  ];

  return (
    <div className="stats-grid">
      <h3 className="stats-title">使用统计</h3>
      <div className="stats-cards">
        {items.map((item) => (
          <div key={item.label} className="stat-card">
            <item.icon size={24} className="stat-icon" />
            <div className="stat-value">{item.value}</div>
            <div className="stat-label">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
