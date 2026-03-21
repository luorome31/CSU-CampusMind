// src/components/chat/EmptyState/index.tsx
import React from 'react';
import './EmptyState.css';

/**
 * Empty state shown when there are no messages.
 * Shows CampusMind branding and system introduction.
 */
export const EmptyState: React.FC = () => {
  return (
    <div className="empty-state">
      <div className="empty-state-logo">
        <svg
          width="64"
          height="64"
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="32" cy="32" r="30" stroke="var(--color-accent)" strokeWidth="2" />
          <path
            d="M32 16C23.163 16 16 23.163 16 32s7.163 16 16 16 16-7.163 16-16-7.163-16-16-16zm0 4c6.627 0 12 5.373 12 12s-5.373 12-12 12-12-5.373-12-12 5.373-12 12-12z"
            fill="var(--color-accent)"
          />
          <circle cx="32" cy="32" r="4" fill="var(--color-accent)" />
        </svg>
      </div>
      <h1 className="empty-state-title">CampusMind</h1>
      <p className="empty-state-subtitle">你的智能校园助手</p>
      <ul className="empty-state-features">
        <li>查询成绩和课表</li>
        <li>了解校园通知和活动</li>
        <li>获取选课和教务信息</li>
      </ul>
    </div>
  );
};

export default EmptyState;
