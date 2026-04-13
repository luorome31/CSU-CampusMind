/**
 * Design Tokens: Elevation & Motion
 * 阴影、圆角、过渡动画系统
 */

import { ViewStyle } from 'react-native';

export const elevation = {
  // === Z-Index Scale ===
  zBase: 0,
  zDropdown: 10,
  zSticky: 20,
  zOverlay: 30,
  zModal: 40,
  zToast: 50,

  // === Border Radius ===
  radiusSm: 6,
  radiusMd: 10,
  radiusLg: 16,
  radiusXl: 18,
  radius2xl: 18,
  radiusFull: 9999,

  // === Shadows ===
  shadowCard: {
    shadowColor: '#3B3D3F',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 3,
    elevation: 2,
  } as ViewStyle,
  shadowCardHover: {
    shadowColor: '#3B3D3F',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 18,
    elevation: 8,
  } as ViewStyle,
  shadowElevated: {
    shadowColor: '#3B3D3F',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.15,
    shadowRadius: 28,
    elevation: 12,
  } as ViewStyle,
} as const;

export const transitions = {
  // === Duration ===
  durationFast: 150,
  durationNormal: 200,
  durationSlow: 300,

  // === Easing ===
  easeDefault: 'cubic-bezier(0.16, 1, 0.3, 1)',
  easeSoft: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
  easeBounce: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
} as const;
