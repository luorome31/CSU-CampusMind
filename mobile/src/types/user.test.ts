/**
 * User Types Tests
 */

import { describe, it, expect } from '@jest/globals';
import type { UsageStats, Session } from './user';

describe('User types', () => {
  describe('UsageStats', () => {
    it('should accept valid usage stats', () => {
      const stats: UsageStats = {
        conversation_count: 10,
        message_count: 100,
        knowledge_base_count: 3,
        join_date: '2024-01-01T00:00:00Z',
      };
      expect(stats.conversation_count).toBe(10);
    });
  });

  describe('Session', () => {
    it('should accept full session', () => {
      const session: Session = {
        session_id: 'session-1',
        device: 'iPhone 15',
        location: 'Beijing',
        created_at: 1704067200,
        is_current: true,
      };
      expect(session.is_current).toBe(true);
    });
  });
});
