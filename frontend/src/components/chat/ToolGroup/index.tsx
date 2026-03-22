import { useState } from 'react';
import './ToolGroup.css';

interface Tool {
  name: string;
  status: 'running' | 'done' | 'error';
  result?: string;
}

interface ToolGroupProps {
  tools: Tool[];
}

function LoadingDots() {
  return (
    <span style={{ display: 'inline-flex', gap: '4px' }}>
      <span style={{ animation: 'bounce 1.4s infinite', animationDelay: '0s' }}>.</span>
      <span style={{ animation: 'bounce 1.4s infinite', animationDelay: '0.2s' }}>.</span>
      <span style={{ animation: 'bounce 1.4s infinite', animationDelay: '0.4s' }}>.</span>
    </span>
  );
}

export function ToolGroup({ tools }: ToolGroupProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const allDone = tools.every((t) => t.status === 'done');
  const doneCount = tools.filter((t) => t.status === 'done').length;

  return (
    <div className="tool-group">
      <div
        className="tool-group-summary"
        onClick={() => setIsExpanded(!isExpanded)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setIsExpanded(!isExpanded)}
      >
        {allDone ? (
          <>
            <span>✓</span>
            <span>执行完成 {tools.length} 个工具</span>
          </>
        ) : (
          <>
            <LoadingDots />
            <span>运行中 {doneCount}/{tools.length} 个工具</span>
          </>
        )}
      </div>
      {isExpanded && (
        <div className="tool-group-details">
          {tools.map((tool, i) => (
            <div key={i} style={{ fontSize: '0.8rem', marginBottom: '4px' }}>
              <span style={{ color: tool.status === 'done' ? 'var(--green)' : 'var(--coral)' }}>
                {tool.status === 'done' ? '✓' : '○'}
              </span>
              <span style={{ marginLeft: '8px' }}>{tool.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
