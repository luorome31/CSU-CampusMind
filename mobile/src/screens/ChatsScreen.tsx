/**
 * ChatsScreen - 聊天页面
 *
 * 组合 MessageList + ChatInput + EmptyState
 * 有消息时显示 MessageList + ChatInput
 * 无消息时显示 EmptyState + ChatInput
 */

import React, { useCallback } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MessageList } from '../components/chat/MessageList';
import { ChatInput } from '../components/chat/ChatInput';
import { EmptyState } from '../components/chat/EmptyState';
import { useChatStream } from '../features/chat/useChatStream';
import { useChatStore } from '../features/chat/chatStore';
import { colors } from '../styles';

export function ChatsScreen() {
  const { sendMessage, isStreaming, messages } = useChatStream();
  const currentKnowledgeIds = useChatStore((s) => s.currentKnowledgeIds);

  const handleSend = useCallback(
    (content: string) => {
      sendMessage(content, currentKnowledgeIds);
    },
    [sendMessage, currentKnowledgeIds]
  );

  const hasMessages = messages.length > 0;

  return (
    <SafeAreaView style={styles.container} edges={['top', 'bottom']}>
      <KeyboardAvoidingView
        style={styles.keyboardAvoid}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        <View style={styles.content}>
          {hasMessages ? (
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
  keyboardAvoid: {
    flex: 1,
  },
  content: {
    flex: 1,
  },
});
