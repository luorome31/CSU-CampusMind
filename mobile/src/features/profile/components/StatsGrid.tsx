// mobile/src/features/profile/components/StatsGrid.tsx
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text } from '@/components/ui/StyledText';
import { MessageSquare, MessageCircle, BookOpen, Calendar } from 'lucide-react-native';
import { Card } from '../../../components/ui/Card';
import { colors, typography, spacing, elevation } from '../../../styles';
import { useProfileStore } from '../profileStore';

export function StatsGrid() {
  const { stats, user } = useProfileStore();

  const joinDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
      })
    : '-';

  const items = [
    {
      icon: MessageSquare,
      label: '对话数',
      value: stats?.conversation_count ?? '-',
    },
    {
      icon: MessageCircle,
      label: '消息数',
      value: stats?.message_count ?? '-',
    },
    {
      icon: BookOpen,
      label: '知识库数',
      value: stats?.knowledge_base_count ?? '-',
    },
    {
      icon: Calendar,
      label: '注册时间',
      value: stats?.join_date || joinDate,
    },
  ];

  return (
    <Card variant="elevated" padding="md" style={styles.card}>
      <Text style={styles.title}>使用统计</Text>
      <View style={styles.grid}>
        {items.map((item) => (
          <View key={item.label} style={styles.statCard}>
            <item.icon size={24} color={colors.accent} style={styles.icon} />
            <Text style={styles.value}>{item.value}</Text>
            <Text style={styles.label}>{item.label}</Text>
          </View>
        ))}
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing[4],
    marginTop: spacing[4],
  },
  title: {
    fontSize: typography.textLg,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    marginBottom: spacing[4],
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing[3],
  },
  statCard: {
    width: '47%',
    backgroundColor: colors.background,
    borderRadius: elevation.radiusMd,
    padding: spacing[3],
    alignItems: 'center',
  },
  icon: {
    marginBottom: spacing[2],
  },
  value: {
    fontSize: typography.textLg,
    fontWeight: typography.fontBold,
    color: colors.text,
    marginBottom: spacing[1],
  },
  label: {
    fontSize: typography.textSm,
    color: colors.textLight,
  },
});

export default StatsGrid;
