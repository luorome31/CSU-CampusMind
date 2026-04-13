/**
 * 网络状态工具
 */

import NetInfo, { NetInfoState } from '@react-native-community/netinfo';

export const network = {
  /**
   * 获取当前网络状态
   */
  async getStatus(): Promise<NetInfoState> {
    return NetInfo.fetch();
  },

  /**
   * 检查是否已连接
   */
  async isConnected(): Promise<boolean> {
    const state = await this.getStatus();
    return state.isConnected ?? false;
  },

  /**
   * 监听网络状态变化
   */
  addListener(
    listener: (state: NetInfoState) => void
  ): () => void {
    const unsubscribe = NetInfo.addEventListener(listener);
    return unsubscribe;
  },
};
