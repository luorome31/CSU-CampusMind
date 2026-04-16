/**
 * Button Component
 * A customizable button component following the design system tokens
 */

import React from 'react';
import { Pressable, ActivityIndicator, StyleSheet, ViewStyle, TextStyle, View } from 'react-native';
import { Text } from '@/components/ui/StyledText';
import { colors, typography, spacing, elevation } from '../../../styles';

// === Types ===
export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps {
  /** Button variant style */
  variant?: ButtonVariant;
  /** Button size */
  size?: ButtonSize;
  /** Left icon component */
  leftIcon?: React.ComponentType<{ size: number }>;
  /** Right icon component */
  rightIcon?: React.ComponentType<{ size: number }>;
  /** Icon size (used for both left and right icons) */
  iconSize?: number;
  /** Loading state */
  isLoading?: boolean;
  /** Text to show when loading */
  loadingText?: string;
  /** Full width button */
  fullWidth?: boolean;
  /** Disabled state */
  disabled?: boolean;
  /** Button content */
  children: React.ReactNode;
  /** Click handler */
  onPress?: () => void;
  /** Additional style */
  style?: ViewStyle;
}

// === Variant Styles ===
const getVariantStyles = (
  variant: ButtonVariant,
  disabled: boolean
): { container: ViewStyle; text: TextStyle } => {
  const baseOpacity = disabled ? 0.5 : 1;

  switch (variant) {
    case 'primary':
      return {
        container: {
          backgroundColor: colors.accent,
          opacity: baseOpacity,
        },
        text: {
          color: '#FFFFFF',
        },
      };
    case 'secondary':
      return {
        container: {
          backgroundColor: colors.backgroundCard,
          borderWidth: 1,
          borderColor: colors.border,
          opacity: baseOpacity,
        },
        text: {
          color: colors.accent,
        },
      };
    case 'ghost':
      return {
        container: {
          backgroundColor: 'transparent',
          opacity: baseOpacity,
        },
        text: {
          color: colors.accent,
        },
      };
    case 'danger':
      return {
        container: {
          backgroundColor: colors.danger,
          opacity: baseOpacity,
        },
        text: {
          color: '#FFFFFF',
        },
      };
    default:
      return {
        container: {
          backgroundColor: colors.accent,
          opacity: baseOpacity,
        },
        text: {
          color: '#FFFFFF',
        },
      };
  }
};

// === Size Styles ===
const getSizeStyles = (
  size: ButtonSize
): { container: ViewStyle; text: TextStyle; iconSize: number } => {
  switch (size) {
    case 'sm':
      return {
        container: {
          height: spacing.buttonHeightSm,
          paddingHorizontal: spacing[3],
        },
        text: {
          fontSize: typography.textSm,
        },
        iconSize: 16,
      };
    case 'lg':
      return {
        container: {
          height: spacing.buttonHeightLg,
          paddingHorizontal: spacing[6],
        },
        text: {
          fontSize: typography.textLg,
        },
        iconSize: 24,
      };
    case 'md':
    default:
      return {
        container: {
          height: spacing.buttonHeightMd,
          paddingHorizontal: spacing[4],
        },
        text: {
          fontSize: typography.textBase,
        },
        iconSize: 20,
      };
  }
};

/**
 * Button Component
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  leftIcon: LeftIcon,
  rightIcon: RightIcon,
  iconSize,
  isLoading = false,
  loadingText,
  fullWidth = false,
  disabled = false,
  children,
  onPress,
  style,
}) => {
  const variantStyles = getVariantStyles(variant, disabled || isLoading);
  const sizeStyles = getSizeStyles(size);
  const resolvedIconSize = iconSize ?? sizeStyles.iconSize;

  const containerStyle: ViewStyle = {
    ...styles.container,
    ...variantStyles.container,
    ...sizeStyles.container,
    ...(fullWidth && { width: '100%' }),
    ...style,
  };

  const textStyle: TextStyle = {
    ...styles.text,
    ...variantStyles.text,
    ...sizeStyles.text,
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <View style={styles.loadingContainer}>
          <ActivityIndicator
            size="small"
            color={variantStyles.text.color}
          />
          {loadingText && (
            <Text style={[textStyle, styles.loadingText]}>{loadingText}</Text>
          )}
        </View>
      );
    }

    return (
      <View style={styles.contentContainer}>
        {LeftIcon && (
          <View style={styles.iconLeft}>
            <LeftIcon size={resolvedIconSize} />
          </View>
        )}
        <Text style={textStyle}>{children}</Text>
        {RightIcon && (
          <View style={styles.iconRight}>
            <RightIcon size={resolvedIconSize} />
          </View>
        )}
      </View>
    );
  };

  return (
    <Pressable
      style={({ pressed }) => [
        containerStyle,
        pressed && !disabled && !isLoading && styles.pressed,
      ]}
      disabled={disabled || isLoading}
      onPress={onPress}
      accessibilityRole="button"
      accessibilityState={{ disabled: disabled || isLoading }}
    >
      {renderContent()}
    </Pressable>
  );
};

// === Styles ===
const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: elevation.radiusMd,
    ...elevation.shadowCard,
    minWidth: spacing.hitTargetMin,
    minHeight: spacing.hitTargetMin,
  },
  contentContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    fontFamily: typography.fontSans,
    fontWeight: typography.fontMedium,
    textAlign: 'center',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    marginLeft: spacing[2],
  },
  iconLeft: {
    marginRight: spacing[2],
  },
  iconRight: {
    marginLeft: spacing[2],
  },
  pressed: {
    opacity: 0.8,
  },
});

export default Button;
