/**
 * 路由类型定义
 */

import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { BottomTabScreenProps } from '@react-navigation/bottom-tabs';
import type { CompositeScreenProps, NavigatorScreenParams } from '@react-navigation/native';

// === Tab Navigator ===
export type RootTabParamList = {
  HomeTab: NavigatorScreenParams<HomeStackParamList>;
  ChatsTab: NavigatorScreenParams<ChatsStackParamList>;
  KnowledgeTab: NavigatorScreenParams<KnowledgeStackParamList>;
  ProfileTab: NavigatorScreenParams<ProfileStackParamList>;
};

// === Home Stack ===
export type HomeStackParamList = {
  Home: undefined;
  KnowledgeBuild: undefined;
};

// === Chats Stack ===
export type ChatsStackParamList = {
  Chats: { dialogId?: string };
  ChatDetail: { dialogId: string };
};

// === Knowledge Stack ===
export type KnowledgeStackParamList = {
  KnowledgeList: undefined;
  KnowledgeDetail: { kbId: string };
  FileDetail: { fileId: string };
};

// === Profile Stack ===
export type ProfileStackParamList = {
  Profile: undefined;
  SessionManagement: undefined;
};

// === Screen Props ===
export type HomeScreenProps = CompositeScreenProps<
  NativeStackScreenProps<HomeStackParamList, 'Home'>,
  BottomTabScreenProps<RootTabParamList>
>;

export type ChatsScreenProps = CompositeScreenProps<
  NativeStackScreenProps<ChatsStackParamList, 'Chats'>,
  BottomTabScreenProps<RootTabParamList>
>;

export type KnowledgeScreenProps = CompositeScreenProps<
  NativeStackScreenProps<KnowledgeStackParamList, 'KnowledgeList'>,
  BottomTabScreenProps<RootTabParamList>
>;

export type ProfileScreenProps = CompositeScreenProps<
  NativeStackScreenProps<ProfileStackParamList, 'Profile'>,
  BottomTabScreenProps<RootTabParamList>
>;

// === ChatDetail Screen Props ===
export type ChatDetailScreenProps = CompositeScreenProps<
  NativeStackScreenProps<ChatsStackParamList, 'ChatDetail'>,
  BottomTabScreenProps<RootTabParamList>
>;

// === KnowledgeBuild Screen Props ===
export type KnowledgeBuildScreenProps = CompositeScreenProps<
  NativeStackScreenProps<HomeStackParamList, 'KnowledgeBuild'>,
  BottomTabScreenProps<RootTabParamList>
>;

// === KnowledgeDetail Screen Props ===
export type KnowledgeDetailScreenProps = CompositeScreenProps<
  NativeStackScreenProps<KnowledgeStackParamList, 'KnowledgeDetail'>,
  BottomTabScreenProps<RootTabParamList>
>;

// === FileDetail Screen Props ===
export type FileDetailScreenProps = CompositeScreenProps<
  NativeStackScreenProps<KnowledgeStackParamList, 'FileDetail'>,
  BottomTabScreenProps<RootTabParamList>
>;

// === SessionManagement Screen Props ===
export type SessionManagementScreenProps = CompositeScreenProps<
  NativeStackScreenProps<ProfileStackParamList, 'SessionManagement'>,
  BottomTabScreenProps<RootTabParamList>
>;

// === Auth Stack (未登录) ===
export type AuthStackParamList = {
  Login: undefined;
};

// === Login Screen Props ===
export type LoginScreenProps = NativeStackScreenProps<AuthStackParamList, 'Login'>;
