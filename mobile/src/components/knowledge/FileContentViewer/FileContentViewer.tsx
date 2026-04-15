import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Badge } from '../../ui/Badge';
import { colors, typography, spacing, elevation } from '../../../styles';

export interface FileContentViewerProps {
  content: string;
  fileName?: string;
}

export const FileContentViewer: React.FC<FileContentViewerProps> = ({
  content,
  fileName,
}) => {
  if (!content) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>暂无内容</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        {fileName && <Text style={styles.fileName}>{fileName}</Text>}
        <Badge variant="info">只读</Badge>
      </View>
      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        <Text style={styles.markdownText}>{content}</Text>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusLg,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  fileName: {
    flex: 1,
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: spacing[4],
  },
  markdownText: {
    fontSize: typography.textSm,
    color: colors.text,
    lineHeight: typography.textSm * 1.8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing[8],
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
});

export default FileContentViewer;
