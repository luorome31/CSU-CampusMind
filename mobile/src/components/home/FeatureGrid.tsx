// mobile/src/components/home/FeatureGrid.tsx
import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';
import { MessageCircle, BookOpen, FilePlus, User } from 'lucide-react-native';
import { Card } from '../ui/Card';
import { colors, typography, spacing } from '../../styles';
import type { RootTabParamList } from '../../navigation/types';

type NavigationProp = BottomTabNavigationProp<RootTabParamList>;

type TabName = 'HomeTab' | 'ChatsTab' | 'KnowledgeTab' | 'ProfileTab';

const features: { label: string; icon: React.ComponentType<any>; tab: TabName }[] = [
  { label: '新建对话', icon: MessageCircle, tab: 'ChatsTab' },
  { label: '知识库', icon: BookOpen, tab: 'KnowledgeTab' },
  { label: '知识构建', icon: FilePlus, tab: 'HomeTab' },
  { label: '个人中心', icon: User, tab: 'ProfileTab' },
];

export function FeatureGrid() {
  const navigation = useNavigation<NavigationProp>();

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>快捷入口</Text>
      <View style={styles.grid}>
        {features.map(({ label, icon: Icon, tab }) => (
          <Pressable
            key={label}
            style={({ pressed }) => [styles.tile, pressed && styles.tilePressed]}
            onPress={() => navigation.navigate(tab as any)}
          >
            <Card style={styles.tileCard}>
              <Icon size={24} color={colors.accent} strokeWidth={2} />
              <Text style={styles.tileLabel}>{label}</Text>
            </Card>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: spacing[6],
    paddingHorizontal: spacing[4],
  },
  sectionTitle: {
    fontSize: typography.textLg,
    fontWeight: typography.fontMedium,
    color: colors.text,
    marginBottom: spacing[3],
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing[3],
  },
  tile: {
    width: '47%',
  },
  tilePressed: {
    opacity: 0.7,
  },
  tileCard: {
    padding: spacing[4],
    backgroundColor: colors.backgroundCard,
    borderRadius: 12,
    alignItems: 'center',
    gap: spacing[2],
  },
  tileLabel: {
    fontSize: typography.textSm,
    color: colors.text,
    fontWeight: typography.fontMedium,
  },
});
