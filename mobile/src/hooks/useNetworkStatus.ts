/**
 * 网络状态 Hook
 */

import { useState, useEffect, useCallback } from 'react';
import { network } from '../utils/network';

export function useNetworkStatus() {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [toastShown, setToastShown] = useState(false);

  useEffect(() => {
    // 初始检查
    network.isConnected().then(setIsConnected);

    // 监听变化
    const unsubscribe = network.addListener((state) => {
      const connected = state.isConnected ?? false;
      setIsConnected(connected);

      // 显示提示
      if (!connected && !toastShown) {
        console.log('网络不可用');
        setToastShown(true);
      } else if (connected && toastShown) {
        console.log('网络已恢复');
        setToastShown(false);
      }
    });

    return unsubscribe;
  }, [toastShown]);

  const refresh = useCallback(async () => {
    const connected = await network.isConnected();
    setIsConnected(connected);
    return connected;
  }, []);

  return {
    isConnected,
    isChecking: isConnected === null,
    refresh,
  };
}
