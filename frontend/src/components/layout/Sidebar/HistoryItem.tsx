// src/components/layout/Sidebar/HistoryItem.tsx
import React, { useEffect, useState } from 'react';
import { MessageSquare, Trash2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import './HistoryItem.css';

interface HistoryItemProps {
  id: string;
  title?: string;
  updatedAt: string;
  isActive: boolean;
  onClick: () => void;
  onDelete: (e: React.MouseEvent) => void;
}

export function HistoryItem({
  id,
  title,
  updatedAt,
  isActive,
  onClick,
  onDelete,
}: HistoryItemProps) {
  const [displayTitle, setDisplayTitle] = useState(title || '新对话');
  const [isUpdating, setIsUpdating] = useState(false);

  // Graceful title transition effect
  useEffect(() => {
    if (title && title !== displayTitle) {
      setIsUpdating(true);
      const timer = setTimeout(() => {
        setDisplayTitle(title);
        setIsUpdating(false);
      }, 300); // Match CSS transition time
      return () => clearTimeout(timer);
    }
  }, [title]);

  return (
    <div
      className={`history-item ${isActive ? 'active' : ''} ${
        isUpdating ? 'updating' : ''
      }`}
      data-dialog-id={id}
      onClick={onClick}
    >
      <MessageSquare size={14} className="history-item-icon" />
      <div className="history-item-content">
        <span className="history-item-title">{displayTitle}</span>
        <span className="history-item-time">
          {formatDistanceToNow(new Date(updatedAt), {
            addSuffix: true,
            locale: zhCN,
          })}
        </span>
      </div>
      <button className="history-item-delete" onClick={onDelete}>
        <Trash2 size={12} />
      </button>
    </div>
  );
}
