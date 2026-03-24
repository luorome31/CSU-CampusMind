import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { StatsGrid } from './StatsGrid';

vi.mock('../profileStore', () => ({
  profileStore: vi.fn(() => ({
    stats: {
      conversation_count: 42,
      message_count: 156,
      knowledge_base_count: 3,
      join_date: '2026-01',
    },
    user: null,
  })),
}));

describe('StatsGrid', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all stat cards', () => {
    render(<StatsGrid />);
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('156')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('对话数')).toBeInTheDocument();
    expect(screen.getByText('消息数')).toBeInTheDocument();
    expect(screen.getByText('知识库数')).toBeInTheDocument();
  });

  it('renders stats title', () => {
    render(<StatsGrid />);
    expect(screen.getByText('使用统计')).toBeInTheDocument();
  });

  it('renders all stat labels', () => {
    render(<StatsGrid />);
    expect(screen.getByText('注册时间')).toBeInTheDocument();
  });
});
