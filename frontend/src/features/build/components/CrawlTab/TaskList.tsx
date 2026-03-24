import React, { useState } from 'react';
import { TaskCard } from './TaskCard';
import { ConfirmDialog } from '../ui/ConfirmDialog';
import { CrawlTask } from '../../api/crawl';
import styles from './TaskList.module.css';

interface TaskListProps {
  tasks: CrawlTask[];
  onDelete?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
  onClearCompleted?: () => void;
}

const TERMINAL_STATES = ['SUCCESS', 'FAILED', 'completed', 'failed'];

export const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onDelete,
  onRetry,
  onClearCompleted,
}) => {
  const [showClearConfirm, setShowClearConfirm] = useState(false);

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

  const completedCount = tasks.filter((t) => TERMINAL_STATES.includes(t.status)).length;
  const hasCompletedTasks = completedCount > 0;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.count}>共 {tasks.length} 个任务</span>
        {hasCompletedTasks && onClearCompleted && (
          <button
            className={styles.clearBtn}
            onClick={() => setShowClearConfirm(true)}
          >
            清空已完成
          </button>
        )}
      </div>
      <div className={styles.list} data-testid="task-list-container">
        {sortedTasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onDelete={onDelete}
            onRetry={onRetry}
          />
        ))}
      </div>

      <ConfirmDialog
        isOpen={showClearConfirm}
        title="清空确认"
        message="确定要清空所有已完成的任务吗？此操作不会删除已爬取的文件。"
        confirmText="确认"
        cancelText="取消"
        onConfirm={() => {
          setShowClearConfirm(false);
          onClearCompleted?.();
        }}
        onCancel={() => setShowClearConfirm(false)}
      />
    </div>
  );
};
