import { Card } from '../../ui';
import './KnowledgeCard.css';

export interface KnowledgeCardProps {
  knowledge: {
    id: string;
    name: string;
    description: string;
  };
  fileCount: number;
  onClick: () => void;
}

export function KnowledgeCard({ knowledge, fileCount, onClick }: KnowledgeCardProps) {
  return (
    <Card
      className="knowledge-card"
      onClick={onClick}
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      <div className="knowledge-card-header">
        <h3 className="knowledge-card-title">{knowledge.name}</h3>
        <span className="knowledge-card-badge">{fileCount} 个文件</span>
      </div>
      <p className="knowledge-card-description">{knowledge.description}</p>
    </Card>
  );
}
