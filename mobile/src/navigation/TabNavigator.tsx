/**
 * 底部 Tab 导航器
 * 4 个 Tab: Home / Chats / Knowledge / Profile
 */

import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text, StyleSheet } from 'react-native';
import { BlurView } from '@react-native-community/blur';
import {
  RootTabParamList,
  HomeStackParamList,
  ChatsStackParamList,
  KnowledgeStackParamList,
  ProfileStackParamList,
} from './types';
import { colors, typography, spacing } from '../styles';

// 占位组件（将在后续模块实现）
const PlaceholderScreen = () => <View style={styles.placeholder}><Text>Screen</Text></View>;

const Tab = createBottomTabNavigator<RootTabParamList>();
const HomeStack = createNativeStackNavigator<HomeStackParamList>();
const ChatsStack = createNativeStackNavigator<ChatsStackParamList>();
const KnowledgeStack = createNativeStackNavigator<KnowledgeStackParamList>();
const ProfileStack = createNativeStackNavigator<ProfileStackParamList>();

function HomeStackNavigator() {
  return (
    <HomeStack.Navigator screenOptions={{ headerShown: false }}>
      <HomeStack.Screen name="Home" component={PlaceholderScreen} />
    </HomeStack.Navigator>
  );
}

function ChatsStackNavigator() {
  return (
    <ChatsStack.Navigator screenOptions={{ headerShown: false }}>
      <ChatsStack.Screen name="Chats" component={PlaceholderScreen} />
    </ChatsStack.Navigator>
  );
}

function KnowledgeStackNavigator() {
  return (
    <KnowledgeStack.Navigator screenOptions={{ headerShown: false }}>
      <KnowledgeStack.Screen name="KnowledgeList" component={PlaceholderScreen} />
    </KnowledgeStack.Navigator>
  );
}

function ProfileStackNavigator() {
  return (
    <ProfileStack.Navigator screenOptions={{ headerShown: false }}>
      <ProfileStack.Screen name="Profile" component={PlaceholderScreen} />
    </ProfileStack.Navigator>
  );
}

// Tab 图标组件
function TabIcon({ name, focused }: { name: string; focused: boolean }) {
  const iconMap: Record<string, string> = {
    HomeTab: '🏠',
    ChatsTab: '💬',
    KnowledgeTab: '📚',
    ProfileTab: '👤',
  };
  return (
    <Text style={[styles.tabIcon, focused && styles.tabIconFocused]}>
      {iconMap[name] || '•'}
    </Text>
  );
}

// Tab Bar 毛玻璃背景组件
function TabBarBackground() {
  return (
    <BlurView
      style={StyleSheet.absoluteFill}
      blurType="light"
      blurAmount={80}
    />
  );
}

export function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused }) => <TabIcon name={route.name} focused={focused} />,
        tabBarActiveTintColor: colors.accent,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarStyle: styles.tabBar,
        tabBarLabelStyle: styles.tabLabel,
        tabBarBackground: () => <TabBarBackground />,
      })}
    >
      <Tab.Screen
        name="HomeTab"
        component={HomeStackNavigator}
        options={{ tabBarLabel: '首页' }}
      />
      <Tab.Screen
        name="ChatsTab"
        component={ChatsStackNavigator}
        options={{ tabBarLabel: '对话' }}
      />
      <Tab.Screen
        name="KnowledgeTab"
        component={KnowledgeStackNavigator}
        options={{ tabBarLabel: '知识库' }}
      />
      <Tab.Screen
        name="ProfileTab"
        component={ProfileStackNavigator}
        options={{ tabBarLabel: '我的' }}
      />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: colors.backgroundGlass,
    borderTopColor: colors.border,
    borderTopWidth: StyleSheet.hairlineWidth,
    paddingTop: spacing[1],
    height: 60,
  },
  tabLabel: {
    fontSize: typography.textXs,
    fontWeight: typography.fontMedium,
  },
  tabIcon: {
    fontSize: 20,
  },
  tabIconFocused: {
    opacity: 1,
  },
  placeholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
});
