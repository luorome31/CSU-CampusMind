/**
 * EmptyState Component
 *
 * Empty state shown when there are no messages.
 * Shows CampusMind branding and system introduction.
 */

import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import { colors } from '../../../styles/tokens/colors';
import { typography } from '../../../styles/tokens/typography';
import { spacing } from '../../../styles/tokens/spacing';

// Assistant avatar
const ASSISTANT_AVATAR = require('../../../assets/csu-xiaotuanzi-answer.png');

// Feature list items
const FEATURES = [
  '查询成绩和课表',
  '了解校园通知和活动',
  '获取选课和教务信息',
];

/**
 * EmptyState - Renders the empty state screen for chat
 *
 * Displays assistant branding, title, subtitle, and feature list
 * when there are no messages in the conversation.
 */
export const EmptyState: React.FC = () => {
  return (
    <View style={styles.container}>
      <View style={styles.logoContainer}>
        <Image
          source={ASSISTANT_AVATAR}
          style={styles.avatar}
          resizeMode="cover"
          testID="empty-state-avatar"
        />
      </View>
      <Text style={styles.title} testID="empty-state-title">
        CampusMind
      </Text>
      <Text style={styles.subtitle} testID="empty-state-subtitle">
        你的智能校园助手
      </Text>
      <View style={styles.featuresContainer}>
        {FEATURES.map((feature, index) => (
          <View key={index} style={styles.featureItem}>
            <Text style={styles.featureBullet}>•</Text>
            <Text style={styles.featureText}>{feature}</Text>
          </View>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing[8],
  },
  logoContainer: {
    marginBottom: spacing[6],
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
  },
  title: {
    fontFamily: typography.fontSans,
    fontSize: typography.text3xl,
    fontWeight: typography.fontBold,
    color: colors.text,
    marginBottom: spacing[2],
  },
  subtitle: {
    fontFamily: typography.fontSans,
    fontSize: typography.textLg,
    fontWeight: typography.fontNormal,
    color: colors.textSecondary,
    marginBottom: spacing[10],
  },
  featuresContainer: {
    alignItems: 'flex-start',
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: spacing[1],
  },
  featureBullet: {
    fontFamily: typography.fontSans,
    fontSize: typography.textBase,
    color: colors.accent,
    marginRight: spacing[2],
  },
  featureText: {
    fontFamily: typography.fontSans,
    fontSize: typography.textBase,
    color: colors.textLight,
  },
});

export default EmptyState;
