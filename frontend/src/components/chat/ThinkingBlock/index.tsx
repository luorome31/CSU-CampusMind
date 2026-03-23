// src/components/chat/ThinkingBlock/index.tsx
import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Brain, ChevronsUpDown, ChevronsDownUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ThinkingBlock.css';

interface ThinkingBlockProps {
  thinking: string[];
}

/**
 * Renders AI thinking process in a collapsible format.
 * Each thinking block can be expanded to view the full thought process.
 */
export const ThinkingBlock: React.FC<ThinkingBlockProps> = ({ thinking }) => {
  const [expandedBlocks, setExpandedBlocks] = useState<Set<number>>(new Set());

  const toggleBlock = (index: number) => {
    setExpandedBlocks((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const expandAll = () => {
    setExpandedBlocks(new Set(thinking.map((_, i) => i)));
  };

  const collapseAll = () => {
    setExpandedBlocks(new Set());
  };

  const allExpanded = expandedBlocks.size === thinking.length;
  const isExpanded = expandedBlocks.size > 0;

  if (thinking.length === 0) {
    return null;
  }

  return (
    <div className="thinking-block">
      <div className="thinking-header">
        <Brain className="thinking-icon" size={16} />
        <span className="thinking-label">AI 思考过程</span>
        <span className="thinking-count">({thinking.length})</span>
        <div className="thinking-actions">
          <button
            className="thinking-action-btn"
            onClick={allExpanded ? collapseAll : expandAll}
            type="button"
            title={allExpanded ? '收起全部' : '展开全部'}
          >
            {allExpanded ? (
              <ChevronsDownUp size={16} />
            ) : (
              <ChevronsUpDown size={16} />
            )}
          </button>
        </div>
      </div>
      {isExpanded && (
        <div className="thinking-content">
          {thinking.map((thought, index) => (
            <div key={index} className="thinking-item">
              <button
                className="thinking-item-header"
                onClick={() => toggleBlock(index)}
                type="button"
                aria-expanded={expandedBlocks.has(index)}
              >
                <span className="thinking-item-chevron">
                  {expandedBlocks.has(index) ? (
                    <ChevronDown size={14} />
                  ) : (
                    <ChevronRight size={14} />
                  )}
                </span>
                <span className="thinking-item-label">
                  步骤 {index + 1}
                </span>
              </button>
              {expandedBlocks.has(index) && (
                <div className="thinking-item-body">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {thought}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ThinkingBlock;
