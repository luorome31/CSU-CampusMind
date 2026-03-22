// src/components/chat/EmptyState/index.tsx
import React from 'react';
import { EMPTY_STATE_AVATAR } from '../../../utils/avatar';
import './EmptyState.css';

/**
 * Empty state shown when there are no messages.
 * Shows CampusMind branding and system introduction.
 */
export const EmptyState: React.FC = () => {
  return (
    <div className="empty-state">
      <div className="empty-state-logo">
        <img src={EMPTY_STATE_AVATAR} alt="CampusMind" />
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
