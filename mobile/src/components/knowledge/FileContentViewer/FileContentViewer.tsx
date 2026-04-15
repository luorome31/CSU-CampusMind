import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import ReactMarkdown from 'react-native-markdown-display';
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
        <ReactMarkdown style={markdownStyles}>{content}</ReactMarkdown>
      </ScrollView>
    </View>
  );
};

// Markdown styles matching warm paper theme
const markdownStyles = StyleSheet.create({
  body: {
    fontSize: typography.textSm,
    color: colors.text,
    lineHeight: typography.textSm * 1.8,
  },
  heading1: {
    fontSize: typography.textXl,
    fontWeight: typography.fontBold,
    color: colors.text,
    marginBottom: spacing[3],
  },
  heading2: {
    fontSize: typography.textLg,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    marginBottom: spacing[2],
  },
  heading3: {
    fontSize: typography.textBase,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    marginBottom: spacing[2],
  },
  paragraph: {
    marginVertical: spacing[1],
  },
  code_inline: {
    backgroundColor: colors.moodBg,
    paddingHorizontal: spacing[2],
    borderRadius: elevation.radiusSm,
    fontFamily: 'monospace',
  },
  code_block: {
    backgroundColor: colors.moodBg,
    padding: spacing[3],
    borderRadius: elevation.radiusMd,
    marginVertical: spacing[2],
  },
  fence: {
    backgroundColor: colors.moodBg,
    padding: spacing[3],
    borderRadius: elevation.radiusMd,
    marginVertical: spacing[2],
  },
  link: {
    color: colors.accent,
  },
  strong: {
    fontWeight: typography.fontBold,
  },
  em: {
    fontStyle: 'italic',
  },
  blockquote: {
    backgroundColor: colors.moodBg,
    borderLeftWidth: 4,
    borderLeftColor: colors.border,
    paddingLeft: spacing[3],
    paddingVertical: spacing[2],
    marginVertical: spacing[2],
  },
  list_item: {
    marginVertical: spacing[1],
  },
  bullet_list: {
    marginVertical: spacing[1],
  },
  ordered_list: {
    marginVertical: spacing[1],
  },
});

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
