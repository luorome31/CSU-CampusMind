/**
 * StyledText - Global font wrappers for Text and TextInput.
 *
 * Use these instead of the react-native originals to ensure
 * the custom font (LXGWWenKaiScreen) is applied everywhere.
 *
 * Usage:
 *   import { Text, TextInput } from '@/components/ui/StyledText';
 */

import React from 'react';
import {
  Text as RNText,
  TextInput as RNTextInput,
  TextProps,
  TextInputProps,
  StyleSheet,
} from 'react-native';

const FONT_FAMILY = 'LXGWWenKaiScreen';

const styles = StyleSheet.create({
  defaultFont: { fontFamily: FONT_FAMILY },
});

/**
 * Drop-in replacement for RN Text with the custom font baked in.
 * Any explicit fontFamily in your own style prop will override this default.
 */
export const Text = React.forwardRef<RNText, TextProps>((props, ref) => (
  <RNText ref={ref} {...props} style={[styles.defaultFont, props.style]} />
));
Text.displayName = 'Text';

/**
 * Drop-in replacement for RN TextInput with the custom font baked in.
 */
export const TextInput = React.forwardRef<RNTextInput, TextInputProps>((props, ref) => (
  <RNTextInput ref={ref} {...props} style={[styles.defaultFont, props.style]} />
));
TextInput.displayName = 'TextInput';
