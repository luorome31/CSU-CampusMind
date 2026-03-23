import { Plus, Check } from 'lucide-react';
import { Card } from '../../ui';
import { chatStore } from '../../../features/chat/chatStore';
import './KnowledgeCard.css';

export interface KnowledgeCardProps {
  knowledge: {
    id: string;
    name: string;
    description: string;
  };
  fileCount: number;
  onClick: () => void;
  onSelect?: (selected: boolean) => void;
}

export function KnowledgeCard({ knowledge, fileCount, onClick, onSelect }: KnowledgeCardProps) {
  const currentKnowledgeIds = chatStore((s) => s.currentKnowledgeIds);
  const isInChat = currentKnowledgeIds.includes(knowledge.id);

  const handleSelectClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onSelect) {
      onSelect(!isInChat);
    } else {
      // Default behavior: toggle in chatStore
      const store = chatStore.getState();
      if (isInChat) {
        store.setCurrentKnowledgeIds(currentKnowledgeIds.filter(id => id !== knowledge.id));
      } else {
        store.setCurrentKnowledgeIds([...currentKnowledgeIds, knowledge.id]);
      }
    }
  };

  return (
    <Card
      className={`knowledge-card ${isInChat ? 'knowledge-card-selected' : ''}`}
      onClick={onClick}
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      <span className="knowledge-card-badge">{fileCount} 个文件</span>
      <div className="knowledge-card-header">
        <h3 className="knowledge-card-title">{knowledge.name}</h3>
      </div>
      <p className="knowledge-card-description">{knowledge.description}</p>
      <button
        className={`knowledge-card-select ${isInChat ? 'selected' : ''}`}
        onClick={handleSelectClick}
        title={isInChat ? '从聊天中移除' : '添加到聊天'}
      >
        {isInChat ? <Check size={16} /> : <Plus size={16} />}
        <span>{isInChat ? '已添加' : '添加'}</span>
      </button>
    </Card>
  );
}
