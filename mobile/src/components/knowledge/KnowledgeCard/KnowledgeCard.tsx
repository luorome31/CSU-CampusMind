import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Card } from '../../ui';
import { Badge } from '../../ui/Badge';
import { colors, typography, spacing, elevation } from '../../../styles';

export interface KnowledgeCardProps {
  knowledge: {
    id: string;
    name: string;
    description?: string;
  };
  fileCount: number;
  onClick: () => void;
}

export const KnowledgeCard: React.FC<KnowledgeCardProps> = ({
  knowledge,
  fileCount,
  onClick,
}) => {
  return (
    <Pressable
      onPress={onClick}
      accessibilityRole="button"
      accessibilityLabel={`知识库: ${knowledge.name}, ${fileCount} 个文件`}
    >
      <Card variant="elevated" padding="md" style={styles.card}>
        <View style={styles.header}>
          <Text style={styles.title} numberOfLines={1}>
            {knowledge.name}
          </Text>
          <Badge variant="info" style={styles.badge}>
            {fileCount} 个文件
          </Badge>
        </View>
        {knowledge.description && (
          <Text style={styles.description} numberOfLines={2}>
            {knowledge.description}
          </Text>
        )}
      </Card>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  card: {
    marginBottom: spacing[3],
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing[2],
  },
  title: {
    flex: 1,
    fontSize: typography.textLg,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    marginRight: spacing[2],
  },
  badge: {
    marginLeft: spacing[2],
  },
  description: {
    fontSize: typography.textSm,
    color: colors.textLight,
    lineHeight: typography.textSm * 1.5,
  },
});

export default KnowledgeCard;