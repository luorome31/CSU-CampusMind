/**
 * Navigation Types Tests
 */

import type {
  RootTabParamList,
  HomeStackParamList,
  ChatsStackParamList,
  KnowledgeStackParamList,
  ProfileStackParamList,
  HomeScreenProps,
  ChatsScreenProps,
  KnowledgeScreenProps,
  ProfileScreenProps,
  ChatDetailScreenProps,
  KnowledgeBuildScreenProps,
  KnowledgeDetailScreenProps,
  FileDetailScreenProps,
  SessionManagementScreenProps,
} from './types';

describe('Navigation types', () => {
  describe('RootTabParamList', () => {
    it('should have 4 tab routes', () => {
      const tabs: RootTabParamList = {
        HomeTab: { screen: 'Home' },
        ChatsTab: { screen: 'Chats', params: {} },
        KnowledgeTab: { screen: 'KnowledgeList' },
        ProfileTab: { screen: 'Profile' },
      };
      expect(Object.keys(tabs).length).toBe(4);
    });
  });

  describe('ChatsStackParamList', () => {
    it('should accept ChatDetail params', () => {
      const params: ChatsStackParamList['ChatDetail'] = { dialogId: '123' };
      expect(params.dialogId).toBe('123');
    });
  });

  describe('KnowledgeStackParamList', () => {
    it('should accept KnowledgeDetail params', () => {
      const params: KnowledgeStackParamList['KnowledgeDetail'] = { kbId: 'kb-1' };
      expect(params.kbId).toBe('kb-1');
    });

    it('should accept FileDetail params', () => {
      const params: KnowledgeStackParamList['FileDetail'] = { fileId: 'file-1' };
      expect(params.fileId).toBe('file-1');
    });
  });
});
