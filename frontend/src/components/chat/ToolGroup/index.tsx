import { useState } from 'react';
import type { ToolEvent } from '../../../features/chat/chatStore';
import './ToolGroup.css';

interface ToolGroupProps {
  events: ToolEvent[];
}

function LoadingDots() {
  return (
    <span className="tool-group-loading">
      <span className="dot" />
      <span className="dot" />
      <span className="dot" />
    </span>
  );
}

export function ToolGroup({ events }: ToolGroupProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const doneCount = events.filter((e) => e.status === 'END').length;
  const errorCount = events.filter((e) => e.status === 'ERROR').length;
  const allDone = doneCount + errorCount === events.length && events.length > 0;

  const getStatusIcon = () => {
    if (allDone) {
      return <span className="tool-group-icon tool-group-icon-done">✓</span>;
    }
    return <LoadingDots />;
  };

  const getStatusText = () => {
    if (events.length === 0) return '等待工具执行...';
    if (allDone) {
      return errorCount > 0
        ? `执行完成 ${doneCount} 个工具，${errorCount} 个错误`
        : `执行完成 ${doneCount} 个工具`;
    }
    return `运行中 ${doneCount}/${events.length} 个工具`;
  };

  if (events.length === 0) {
    return null;
  }

  return (
    <div className="tool-group">
      <button
        className="tool-group-summary"
        onClick={() => setIsExpanded(!isExpanded)}
        type="button"
      >
        {getStatusIcon()}
        <span className="tool-group-text">{getStatusText()}</span>
        <span className={`tool-group-chevron ${isExpanded ? 'expanded' : ''}`}>
          ▾
        </span>
      </button>
      {isExpanded && (
        <div className="tool-group-details">
          {events.map((event) => {
            const isEnd = event.status === 'END';
            const isError = event.status === 'ERROR';
            return (
              <div key={event.id} className="tool-group-item">
                <span
                  className={`tool-group-status ${
                    isEnd
                      ? 'tool-group-status-done'
                      : isError
                        ? 'tool-group-status-error'
                        : 'tool-group-status-running'
                  }`}
                >
                  {isEnd ? '✓' : isError ? '✗' : '○'}
                </span>
                <span className="tool-group-item-title">{event.title}</span>
                {event.message && (
                  <span className="tool-group-item-msg">{event.message}</span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
