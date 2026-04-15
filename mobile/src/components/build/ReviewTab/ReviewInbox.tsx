// mobile/src/components/build/ReviewTab/ReviewInbox.tsx
import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { Clipboard } from 'lucide-react-native';
import { colors, typography, spacing, elevation } from '../../../styles';

interface ReviewInboxProps {
  count: number;
  onPress: () => void;
}

export function ReviewInbox({ count, onPress }: ReviewInboxProps) {
  const isDisabled = count === 0;

  return (
    <Pressable
      style={[styles.container, isDisabled && styles.containerDisabled]}
      onPress={onPress}
      disabled={isDisabled}
    >
      <View style={styles.content}>
        <Clipboard size={18} color={isDisabled ? colors.textMuted : colors.accent} />
        <Text style={[styles.label, isDisabled && styles.labelDisabled]}>待审核文件</Text>
      </View>
      {count > 0 && (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{count}</Text>
        </View>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusMd,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    minHeight: 48,
  },
  containerDisabled: {
    opacity: 0.5,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[2],
  },
  label: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
  },
  labelDisabled: {
    color: colors.textMuted,
  },
  badge: {
    backgroundColor: colors.accent,
    borderRadius: elevation.radiusFull,
    minWidth: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing[2],
  },
  badgeText: {
    fontSize: typography.textXs,
    fontWeight: typography.fontSemibold,
    color: colors.background,
  },
});
