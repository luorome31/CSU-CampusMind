/**
 * Input Component
 * A customizable input component following the design system tokens
 */

import React from 'react';
import { View, StyleSheet, TextInputProps, ViewStyle, TextStyle } from 'react-native';
import { Text, TextInput } from '@/components/ui/StyledText';
import { colors, typography, spacing, elevation } from '../../../styles';

// === Types ===
export type InputSize = 'sm' | 'md' | 'lg';

export interface InputProps extends Omit<TextInputProps, 'style'> {
  /** Label text displayed above the input */
  label?: string;
  /** Error message displayed below the input */
  error?: string;
  /** Hint text displayed below the input */
  hint?: string;
  /** Input size variant */
  size?: InputSize;
  /** Left icon component */
  leftIcon?: React.ComponentType<{ size: number }>;
  /** Right icon component */
  rightIcon?: React.ComponentType<{ size: number }>;
  /** Full width input */
  fullWidth?: boolean;
  /** Additional container style */
  style?: ViewStyle;
}

// === Size Styles ===
const getSizeStyles = (
  size: InputSize
): { container: ViewStyle; input: TextStyle; iconSize: number } => {
  switch (size) {
    case 'sm':
      return {
        container: {
          height: spacing.buttonHeightSm, // 36px
        },
        input: {
          height: spacing.buttonHeightSm,
          fontSize: typography.textSm,
        },
        iconSize: 16,
      };
    case 'lg':
      return {
        container: {
          height: spacing.buttonHeightLg, // 48px
        },
        input: {
          height: spacing.buttonHeightLg,
          fontSize: typography.textLg,
        },
        iconSize: 24,
      };
    case 'md':
    default:
      return {
        container: {
          height: spacing.inputHeight, // 44px
        },
        input: {
          height: spacing.inputHeight,
          fontSize: typography.textBase,
        },
        iconSize: 20,
      };
  }
};

/**
 * Input Component
 */
export const Input: React.FC<InputProps> = ({
  label,
  error,
  hint,
  size = 'md',
  leftIcon: LeftIcon,
  rightIcon: RightIcon,
  fullWidth = true,
  style,
  ...textInputProps
}) => {
  const sizeStyles = getSizeStyles(size);
  const hasError = !!error;

  const containerStyle: ViewStyle = {
    ...styles.container,
    ...(fullWidth && { width: '100%' }),
    ...style,
  };

  const inputContainerStyle: ViewStyle = {
    ...styles.inputContainer,
    ...sizeStyles.container,
    borderColor: hasError ? colors.coral : colors.border,
  };

  const inputTextStyle: TextStyle = {
    ...styles.inputText,
    ...sizeStyles.input,
  };

  return (
    <View style={containerStyle}>
      {label && <Text style={styles.label}>{label}</Text>}
      <View style={inputContainerStyle}>
        {LeftIcon && (
          <View style={styles.iconLeft}>
            <LeftIcon size={sizeStyles.iconSize} />
          </View>
        )}
        <TextInput
          style={[inputTextStyle, LeftIcon && styles.inputWithLeftIcon, RightIcon && styles.inputWithRightIcon]}
          placeholderTextColor={colors.textMuted}
          {...textInputProps}
        />
        {RightIcon && (
          <View style={styles.iconRight}>
            <RightIcon size={sizeStyles.iconSize} />
          </View>
        )}
      </View>
      {error && <Text style={styles.errorText}>{error}</Text>}
      {hint && !error && <Text style={styles.hintText}>{hint}</Text>}
    </View>
  );
};

// === Styles ===
const styles = StyleSheet.create({
  container: {
    marginBottom: spacing[3],
  },
  label: {
    fontFamily: typography.fontSans,
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.textLight,
    marginBottom: spacing[1],
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: elevation.radiusMd,
    borderWidth: 1,
    paddingHorizontal: spacing[3],
  },
  inputText: {
    flex: 1,
    fontFamily: typography.fontSans,
    color: colors.text,
    paddingVertical: 0,
  },
  inputWithLeftIcon: {
    paddingLeft: spacing[1],
  },
  inputWithRightIcon: {
    paddingRight: spacing[1],
  },
  iconLeft: {
    marginRight: spacing[2],
  },
  iconRight: {
    marginLeft: spacing[2],
  },
  errorText: {
    fontFamily: typography.fontSans,
    fontSize: typography.textXs,
    color: colors.coral,
    marginTop: spacing[1],
  },
  hintText: {
    fontFamily: typography.fontSans,
    fontSize: typography.textXs,
    color: colors.textMuted,
    marginTop: spacing[1],
  },
});

export default Input;
