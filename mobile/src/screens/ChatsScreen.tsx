/**
 * ChatsScreen - 聊天页面
 *
 * 组合 MessageList + ChatInput + EmptyState
 * 有消息时显示 MessageList + ChatInput
 * 无消息时显示 EmptyState + ChatInput
 */

import React, { useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ChevronLeft } from 'lucide-react-native';
import { MessageList } from '../components/chat/MessageList';
import { ChatInput } from '../components/chat/ChatInput';
import { EmptyState } from '../components/chat/EmptyState';
import { useChatStream } from '../features/chat/useChatStream';
import { useChatStore } from '../features/chat/chatStore';
import { colors, spacing, typography } from '../styles';

export function ChatsScreen({ navigation }: any) {
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
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => navigation.navigate('HomeTab')}
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
});
