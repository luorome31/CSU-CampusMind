import React from 'react';
import { Check, X, Loader2 } from 'lucide-react';
import { CrawlTask } from '../../api/crawl';
import styles from './TaskCard.module.css';

interface TaskCardProps {
  task: CrawlTask;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task }) => {
  const progress = task.total_urls > 0
    ? Math.round((task.completed_urls / task.total_urls) * 100)
    : 0;

  const getStatusDisplay = () => {
    switch (task.status) {
      case 'SUCCESS':
      case 'completed':
        return { icon: <Check size={16} />, text: '成功', className: styles.success };
      case 'FAILED':
        return { icon: <X size={16} />, text: '失败', className: styles.failed };
      case 'processing':
        return { icon: <Loader2 size={16} className={styles.spinning} />, text: '处理中', className: styles.processing };
      case 'pending':
      default:
        return { icon: <Loader2 size={16} className={styles.spinning} />, text: '等待中', className: styles.pending };
    }
  };

  const status = getStatusDisplay();

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.taskId}>Task ID: {task.id}</span>
        <span className={`${styles.status} ${status.className}`}>
          {status.icon}
          {status.text}
        </span>
      </div>

      <div className={styles.progress}>
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className={styles.progressText}>
          {task.completed_urls}/{task.total_urls}
        </span>
      </div>

      <div className={styles.stats}>
        <span>成功: {task.success_count}</span>
        <span>失败: {task.fail_count}</span>
        <span className={styles.date}>{formatDate(task.create_time)}</span>
      </div>
    </div>
  );
};
