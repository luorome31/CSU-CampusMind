/**
 * Badge Component
 * A pill-shaped badge component with variant-based styling
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { colors, typography, elevation } from '../../../styles';

// === Types ===
export type BadgeVariant = 'success' | 'error' | 'warning' | 'info';

export interface BadgeProps {
  /** Badge variant style */
  variant?: BadgeVariant;
  /** Badge content */
  children: React.ReactNode;
  /** Additional style */
  style?: ViewStyle;
}

// === Variant Styles ===
const getVariantStyles = (
  variant: BadgeVariant
): { container: ViewStyle; text: TextStyle } => {
  switch (variant) {
    case 'success':
      return {
        container: {
          backgroundColor: colors.successBg,
        },
        text: {
          color: colors.success,
        },
      };
    case 'error':
      return {
        container: {
          backgroundColor: colors.errorBg,
        },
        text: {
          color: colors.error,
        },
      };
    case 'warning':
      return {
        container: {
          backgroundColor: colors.warningBg,
        },
        text: {
          color: colors.warning,
        },
      };
    case 'info':
    default:
      return {
        container: {
          backgroundColor: colors.accentLight,
        },
        text: {
          color: colors.accent,
        },
      };
  }
};

/**
 * Badge Component
 */
export const Badge: React.FC<BadgeProps> = ({
  variant = 'info',
  children,
  style,
}) => {
  const variantStyles = getVariantStyles(variant);

  const containerStyle: ViewStyle = {
    ...styles.container,
    ...variantStyles.container,
    ...style,
  };

  const textStyle: TextStyle = {
    ...styles.text,
    ...variantStyles.text,
  };

  return (
    <View style={containerStyle} accessibilityRole="text">
      <Text style={textStyle}>{children}</Text>
    </View>
  );
};

// === Styles ===
const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: elevation.radiusFull,
    alignSelf: 'flex-start',
  },
  text: {
    fontFamily: typography.fontSans,
    fontSize: typography.textXs,
    fontWeight: typography.fontMedium,
  },
});

export default Badge;
