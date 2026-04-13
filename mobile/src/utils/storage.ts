/**
 * 安全存储封装
 * 使用 react-native-keychain 替代 sessionStorage
 */

import * as Keychain from 'react-native-keychain';

const SERVICE_NAME = 'CampusMind';

export const storage = {
  async setToken(token: string): Promise<void> {
    await Keychain.setGenericPassword('token', token, {
      service: `${SERVICE_NAME}.token`,
    });
  },

  async getToken(): Promise<string | null> {
    try {
      const credentials = await Keychain.getGenericPassword({
        service: `${SERVICE_NAME}.token`,
      });
      if (credentials) {
        return credentials.password;
      }
      return null;
    } catch {
      return null;
    }
  },

  async removeToken(): Promise<void> {
    await Keychain.resetGenericPassword({
      service: `${SERVICE_NAME}.token`,
    });
  },

  async setSessionId(sessionId: string): Promise<void> {
    await Keychain.setGenericPassword('sessionId', sessionId, {
      service: `${SERVICE_NAME}.sessionId`,
    });
  },

  async getSessionId(): Promise<string | null> {
    try {
      const credentials = await Keychain.getGenericPassword({
        service: `${SERVICE_NAME}.sessionId`,
      });
      if (credentials) {
        return credentials.password;
      }
      return null;
    } catch {
      return null;
    }
  },

  async removeSessionId(): Promise<void> {
    await Keychain.resetGenericPassword({
      service: `${SERVICE_NAME}.sessionId`,
    });
  },

  async clear(): Promise<void> {
    await this.removeToken();
    await this.removeSessionId();
  },
};