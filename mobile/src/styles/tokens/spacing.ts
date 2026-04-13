/**
 * Design Tokens: Spacing System
 * 4px 基准间距系统
 */

export const spacing = {
  // === Core Spacing Scale ===
  0: 0,
  1: 4,    // 0.25rem
  2: 8,    // 0.5rem
  3: 12,   // 0.75rem
  4: 16,   // 1rem
  5: 20,   // 1.25rem
  6: 24,   // 1.5rem
  8: 32,   // 2rem
  10: 40,  // 2.5rem
  12: 48,  // 3rem
  16: 64,  // 4rem
  20: 80,  // 5rem
  24: 96,  // 6rem

  // === Component-Specific ===
  hitTargetMin: 44,      // WCAG touch target
  inputHeight: 44,        // 2.75rem
  buttonHeightSm: 36,     // 2.25rem
  buttonHeightMd: 44,     // 2.75rem
  buttonHeightLg: 48,     // 3rem

  // === Layout ===
  containerMax: '90vw',
  containerMaxSm: 440,
  containerMaxMd: 720,
  containerMaxLg: 1024,
  containerMaxXl: 1280,
} as const;

// 语义化别名
export const layout = {
  screenPadding: spacing[4],
  cardPadding: spacing[4],
  sectionGap: spacing[8],
  itemGap: spacing[2],
} as const;
