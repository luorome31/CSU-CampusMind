/**
 * 安全存储封装
 * 替换不支持 Expo Go 的 react-native-keychain 为 expo-secure-store
 */

import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

export const storage = {
  async setToken(token: string): Promise<void> {
    if (Platform.OS === 'web') {
      try { localStorage.setItem('token', token); } catch {}
      return;
    }
    await SecureStore.setItemAsync('token', token);
  },

  async getToken(): Promise<string | null> {
    if (Platform.OS === 'web') {
      try { return localStorage.getItem('token'); } catch { return null; }
    }
    try {
      return await SecureStore.getItemAsync('token');
    } catch {
      return null;
    }
  },

  async removeToken(): Promise<void> {
    if (Platform.OS === 'web') {
      try { localStorage.removeItem('token'); } catch {}
      return;
    }
    await SecureStore.deleteItemAsync('token');
  },

  async setSessionId(sessionId: string): Promise<void> {
    if (Platform.OS === 'web') {
      try { localStorage.setItem('sessionId', sessionId); } catch {}
      return;
    }
    await SecureStore.setItemAsync('sessionId', sessionId);
  },

  async getSessionId(): Promise<string | null> {
    if (Platform.OS === 'web') {
      try { return localStorage.getItem('sessionId'); } catch { return null; }
    }
    try {
      return await SecureStore.getItemAsync('sessionId');
    } catch {
      return null;
    }
  },

  async removeSessionId(): Promise<void> {
    if (Platform.OS === 'web') {
      try { localStorage.removeItem('sessionId'); } catch {}
      return;
    }
    await SecureStore.deleteItemAsync('sessionId');
  },

  async clear(): Promise<void> {
    await this.removeToken();
    await this.removeSessionId();
  },
};