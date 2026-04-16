import React from 'react';
import { View, Pressable, StyleSheet } from 'react-native';
import { Text } from '@/components/ui/StyledText';
import { colors, typography, spacing, elevation } from '../../styles';

interface Option {
  value: string;
  label: string;
}

interface SegmentedControlProps {
  options: Option[];
  value: string;
  onChange: (value: string) => void;
}

export function SegmentedControl({ options, value, onChange }: SegmentedControlProps) {
  return (
    <View style={styles.container}>
      {options.map((option) => {
        const isSelected = option.value === value;
        return (
          <Pressable
            key={option.value}
            style={[styles.tab, isSelected && styles.tabSelected]}
            onPress={() => onChange(option.value)}
          >
            <Text style={[styles.tabText, isSelected && styles.tabTextSelected]}>
              {option.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: colors.accentLight,
    borderRadius: elevation.radiusLg,
    padding: 2,
  },
  tab: {
    flex: 1,
    paddingVertical: spacing[2],
    paddingHorizontal: spacing[3],
    borderRadius: elevation.radiusMd,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabSelected: {
    backgroundColor: colors.backgroundCard,
    ...elevation.shadowCard,
  },
  tabText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.textMuted,
  },
  tabTextSelected: {
    color: colors.text,
    fontWeight: typography.fontSemibold,
  },
});
