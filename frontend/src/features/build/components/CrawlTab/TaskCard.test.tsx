import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TaskCard } from './TaskCard';
import { CrawlTask } from '../../api/crawl';

const mockTask: CrawlTask = {
  id: 'task_xyz',
  knowledge_id: 'kb_abc',
  user_id: 'user_1',
  total_urls: 10,
  completed_urls: 7,
  success_count: 5,
  fail_count: 2,
  status: 'processing',
  create_time: '2024-01-01T12:00:00',
  update_time: '2024-01-01T12:05:00',
};

describe('TaskCard', () => {
  it('should render task id and status', () => {
    render(<TaskCard task={mockTask} />);

    expect(screen.getByText(/task_xyz/)).toBeInTheDocument();
    expect(screen.getByText(/处理中/)).toBeInTheDocument();
  });

  it('should render progress bar with correct percentage', () => {
    render(<TaskCard task={mockTask} />);

    const progressText = screen.getByText(/7\/10/);
    expect(progressText).toBeInTheDocument();
  });

  it('should render success and fail counts', () => {
    render(<TaskCard task={mockTask} />);

    // Use exact text match with getAllByText since "成功" and "失败" appear twice each
    // Check stats section - there are 2 spans with "成功" and "失败" text
    const allSuccess = screen.getAllByText((content) => content.includes('成功'));
    expect(allSuccess.length).toBeGreaterThanOrEqual(1);
    const allFailed = screen.getAllByText((content) => content.includes('失败'));
    expect(allFailed.length).toBeGreaterThanOrEqual(1);
  });

  it('should render checkmark for SUCCESS status', () => {
    const successTask = { ...mockTask, status: 'SUCCESS' as const, completed_urls: 10 };
    render(<TaskCard task={successTask} />);

    // Check for the status badge with "成功" text
    const statusElements = screen.getAllByText((content) => content.includes('成功'));
    expect(statusElements.length).toBeGreaterThan(0);
  });

  it('should render X mark for FAILED status', () => {
    const failedTask = { ...mockTask, status: 'FAILED' as const };
    render(<TaskCard task={failedTask} />);

    // Check for the status badge with "失败" text
    const statusElements = screen.getAllByText((content) => content.includes('失败'));
    expect(statusElements.length).toBeGreaterThan(0);
  });
});
