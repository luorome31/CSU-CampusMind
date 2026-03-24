import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ReviewInbox } from './ReviewInbox';

describe('ReviewInbox', () => {
  const mockToggle = vi.fn();

  it('should render empty state when no files', () => {
    render(<ReviewInbox isCollapsed={false} onToggleCollapse={mockToggle} />);
    expect(screen.getByText(/暂无待审核文件/)).toBeInTheDocument();
  });

  it('should render collapsed state', () => {
    render(<ReviewInbox isCollapsed={true} onToggleCollapse={mockToggle} />);
    expect(screen.queryByText(/暂无待审核文件/)).not.toBeInTheDocument();
  });
});
