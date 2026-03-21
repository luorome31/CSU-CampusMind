// src/components/chat/KnowledgeSelector/index.tsx
import React from 'react';
import { X } from 'lucide-react';
import { Chip } from '../../ui/Chip';
import { chatStore } from '../../../features/chat/chatStore';
import './KnowledgeSelector.css';

interface KnowledgeBase {
  id: string;
  name: string;
}

interface KnowledgeSelectorProps {
  knowledgeBases: KnowledgeBase[];
}

/**
 * Knowledge base selector shown above the message list.
 * Users select which knowledge bases to include in RAG.
 */
export const KnowledgeSelector: React.FC<KnowledgeSelectorProps> = ({
  knowledgeBases,
}) => {
  const currentKnowledgeIds = chatStore((s) => s.currentKnowledgeIds);
  const setCurrentKnowledgeIds = chatStore((s) => s.setCurrentKnowledgeIds);

  const handleToggle = (kbId: string) => {
    if (currentKnowledgeIds.includes(kbId)) {
      setCurrentKnowledgeIds(currentKnowledgeIds.filter((id: string) => id !== kbId));
    } else {
      setCurrentKnowledgeIds([...currentKnowledgeIds, kbId]);
    }
  };

  return (
    <div className="knowledge-selector">
      <span className="knowledge-selector-label">知识库</span>
      <div className="knowledge-selector-chips">
        {knowledgeBases.map((kb) => {
          const isSelected = currentKnowledgeIds.includes(kb.id);
          return (
            <Chip
              key={kb.id}
              variant={isSelected ? 'active' : 'default'}
              onClick={() => handleToggle(kb.id)}
            >
              {kb.name}
            </Chip>
          );
        })}
      </div>
      {currentKnowledgeIds.length > 0 && (
        <button
          className="knowledge-selector-clear"
          onClick={() => setCurrentKnowledgeIds([])}
          type="button"
        >
          <X size={14} />
          清除
        </button>
      )}
    </div>
  );
};

export default KnowledgeSelector;
