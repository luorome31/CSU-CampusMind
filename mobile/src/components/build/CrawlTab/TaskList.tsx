import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { TaskCard } from './TaskCard';
import { useBuildStore } from '../../../features/build/buildStore';
import { colors, typography, spacing } from '../../../styles';

interface TaskListProps {
  onDelete?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
}

export function TaskList({ onDelete, onRetry }: TaskListProps) {
  const tasks = useBuildStore((s) => s.tasks);
  const removeTask = useBuildStore((s) => s.removeTask);
  const retryFailedUrls = useBuildStore((s) => s.retryFailedUrls);

  const handleDelete = onDelete || removeTask;
  const handleRetry = onRetry || retryFailedUrls;

  if (tasks.length === 0) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>暂无爬取任务</Text>
      </View>
    );
  }

  // Sort by create_time descending (newest first)
  const sortedTasks = [...tasks].sort(
    (a, b) => new Date(b.create_time).getTime() - new Date(a.create_time).getTime()
  );

  return (
    <View style={styles.container}>
      <Text style={styles.header}>任务列表 ({tasks.length})</Text>
      {sortedTasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onDelete={handleDelete}
          onRetry={handleRetry}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: spacing[4],
  },
  header: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
    marginBottom: spacing[3],
  },
  empty: {
    padding: spacing[8],
    alignItems: 'center',
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
});
