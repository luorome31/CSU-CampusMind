import { useState, useEffect, useRef } from 'react';
import { network } from '../utils/network';

export function useNetworkStatus() {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const toastShownRef = useRef(false);

  useEffect(() => {
    // 初始检查
    network.isConnected().then(setIsConnected);

    // 监听变化
    const unsubscribe = network.addListener((state) => {
      const connected = state.isConnected ?? false;
      setIsConnected(connected);

      // 使用 ref 避免 stale closure
      if (!connected && !toastShownRef.current) {
        console.log('网络不可用');
        toastShownRef.current = true;
      } else if (connected && toastShownRef.current) {
        console.log('网络已恢复');
        toastShownRef.current = false;
      }
    });

    return unsubscribe;
  }, []); // 空依赖，监听器持久化，ref 稳定

  const refresh = async () => {
    const connected = await network.isConnected();
    setIsConnected(connected);
    return connected;
  };

  return {
    isConnected,
    isChecking: isConnected === null,
    refresh,
  };
}
