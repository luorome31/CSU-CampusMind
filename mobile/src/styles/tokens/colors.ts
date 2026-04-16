/**
 * Design Tokens: Color System
 * Theme: Warm Paper Blue-Grey Accent
 * 延续 Web 端暖纸主题配色
 */

export const colors = {
  // === Background System ===
  background: '#F8F5ED',
  backgroundCard: '#FCFAF5',
  backgroundGlass: 'rgba(250, 248, 242, 0.92)',

  // === Accent System (Blue-Grey, desaturated) ===
  accent: '#537D96',
  accentHover: '#456A80',
  accentLight: 'rgba(83, 125, 150, 0.08)',

  // === Text System ===
  text: '#3B3D3F',
  textLight: '#6B6F73',
  textMuted: '#8E9196',

  // === Border & Shadow ===
  border: 'rgba(83, 125, 150, 0.22)',
  shadow: 'rgba(59, 61, 63, 0.09)',

  // === Status Colors ===
  green: '#7BAE7F',
  coral: '#EC8F8D',
  danger: '#8B3A3A',

  // === Chat Specific ===
  assistantText: '#36332eff',
  moodBg: 'rgba(83, 125, 150, 0.05)',
  moodText: '#537D96',
  moodBorder: 'rgba(83, 125, 150, 0.16)',
  toolBg: 'rgba(83, 125, 150, 0.06)',
  toolText: '#6B6F73',
  userBg: 'rgba(83, 125, 150, 0.08)',

  // === Semantic Aliases ===
  success: '#4a8c5e',
  successBg: 'rgba(74, 140, 94, 0.12)',
  error: '#b85c5c',
  errorBg: 'rgba(184, 92, 92, 0.12)',
  warning: '#c4935a',
  warningBg: 'rgba(196, 147, 90, 0.12)',
  info: '#6b8fa3',

  // === Legacy Aliases ===
  bgPrimary: '#F8F5ED',
  bgSecondary: '#FCFAF5',
  bgTertiary: '#E8E5DD',
  textPrimary: '#3B3D3F',
  textSecondary: '#6B6F73',
  textTertiary: '#8E9196',
} as const;

export type ColorKey = keyof typeof colors;
