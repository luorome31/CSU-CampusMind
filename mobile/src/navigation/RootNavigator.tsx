/**
 * 根导航器
 * 根据认证状态显示 AuthStack 或 MainTabs
 */
import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore } from '../features/auth/authStore';
import { TabNavigator } from './TabNavigator';
import { LoginScreen } from '../features/auth/LoginScreen';
import type { AuthStackParamList } from './types';

const AuthStack = createNativeStackNavigator<AuthStackParamList>();

function AuthStackNavigator() {
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="Login" component={LoginScreen} />
    </AuthStack.Navigator>
  );
}

function MainTabs() {
  return <TabNavigator />;
}

export function RootNavigator() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const initAuth = useAuthStore((s) => s.initAuth);

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainTabs /> : <AuthStackNavigator />}
    </NavigationContainer>
  );
}
