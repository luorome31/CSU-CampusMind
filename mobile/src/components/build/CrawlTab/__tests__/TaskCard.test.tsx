import React from 'react';
import { render } from '@testing-library/react-native';
import { TaskCard } from '../TaskCard';

const mockTask = {
  id: 'task-123',
  knowledge_id: 'kb-1',
  user_id: 'user-1',
  total_urls: 10,
  completed_urls: 5,
  success_count: 4,
  fail_count: 1,
  status: 'processing' as const,
  create_time: '2024-04-15T10:00:00Z',
  update_time: '2024-04-15T10:05:00Z',
};

describe('TaskCard', () => {
  it('should render task progress', () => {
    const { getByText } = render(
      <TaskCard task={mockTask} onDelete={jest.fn()} onRetry={jest.fn()} />
    );

    expect(getByText('5/10')).toBeTruthy();
  });

  it('should render status text', () => {
    const { getByText } = render(
      <TaskCard task={mockTask} onDelete={jest.fn()} onRetry={jest.fn()} />
    );

    expect(getByText('处理中')).toBeTruthy();
  });
});
