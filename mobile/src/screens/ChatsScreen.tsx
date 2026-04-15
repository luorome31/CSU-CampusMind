/**
 * ChatsScreen - 聊天页面
 *
 * 组合 MessageList + ChatInput + EmptyState
 * 有消息时显示 MessageList + ChatInput
 * 无消息时显示 EmptyState + ChatInput
 * 支持从 Home 导航时传入 dialogId 加载历史对话
 */

import React, { useCallback, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from '@react-navigation/native';
import { ChevronLeft } from 'lucide-react-native';
import { MessageList } from '../components/chat/MessageList';
import { ChatInput } from '../components/chat/ChatInput';
import { EmptyState } from '../components/chat/EmptyState';
import { useChatStream } from '../features/chat/useChatStream';
import { useChatStore } from '../features/chat/chatStore';
import { getDialogMessages } from '../api/dialog';
import { colors, spacing, typography } from '../styles';
import type { ChatsScreenProps } from '../navigation/types';

export function ChatsScreen({ navigation, route }: ChatsScreenProps) {
  const { sendMessage, isStreaming, messages } = useChatStream();
  const currentKnowledgeIds = useChatStore((s) => s.currentKnowledgeIds);
  const loadDialog = useChatStore((s) => s.loadDialog);
  const clearMessages = useChatStore((s) => s.clearMessages);
  const setIsLoadingHistory = useChatStore((s) => s.setIsLoadingHistory);
  const isLoadingHistory = useChatStore((s) => s.isLoadingHistory);
  const dialogId = route.params?.dialogId;

  // 每次 screen focus 时，如果是新建对话则清空消息
  useFocusEffect(
    useCallback(() => {
      if (!dialogId) {
        clearMessages();
      }
    }, [dialogId])
  );

  useEffect(() => {
    if (dialogId) {
      setIsLoadingHistory(true);
      getDialogMessages(dialogId)
        .then((dbMessages) => loadDialog(dialogId, dbMessages))
        .catch(console.error)
        .finally(() => setIsLoadingHistory(false));
    } else {
      clearMessages();
    }
  }, [dialogId]);

  const handleSend = useCallback(
    (content: string) => {
      sendMessage(content, currentKnowledgeIds);
    },
    [sendMessage, currentKnowledgeIds]
  );

  const hasMessages = messages.length > 0;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.navigate('HomeTab' as any)}
          activeOpacity={0.7}
        >
          <ChevronLeft size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>CampusMind</Text>
        <View style={styles.headerRight} />
      </View>
      <KeyboardAvoidingView
        style={styles.keyboardAvoid}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles.content}>
          {isLoadingHistory ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={colors.accent} />
              <Text style={styles.loadingText}>加载历史消息...</Text>
            </View>
          ) : hasMessages ? (
            <MessageList messages={messages} isStreaming={isStreaming} />
          ) : (
            <EmptyState />
          )}
        </View>
        <ChatInput onSend={handleSend} disabled={isStreaming} />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[3],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
    backgroundColor: colors.backgroundGlass,
  },
  backButton: {
    padding: spacing[1],
    marginLeft: -spacing[1],
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: typography.fontBold,
    color: colors.text,
    letterSpacing: 0.5,
  },
  headerRight: {
    width: 32,
  },
  keyboardAvoid: {
    flex: 1,
  },
  content: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: spacing[4],
    fontSize: typography.textBase,
    color: colors.textMuted,
  },
});
