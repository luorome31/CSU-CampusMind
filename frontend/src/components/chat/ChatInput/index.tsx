// src/components/chat/ChatInput/index.tsx
import React, { useState } from 'react';
import { Send } from 'lucide-react';
import { Button } from '../../ui/Button';
import './ChatInput.css';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

/**
 * Chat input with send button.
 * Disabled during streaming.
 */
export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [value, setValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
  };

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <div className="chat-input-wrapper">
        <input
          type="text"
          className="chat-input"
          placeholder={disabled ? '等待回复中...' : '输入消息...'}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={disabled}
          autoComplete="off"
        />
        <Button
          type="submit"
          variant="primary"
          size="md"
          disabled={disabled || !value.trim()}
          className="chat-input-send"
        >
          <Send size={16} />
        </Button>
      </div>
    </form>
  );
};

export default ChatInput;