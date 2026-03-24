import { create } from 'zustand';
import { profileApi } from './api/profile';
import { User, UsageStats, Session } from './types';

interface ProfileState {
  user: User | null;
  stats: UsageStats | null;
  sessions: Session[];
  isLoading: boolean;
  error: string | null;
}

interface ProfileActions {
  loadProfile: () => Promise<void>;
  updateProfile: (data: { display_name?: string; email?: string; phone?: string }) => Promise<void>;
  loadStats: () => Promise<void>;
  loadSessions: () => Promise<void>;
  revokeSession: (sessionId: string) => Promise<void>;
  clearError: () => void;
}

type ProfileStore = ProfileState & ProfileActions;

export const profileStore = create<ProfileStore>((set) => ({
  user: null,
  stats: null,
  sessions: [],
  isLoading: false,
  error: null,

  loadProfile: async () => {
    set({ isLoading: true, error: null });
    try {
      const user = await profileApi.getProfile();
      set({ user, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  updateProfile: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const user = await profileApi.updateProfile(data);
      set({ user, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  loadStats: async () => {
    set({ isLoading: true, error: null });
    try {
      const stats = await profileApi.getStats();
      set({ stats, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  loadSessions: async () => {
    set({ isLoading: true, error: null });
    try {
      const sessions = await profileApi.getSessions();
      set({ sessions, isLoading: false });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  revokeSession: async (sessionId: string) => {
    try {
      await profileApi.revokeSession(sessionId);
      set((state) => ({
        sessions: state.sessions.filter((s) => s.session_id !== sessionId),
      }));
    } catch (err) {
      set({ error: (err as Error).message });
    }
  },

  clearError: () => set({ error: null }),
}));
