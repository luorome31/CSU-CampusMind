/**
 * Logger - Centralized logging utility with environment-based control.
 *
 * Usage:
 *   import { logger } from '@/utils/logger';
 *   logger.debug('ChatAPI', 'New dialog ID:', id);
 *   logger.warn('Network', 'Connection lost');
 *   logger.error('Auth', 'Login failed:', err);
 *
 * Control via .env:
 *   EXPO_PUBLIC_DEBUG_MODE=true   → enables debug/info/log output
 *   EXPO_PUBLIC_DEBUG_MODE=false  → only warn/error are printed (default)
 */

const isDebugEnabled =
  process.env.EXPO_PUBLIC_DEBUG_MODE === 'true' ||
  process.env.EXPO_PUBLIC_DEBUG_MODE === '1';

function formatTag(tag: string): string {
  return `[${tag}]`;
}

/**
 * Centralized logger that respects EXPO_PUBLIC_DEBUG_MODE.
 *
 * - `debug` / `info` / `log` are silenced when debug mode is off.
 * - `warn` / `error` are always printed regardless of the setting.
 */
export const logger = {
  /** Verbose debug output – only in debug mode */
  debug(tag: string, ...args: unknown[]): void {
    if (isDebugEnabled) {
      console.log(formatTag(tag), ...args);
    }
  },

  /** Informational messages – only in debug mode */
  info(tag: string, ...args: unknown[]): void {
    if (isDebugEnabled) {
      console.info(formatTag(tag), ...args);
    }
  },

  /** General log – only in debug mode */
  log(tag: string, ...args: unknown[]): void {
    if (isDebugEnabled) {
      console.log(formatTag(tag), ...args);
    }
  },

  /** Warnings – always printed */
  warn(tag: string, ...args: unknown[]): void {
    console.warn(formatTag(tag), ...args);
  },

  /** Errors – always printed */
  error(tag: string, ...args: unknown[]): void {
    console.error(formatTag(tag), ...args);
  },
};
