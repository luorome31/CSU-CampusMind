/**
 * MessageBubble Component
 *
 * Single message bubble for chat.
 * - User: right-aligned, userBg background
 * - Assistant: left-aligned, backgroundCard background, with avatar
 */

import React, { useMemo } from 'react';
import { View, Text, Image, StyleSheet, ScrollView } from 'react-native';
import Markdown from 'react-native-markdown-display';
import { colors } from '../../../styles/tokens/colors';
import type { ChatMessage } from '../../../features/chat/chatStore';
import { ThinkingBlock } from '../ThinkingBlock';
import { ToolGroup } from '../ToolGroup';
import { parseThinkingContent } from '../../../utils/parseThinking';

interface MessageBubbleProps {
  message: ChatMessage;
}

// Assistant avatar
const ASSISTANT_AVATAR = require('../../../assets/csu-xiaotuanzi-answer.png');

/**
 * MessageBubble - Renders a single chat message bubble
 *
 * @param message - ChatMessage object with role and content
 */
const markdownRules = {
  table: (node: any, children: any, parent: any, styles: any) => (
    <ScrollView horizontal key={node.key} style={styles.tableScrollView}>
      <View style={styles.table}>{children}</View>
    </ScrollView>
  ),
};

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  // Parse thinking content from assistant messages
  const parsedContent = useMemo(() => {
    if (isUser) return null;
    return parseThinkingContent(message.content);
  }, [message.content, isUser]);

  return (
    <View
      style={[
        styles.container,
        isUser ? styles.userContainer : styles.assistantContainer,
      ]}
    >
      {/* Avatar for assistant messages */}
      {!isUser && (
        <Image
          source={ASSISTANT_AVATAR}
          style={styles.avatar}
          resizeMode="cover"
        />
      )}

      {/* Message content */}
      <View
        style={[
          styles.bubble,
          isUser ? styles.userBubble : styles.assistantBubble,
        ]}
      >
        {isUser ? (
          <Text style={[styles.userText]}>{message.content}</Text>
        ) : parsedContent ? (
          <>
            {parsedContent.thinking.length > 0 && (
              <ThinkingBlock thinking={parsedContent.thinking} />
            )}
            {parsedContent.text && (
              <Markdown style={markdownStyles} rules={markdownRules as any}>{parsedContent.text}</Markdown>
            )}
            {message.events.length > 0 && <ToolGroup events={message.events} />}
          </>
        ) : (
          // Fallback for messages without thinking tags (legacy or simple text)
          <Markdown style={markdownStyles} rules={markdownRules as any}>{message.content}</Markdown>
        )}
      </View>
    </View>
  );
};

// Markdown styles for assistant messages
const markdownStyles = StyleSheet.create({
  body: {
    color: colors.assistantText,
    fontSize: 16,
    lineHeight: 24,
  },
  heading1: {
    color: colors.text,
    fontSize: 20,
    fontWeight: 'bold',
    marginVertical: 4,
  },
  heading2: {
    color: colors.text,
    fontSize: 18,
    fontWeight: 'bold',
    marginVertical: 3,
  },
  heading3: {
    color: colors.text,
    fontSize: 16,
    fontWeight: 'bold',
    marginVertical: 2,
  },
  paragraph: {
    marginVertical: 4,
  },
  link: {
    color: colors.accent,
  },
  code_inline: {
    backgroundColor: colors.moodBg,
    color: colors.accent,
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderRadius: 4,
    fontFamily: 'monospace',
    fontSize: 14,
  },
  code_block: {
    backgroundColor: colors.moodBg,
    padding: 8,
    borderRadius: 8,
    marginVertical: 4,
  },
  fence: {
    backgroundColor: colors.moodBg,
    padding: 8,
    borderRadius: 8,
    marginVertical: 4,
  },
  list_item: {
    marginVertical: 2,
  },
  bullet_list: {
    marginVertical: 4,
  },
  ordered_list: {
    marginVertical: 4,
  },
  blockquote: {
    backgroundColor: colors.moodBg,
    borderLeftColor: colors.accent,
    borderLeftWidth: 4,
    paddingLeft: 8,
    marginVertical: 4,
  },
  strong: {
    fontWeight: 'bold',
  },
  em: {
    fontStyle: 'italic',
  },
  hr: {
    backgroundColor: colors.border,
    height: 1,
    marginVertical: 8,
  },
  tableScrollView: {
    marginVertical: 8,
  },
});

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    marginVertical: 8,
    paddingHorizontal: 16,
  },
  assistantContainer: {
    justifyContent: 'flex-start',
  },
  userContainer: {
    justifyContent: 'flex-end',
  },
  avatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    marginRight: 8,
  },
  bubble: {
    maxWidth: '75%',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 16,
  },
  userBubble: {
    backgroundColor: colors.userBg,
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    backgroundColor: 'transparent',
    borderBottomLeftRadius: 4,
  },
  userText: {
    color: colors.text,
    fontSize: 16,
    lineHeight: 24,
  },
});

export default MessageBubble;
