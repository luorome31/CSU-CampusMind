// mobile/src/components/home/HeroBanner.tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card } from '../ui/Card';
import { colors, typography, spacing } from '../../styles';

export function HeroBanner() {
  return (
    <Card style={styles.card}>
      <View style={styles.logoPlaceholder}>
        <Text style={styles.logoText}>CM</Text>
      </View>
      <Text style={styles.title}>CampusMind</Text>
      <Text style={styles.subtitle}>你的智能校园助手</Text>
      <View style={styles.features}>
        <Text style={styles.feature}>查询成绩和课表</Text>
        <Text style={styles.feature}>了解校园通知和活动</Text>
        <Text style={styles.feature}>获取选课和教务信息</Text>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing[4],
    marginTop: spacing[4],
    padding: spacing[4],
    backgroundColor: colors.backgroundCard,
    borderRadius: 16,
  },
  logoPlaceholder: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.accent,
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'center',
    marginBottom: spacing[3],
  },
  logoText: {
    fontSize: 24,
    fontWeight: '700',
    color: '#fff',
  },
  title: {
    fontSize: typography.text2xl,
    fontWeight: typography.fontBold,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing[1],
  },
  subtitle: {
    fontSize: typography.textBase,
    color: colors.textLight,
    textAlign: 'center',
    marginBottom: spacing[4],
  },
  features: {
    gap: spacing[1],
  },
  feature: {
    fontSize: typography.textSm,
    color: colors.textMuted,
    textAlign: 'center',
  },
});
