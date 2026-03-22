import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EmptyState } from './index';

describe('EmptyState', () => {
  it('renders the logo SVG', () => {
    render(<EmptyState />);
    // The EmptyState renders an SVG with a circle
    expect(document.querySelector('.empty-state-logo svg')).toBeInTheDocument();
  });

  it('renders the application title', () => {
    render(<EmptyState />);
    expect(screen.getByText('CampusMind')).toBeInTheDocument();
  });

  it('renders the Chinese subtitle', () => {
    render(<EmptyState />);
    expect(screen.getByText('你的智能校园助手')).toBeInTheDocument();
  });

  it('renders the feature list', () => {
    render(<EmptyState />);
    expect(screen.getByText('查询成绩和课表')).toBeInTheDocument();
    expect(screen.getByText('了解校园通知和活动')).toBeInTheDocument();
    expect(screen.getByText('获取选课和教务信息')).toBeInTheDocument();
  });

  it('has correct CSS classes for styling', () => {
    render(<EmptyState />);
    const container = document.querySelector('.empty-state');
    expect(container).toBeInTheDocument();
  });
});
