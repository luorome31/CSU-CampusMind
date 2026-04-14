/**
 * MessageList Component
 *
 * Scrollable message list container using FlatList.
 * Auto-scrolls to bottom when new messages arrive or during streaming.
 */

import React, { useRef, useEffect } from 'react';
import { FlatList, View, StyleSheet } from 'react-native';
import { MessageBubble } from '../MessageBubble';
import type { ChatMessage } from '../../../features/chat/chatStore';

interface MessageListProps {
  messages: ChatMessage[];
  isStreaming: boolean;
}

/**
 * MessageList - Renders a scrollable list of chat messages
 *
 * Uses FlatList for efficient rendering of large message lists.
 * Auto-scrolls to bottom when messages change or streaming updates.
 *
 * @param messages - Array of ChatMessage objects to display
 * @param isStreaming - Whether streaming is in progress (triggers scroll to bottom)
 */
export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isStreaming,
}) => {
  const flatListRef = useRef<FlatList<ChatMessage>>(null);

  // Auto-scroll to bottom when messages change or streaming updates
  useEffect(() => {
    if (messages.length > 0) {
      flatListRef.current?.scrollToEnd({ animated: true });
    }
  }, [messages, isStreaming]);

  const renderItem = ({ item }: { item: ChatMessage }) => (
    <MessageBubble message={item} />
  );

  const keyExtractor = (item: ChatMessage) => item.id;

  // Render empty state as a placeholder View
  const ListEmptyComponent = () => <View style={styles.emptyContainer} />;

  return (
    <View style={styles.container} testID="message-list">
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderItem}
        keyExtractor={keyExtractor}
        ListEmptyComponent={ListEmptyComponent}
        showsVerticalScrollIndicator={true}
        contentContainerStyle={styles.contentContainer}
        onContentSizeChange={() => {
          // Ensure we scroll to end when content size changes (e.g., streaming)
          if (messages.length > 0) {
            flatListRef.current?.scrollToEnd({ animated: true });
          }
        }}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentContainer: {
    flexGrow: 1,
    justifyContent: 'flex-end',
  },
  emptyContainer: {
    flex: 1,
    minHeight: 1,
  },
});

export default MessageList;