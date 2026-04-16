import React from 'react';
import { View, StyleSheet, FlatList, Pressable } from 'react-native';
import { Text } from '@/components/ui/StyledText';
import { Badge } from '../../ui/Badge';
import { colors, typography, spacing, elevation } from '../../../styles';
import type { KnowledgeFile } from '../../../api/knowledge';

export interface FileTableProps {
  files: KnowledgeFile[];
  onFileClick: (file: KnowledgeFile) => void;
}

const STATUS_LABELS: Record<KnowledgeFile['status'], string> = {
  process: '处理中',
  indexing: '索引中',
  success: '成功',
  verified: '已验证',
  indexed: '已索引',
  fail: '失败',
  pending_verify: '待验证',
};

const STATUS_VARIANT: Record<KnowledgeFile['status'], 'success' | 'error' | 'warning' | 'info'> = {
  process: 'warning',
  indexing: 'info',
  success: 'success',
  verified: 'success',
  indexed: 'success',
  fail: 'error',
  pending_verify: 'warning',
};

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) {
    return '无效日期';
  }
  const datePart = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  const timePart = `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
  return `${datePart} ${timePart}`;
}

export const FileTable: React.FC<FileTableProps> = ({ files, onFileClick }) => {
  if (files.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>暂无文件</Text>
      </View>
    );
  }

  const renderItem = ({ item }: { item: KnowledgeFile }) => (
    <Pressable
      style={styles.row}
      onPress={() => onFileClick(item)}
      accessibilityRole="button"
      accessibilityLabel={`文件 ${item.file_name}`}
    >
      <View style={styles.nameCell}>
        <Text style={styles.fileName} numberOfLines={1}>
          {item.file_name}
        </Text>
      </View>
      <View style={styles.statusCell}>
        <Badge variant={STATUS_VARIANT[item.status]}>
          {STATUS_LABELS[item.status]}
        </Badge>
      </View>
      <View style={styles.dateCell}>
        <Text style={styles.dateText}>{formatDate(item.update_time)}</Text>
      </View>
    </Pressable>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerText}>文件名</Text>
        <Text style={styles.headerText}>状态</Text>
        <Text style={styles.headerText}>更新时间</Text>
      </View>
      {/* Body */}
      <FlatList
        data={files}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        scrollEnabled={false}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusLg,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    backgroundColor: colors.moodBg,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  headerText: {
    flex: 1,
    fontSize: typography.textXs,
    fontWeight: typography.fontMedium,
    color: colors.textLight,
  },
  row: {
    flexDirection: 'row',
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
    alignItems: 'center',
  },
  nameCell: {
    flex: 1,
    marginRight: spacing[2],
  },
  fileName: {
    fontSize: typography.textSm,
    color: colors.text,
  },
  statusCell: {
    width: 70,
    alignItems: 'center',
  },
  dateCell: {
    width: 80,
    alignItems: 'flex-end',
  },
  dateText: {
    fontSize: typography.textXs,
    color: colors.textMuted,
  },
  emptyContainer: {
    padding: spacing[8],
    alignItems: 'center',
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
});

export default FileTable;
