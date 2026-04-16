/**
 * ChatInput Component
 *
 * Multi-line chat input with auto-grow TextInput and send button.
 * - Placeholder changes based on disabled state
 * - Send button only visible when there's content
 * - Auto-grows as content increases (minHeight: 24, maxHeight: 120)
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Keyboard,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Send } from 'lucide-react-native';
import { colors, spacing } from '../../../styles';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const MIN_HEIGHT = 24;
const MAX_HEIGHT = 120;

/**
 * ChatInput - Multi-line input with send button
 *
 * @param onSend - Callback when message is sent
 * @param disabled - Disable input during streaming
 */
export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [value, setValue] = useState('');
  const [inputHeight, setInputHeight] = useState(MIN_HEIGHT);
  const insets = useSafeAreaInsets();

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
    Keyboard.dismiss();
  }, [value, disabled, onSend]);

  const handleChangeText = useCallback((text: string) => {
    setValue(text);
  }, []);

  const handleContentSizeChange = useCallback((e: { nativeEvent: { contentSize: { height: number } } }) => {
    const newHeight = e.nativeEvent.contentSize.height;
    setInputHeight(Math.min(Math.max(newHeight, MIN_HEIGHT), MAX_HEIGHT));
  }, []);

  const showSendButton = value.trim().length > 0 && !disabled;

  return (
    <View style={[styles.container, { paddingBottom: Math.max(insets.bottom, spacing[3]) }]}>
      <View style={[styles.inputWrapper, disabled && styles.inputWrapperDisabled]}>
        <TextInput
          testID="chat-input"
          style={[styles.textInput, { height: inputHeight }]}
          placeholder={disabled ? '等待回复中...' : '输入消息...'}
          placeholderTextColor={colors.textMuted}
          value={value}
          onChangeText={handleChangeText}
          onContentSizeChange={handleContentSizeChange}
          multiline
          maxLength={2000}
          editable={!disabled}
        />
        <TouchableOpacity
          testID="send-button"
          style={[styles.sendButton, showSendButton && styles.sendButtonActive]}
          onPress={handleSend}
          disabled={!showSendButton}
          activeOpacity={0.7}
        >
          <Send
            size={20}
            color={showSendButton ? colors.backgroundCard : colors.textMuted}
            strokeWidth={2}
          />
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: spacing[4],
    paddingTop: spacing[3],
    backgroundColor: 'transparent',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.background,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing[3],
    paddingVertical: spacing[2],
    minHeight: 44,
  },
  inputWrapperDisabled: {
    opacity: 0.7,
    backgroundColor: colors.backgroundGlass,
  },
  textInput: {
    flex: 1,
    fontSize: 16,
    lineHeight: 20,
    color: colors.text,
    paddingVertical: 8,
    paddingHorizontal: 0,
    margin: 0,
  },
  sendButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'flex-end',
    marginLeft: spacing[2],
    backgroundColor: colors.backgroundGlass,
  },
  sendButtonActive: {
    backgroundColor: colors.accent,
  },
});

export default ChatInput;
