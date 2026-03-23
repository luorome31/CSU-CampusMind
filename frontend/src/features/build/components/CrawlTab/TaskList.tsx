import React from 'react';
import { TaskCard } from './TaskCard';
import { CrawlTask } from '../../api/crawl';

interface TaskListProps {
  tasks: CrawlTask[];
}

export const TaskList: React.FC<TaskListProps> = ({ tasks }) => {
  if (tasks.length === 0) {
    return (
      <div style={{
        textAlign: 'center',
        padding: 'var(--space-8, 32px)',
        color: 'var(--color-text-secondary, #666)',
      }}>
        暂无爬取任务
      </div>
    );
  }

  // Sort by create_time descending (newest first)
  const sortedTasks = [...tasks].sort(
    (a, b) => new Date(b.create_time).getTime() - new Date(a.create_time).getTime()
  );

  return (
    <div>
      <div style={{
        fontSize: 'var(--text-sm, 14px)',
        color: 'var(--color-text-secondary, #666)',
        marginBottom: 'var(--space-3, 12px)',
      }}>
        共 {tasks.length} 个任务
      </div>
      {sortedTasks.map((task) => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
};
