import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TaskList } from './TaskList';
import { CrawlTask } from '../../api/crawl';

const mockTasks: CrawlTask[] = [
  {
    id: 'task_1',
    knowledge_id: 'kb_1',
    user_id: 'user_1',
    total_urls: 10,
    completed_urls: 10,
    success_count: 8,
    fail_count: 2,
    status: 'SUCCESS',
    create_time: '2024-01-01T12:00:00',
    update_time: '2024-01-01T12:05:00',
  },
  {
    id: 'task_2',
    knowledge_id: 'kb_1',
    user_id: 'user_1',
    total_urls: 5,
    completed_urls: 2,
    success_count: 2,
    fail_count: 0,
    status: 'processing',
    create_time: '2024-01-02T12:00:00',
    update_time: '2024-01-02T12:03:00',
  },
];

describe('TaskList', () => {
  it('should render empty state when no tasks', () => {
    render(<TaskList tasks={[]} />);
    expect(screen.getByText(/暂无爬取任务/)).toBeInTheDocument();
  });

  it('should render list of tasks', () => {
    render(<TaskList tasks={mockTasks} />);
    expect(screen.getByText(/task_1/)).toBeInTheDocument();
    expect(screen.getByText(/task_2/)).toBeInTheDocument();
  });

  it('should render task count', () => {
    render(<TaskList tasks={mockTasks} />);
    expect(screen.getByText(/共 2 个任务/)).toBeInTheDocument();
  });
});
