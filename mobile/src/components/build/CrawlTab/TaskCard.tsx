import React, { useState } from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { Check, X, Loader2, Trash2, RotateCw, ChevronDown, ChevronUp } from 'lucide-react-native';
import { CrawlTask } from '../../../api/crawl';
import { colors, typography, spacing, elevation } from '../../../styles';

interface TaskCardProps {
  task: CrawlTask;
  onDelete?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
}

const TERMINAL_STATES = ['SUCCESS', 'FAILED', 'completed', 'failed'];

export function TaskCard({ task, onDelete, onRetry }: TaskCardProps) {
  const [showFailedDetails, setShowFailedDetails] = useState(false);

  const progress = task.total_urls > 0
    ? Math.round((task.completed_urls / task.total_urls) * 100)
    : 0;

  const isTerminal = TERMINAL_STATES.includes(task.status);
  const hasFailedUrls = (task.failed_urls?.length ?? 0) > 0;
  const canRetry = isTerminal && hasFailedUrls && task.knowledge_id;

  const getStatusDisplay = () => {
    if (task.success_count === 0 && task.fail_count > 0) {
      return { icon: <X size={14} color={colors.error} />, text: '失败', style: styles.statusFailed };
    }

    if (task.status === 'completed' || task.status === 'SUCCESS') {
      if (task.fail_count === 0) {
        return { icon: <Check size={14} color={colors.success} />, text: '成功', style: styles.statusSuccess };
      } else {
        return { icon: <X size={14} color={colors.warning} />, text: '部分成功', style: styles.statusPartial };
      }
    }

    switch (task.status) {
      case 'FAILED':
        return { icon: <X size={14} color={colors.error} />, text: '失败', style: styles.statusFailed };
      case 'processing':
        return { icon: <Loader2 size={14} color={colors.accent} />, text: '处理中', style: styles.statusProcessing };
      case 'pending':
      default:
        return { icon: <Loader2 size={14} color={colors.textMuted} />, text: '等待中', style: styles.statusPending };
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
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.taskId}>Task: {task.id.slice(0, 8)}</Text>
        <View style={styles.actions}>
          {canRetry && onRetry && (
            <Pressable style={styles.actionBtn} onPress={() => onRetry(task.id)}>
              <RotateCw size={14} color={colors.accent} />
              <Text style={styles.actionText}>重试</Text>
            </Pressable>
          )}
          {isTerminal && onDelete && (
            <Pressable style={styles.actionBtn} onPress={() => onDelete(task.id)}>
              <Trash2 size={14} color={colors.error} />
            </Pressable>
          )}
          <View style={[styles.statusBadge, status.style]}>
            {status.icon}
            <Text style={[styles.statusText, status.style]}>{status.text}</Text>
          </View>
        </View>
      </View>

      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${progress}%` }]} />
        </View>
        <Text style={styles.progressText}>{task.completed_urls}/{task.total_urls}</Text>
      </View>

      <View style={styles.stats}>
        <Text style={styles.statText}>成功: {task.success_count}</Text>
        <Text style={[styles.statText, task.fail_count > 0 && styles.failStat]}>失败: {task.fail_count}</Text>
        <Text style={styles.dateText}>{formatDate(task.create_time)}</Text>
      </View>

      {hasFailedUrls && (
        <Pressable
          style={styles.failedToggle}
          onPress={() => setShowFailedDetails(!showFailedDetails)}
        >
          {showFailedDetails ? (
            <ChevronUp size={12} color={colors.textMuted} />
          ) : (
            <ChevronDown size={12} color={colors.textMuted} />
          )}
          <Text style={styles.failedToggleText}>查看失败详情 ({task.failed_urls?.length})</Text>
        </Pressable>
      )}

      {showFailedDetails && (
        <View style={styles.failedList}>
          {task.failed_urls?.map((failed, idx) => (
            <View key={idx} style={styles.failedItem}>
              <Text style={styles.failedUrl} numberOfLines={1}>{failed.url}</Text>
              <Text style={styles.failedError}>{failed.error}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusLg,
    padding: spacing[4],
    marginBottom: spacing[3],
    ...elevation.shadowCard,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing[3],
  },
  taskId: {
    fontSize: typography.textSm,
    color: colors.textMuted,
    fontFamily: 'monospace',
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[2],
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[1],
    gap: 2,
  },
  actionText: {
    fontSize: typography.textXs,
    color: colors.accent,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing[2],
    paddingVertical: spacing[1],
    borderRadius: elevation.radiusMd,
    gap: 4,
  },
  statusSuccess: { backgroundColor: colors.successBg },
  statusFailed: { backgroundColor: colors.errorBg },
  statusPartial: { backgroundColor: colors.warningBg },
  statusProcessing: { backgroundColor: colors.accentLight },
  statusPending: { backgroundColor: colors.backgroundGlass },
  statusText: {
    fontSize: typography.textXs,
    fontWeight: typography.fontMedium,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing[2],
  },
  progressBar: {
    flex: 1,
    height: 6,
    backgroundColor: colors.backgroundGlass,
    borderRadius: 3,
    marginRight: spacing[2],
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.accent,
    borderRadius: 3,
  },
  progressText: {
    fontSize: typography.textXs,
    color: colors.textMuted,
    fontFamily: 'monospace',
  },
  stats: {
    flexDirection: 'row',
    gap: spacing[4],
  },
  statText: {
    fontSize: typography.textXs,
    color: colors.textSecondary,
  },
  failStat: {
    color: colors.error,
  },
  dateText: {
    fontSize: typography.textXs,
    color: colors.textMuted,
    marginLeft: 'auto',
  },
  failedToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing[2],
    paddingTop: spacing[2],
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
    gap: 4,
  },
  failedToggleText: {
    fontSize: typography.textXs,
    color: colors.textMuted,
  },
  failedList: {
    marginTop: spacing[2],
    paddingTop: spacing[2],
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
  failedItem: {
    paddingVertical: spacing[1],
  },
  failedUrl: {
    fontSize: typography.textXs,
    color: colors.text,
    fontFamily: 'monospace',
  },
  failedError: {
    fontSize: typography.textXs,
    color: colors.error,
  },
});
