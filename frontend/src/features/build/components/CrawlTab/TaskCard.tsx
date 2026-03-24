import React, { useState } from 'react';
import { Check, X, Loader2, Trash2, RotateCw, ChevronDown, ChevronUp } from 'lucide-react';
import { CrawlTask } from '../../api/crawl';
import styles from './TaskCard.module.css';

interface TaskCardProps {
  task: CrawlTask;
  onDelete?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
}

const TERMINAL_STATES = ['SUCCESS', 'FAILED', 'completed', 'failed'];

export const TaskCard: React.FC<TaskCardProps> = ({ task, onDelete, onRetry }) => {
  const [showFailedDetails, setShowFailedDetails] = useState(false);

  const progress = task.total_urls > 0
    ? Math.round((task.completed_urls / task.total_urls) * 100)
    : 0;

  const isTerminal = TERMINAL_STATES.includes(task.status);
  const hasFailedUrls = (task.failed_urls?.length ?? 0) > 0;
  const canRetry = isTerminal && hasFailedUrls && task.knowledge_id;

  const getStatusDisplay = () => {
    // For completed status, determine exact state
    if (task.status === 'completed' || task.status === 'SUCCESS') {
      if (task.fail_count === 0) {
        return { icon: <Check size={16} />, text: '成功', className: styles.success };
      } else if (task.success_count === 0) {
        return { icon: <X size={16} />, text: '失败', className: styles.failed };
      } else {
        return { icon: <X size={16} />, text: '部分成功', className: styles.partial };
      }
    }
    switch (task.status) {
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

  const handleDelete = () => {
    if (isTerminal && onDelete) {
      onDelete(task.id);
    }
  };

  const handleRetry = () => {
    if (canRetry && onRetry) {
      onRetry(task.id);
    }
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.taskId}>Task ID: {task.id.slice(0, 8)}</span>
        <div className={styles.actions}>
          {canRetry && onRetry && (
            <button
              className={styles.actionBtn}
              onClick={handleRetry}
              title="重试失败链接"
            >
              <RotateCw size={16} />
              <span>重试</span>
            </button>
          )}
          {isTerminal && onDelete && (
            <button
              className={`${styles.actionBtn} ${styles.deleteBtn}`}
              onClick={handleDelete}
              disabled={!isTerminal}
              aria-label="删除任务"
              title="删除任务"
            >
              <Trash2 size={16} />
            </button>
          )}
          <span className={`${styles.status} ${status.className}`}>
            {status.icon}
            {status.text}
          </span>
        </div>
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
        <span className={styles.successStat}>成功: {task.success_count}</span>
        <span className={task.fail_count > 0 ? styles.failStat : ''}>失败: {task.fail_count}</span>
        <span className={styles.date}>{formatDate(task.create_time)}</span>
      </div>

      {hasFailedUrls && (
        <div className={styles.failedSection}>
          <button
            className={styles.failedToggle}
            onClick={() => setShowFailedDetails(!showFailedDetails)}
          >
            {showFailedDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            <span>查看失败详情 ({task.failed_urls?.length})</span>
          </button>
          {showFailedDetails && (
            <ul className={styles.failedList}>
              {task.failed_urls?.map((failed, idx) => (
                <li key={idx} className={styles.failedItem}>
                  <span className={styles.failedUrl}>{failed.url}</span>
                  <span className={styles.failedError}>{failed.error}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};
