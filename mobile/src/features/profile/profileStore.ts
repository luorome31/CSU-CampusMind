/**
 * ProfileStore - 用户信息状态管理
 */
import { create } from 'zustand';
import { profileApi, type UpdateProfileData } from './api/profile';
import type { User, UsageStats, Session } from '../../types/user';
import { ApiError } from '../../types/api';

interface ProfileState {
  user: User | null;
  stats: UsageStats | null;
  sessions: Session[];
  isLoading: boolean;
  error: string | null;
}

interface ProfileActions {
  loadProfile: () => Promise<void>;
  updateProfile: (data: UpdateProfileData) => Promise<void>;
  loadStats: () => Promise<void>;
  loadSessions: () => Promise<void>;
  clearError: () => void;
}

type ProfileStore = ProfileState & ProfileActions;

export const useProfileStore = create<ProfileStore>((set) => ({
  user: null,
  stats: null,
  sessions: [],
  isLoading: false,
  error: null,

  loadProfile: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await profileApi.getProfile();
      set({ user: response.data, isLoading: false });
    } catch (err) {
      const apiError = err as ApiError;
      set({ error: apiError.detail || apiError.message, isLoading: false });
    }
  },

  updateProfile: async (data: UpdateProfileData) => {
    set({ isLoading: true, error: null });
    try {
      const response = await profileApi.updateProfile(data);
      set({ user: response.data, isLoading: false });
    } catch (err) {
      const apiError = err as ApiError;
      set({ error: apiError.detail || apiError.message, isLoading: false });
    }
  },

  loadStats: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await profileApi.getStats();
      set({ stats: response.data, isLoading: false });
    } catch (err) {
      const apiError = err as ApiError;
      set({ error: apiError.detail || apiError.message, isLoading: false });
    }
  },

  loadSessions: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await profileApi.getSessions();
      set({ sessions: response.data, isLoading: false });
    } catch (err) {
      const apiError = err as ApiError;
      set({ error: apiError.detail || apiError.message, isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));