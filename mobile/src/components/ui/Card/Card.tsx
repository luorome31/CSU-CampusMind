/**
 * Card Component
 * A customizable card component following the design system tokens
 */

import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { colors, spacing, elevation } from '../../../styles';

// === Types ===
export type CardVariant = 'default' | 'elevated' | 'glass';
export type CardPadding = 'sm' | 'md' | 'lg';

export interface CardProps {
  /** Card variant style */
  variant?: CardVariant;
  /** Card padding size */
  padding?: CardPadding;
  /** Card content */
  children: React.ReactNode;
  /** Additional style */
  style?: ViewStyle;
}

// === Variant Styles ===
const getVariantStyles = (variant: CardVariant): ViewStyle => {
  switch (variant) {
    case 'elevated':
      return {
        backgroundColor: colors.backgroundCard,
        ...elevation.shadowElevated,
        borderRadius: elevation.radiusLg,
      };
    case 'glass':
      return {
        backgroundColor: colors.backgroundGlass,
        borderRadius: elevation.radiusXl,
        borderWidth: 1,
        borderColor: colors.border,
      };
    case 'default':
    default:
      return {
        backgroundColor: colors.backgroundCard,
        borderRadius: elevation.radiusLg,
        borderWidth: 1,
        borderColor: colors.border,
      };
  }
};

// === Padding Styles ===
const getPaddingStyles = (padding: CardPadding): ViewStyle => {
  switch (padding) {
    case 'sm':
      return {
        padding: spacing[2], // 8px
      };
    case 'lg':
      return {
        padding: spacing[6], // 24px
      };
    case 'md':
    default:
      return {
        padding: spacing[4], // 16px
      };
  }
};

/**
 * Card Component
 */
export const Card: React.FC<CardProps> = ({
  variant = 'default',
  padding = 'md',
  children,
  style,
}) => {
  const variantStyles = getVariantStyles(variant);
  const paddingStyles = getPaddingStyles(padding);

  const containerStyle: ViewStyle = {
    ...styles.container,
    ...variantStyles,
    ...paddingStyles,
    ...style,
  };

  return <View style={containerStyle}>{children}</View>;
};

// === Styles ===
const styles = StyleSheet.create({
  container: {
    overflow: 'hidden',
  },
});

export default Card;
