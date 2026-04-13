/**
 * User Types Tests
 */

import { describe, it, expect } from '@jest/globals';
import type { UsageStats, Session } from './user';

describe('User types', () => {
  describe('UsageStats', () => {
    it('should accept valid usage stats', () => {
      const stats: UsageStats = {
        dialog_count: 10,
        message_count: 100,
        knowledge_base_count: 3,
        joined_at: '2024-01-01T00:00:00Z',
      };
      expect(stats.dialog_count).toBe(10);
    });
  });

  describe('Session', () => {
    it('should accept full session', () => {
      const session: Session = {
        id: 'session-1',
        device: 'iPhone 15',
        location: 'Beijing',
        ip_address: '192.168.1.1',
        last_active_at: '2024-01-01T00:00:00Z',
        is_current: true,
      };
      expect(session.is_current).toBe(true);
    });

    it('should accept minimal session', () => {
      const session: Session = {
        id: 'session-2',
        last_active_at: '2024-01-01T00:00:00Z',
        is_current: false,
      };
      expect(session.device).toBeUndefined();
    });
  });
});
