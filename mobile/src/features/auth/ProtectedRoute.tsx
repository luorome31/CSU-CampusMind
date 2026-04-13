/**
 * ProtectedRoute - 路由保护组件
 * 未登录时重定向到 LoginScreen
 */
import React from 'react';
import { useAuthStore } from './authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  if (!isAuthenticated) {
    // This component is used within NavigationContainer
    // Actual redirect is handled by conditional rendering in RootNavigator
    return null;
  }

  return <>{children}</>;
}
