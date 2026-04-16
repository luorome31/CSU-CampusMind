/**
 * Design Tokens: Typography System
 * RN 端字体排版系统
 */

import { Platform, TextStyle } from 'react-native';

const fontFamily = Platform.select({
  ios: 'LXGWWenKaiScreen',
  android: 'LXGWWenKaiScreen',
  default: 'LXGWWenKaiScreen',
});

export const typography = {
  // === Font Families ===
  fontSans: fontFamily,
  fontMono: Platform.select({
    ios: 'Menlo',
    android: 'monospace',
    default: 'monospace',
  }),

  // === Type Scale ===
  textXs: 12,
  textSm: 14,
  textBase: 16,
  textLg: 18,
  textXl: 20,
  text2xl: 24,
  text3xl: 30,
  text4xl: 36,
  text5xl: 48,

  // === Line Heights ===
  leadingNone: 1,
  leadingTight: 1.25,
  leadingSnug: 1.375,
  leadingNormal: 1.5,
  leadingRelaxed: 1.625,

  // === Font Weights ===
  fontNormal: '400' as TextStyle['fontWeight'],
  fontMedium: '500' as TextStyle['fontWeight'],
  fontSemibold: '600' as TextStyle['fontWeight'],
  fontBold: '700' as TextStyle['fontWeight'],

  // === Letter Spacing ===
  trackingTighter: -0.025,
  trackingTight: -0.015,
  trackingNormal: 0,
  trackingWide: 0.025,
  trackingWider: 0.05,
  trackingWidest: 0.1,
  trackingLabel: 0.16,
} as const;

export type Typography = typeof typography;

// 常用文本样式预设
export const textStyles = {
  display: {
    fontFamily: typography.fontSans,
    fontWeight: typography.fontSemibold,
    lineHeight: typography.text4xl * typography.leadingTight,
  } as TextStyle,
  body: {
    fontFamily: typography.fontSans,
    fontWeight: typography.fontNormal,
    lineHeight: typography.textBase * typography.leadingNormal,
  } as TextStyle,
  label: {
    fontFamily: typography.fontSans,
    fontWeight: typography.fontMedium,
    fontSize: typography.textXs,
    letterSpacing: typography.trackingLabel,
    textTransform: 'uppercase',
  } as TextStyle,
} as const;
