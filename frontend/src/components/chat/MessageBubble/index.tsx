// src/components/chat/MessageBubble/index.tsx
import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { ToolGroup } from '../ToolGroup';
import { ThinkingBlock } from '../ThinkingBlock';
import type { ChatMessage } from '../../../features/chat/chatStore';
import { ASSISTANT_AVATAR } from '../../../utils/avatar';
import { parseThinkingContent } from '../../../utils/parseThinking';
import './MessageBubble.css';

interface MessageBubbleProps {
  message: ChatMessage;
}

// Warm Paper themed syntax highlighting style
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const warmPaperStyle: any = {
  'code[class*="language-"]': {
    color: '#3B3D3F',
    background: 'none',
    fontFamily: 'ui-monospace, "SF Mono", Monaco, Consolas, monospace',
    fontSize: '0.875rem',
    textAlign: 'left',
    whiteSpace: 'pre',
    wordSpacing: 'normal',
    wordBreak: 'normal',
    wordWrap: 'normal',
    lineHeight: '1.6',
    tabSize: '2',
    hyphens: 'none',
  },
  'pre[class*="language-"]': {
    color: '#3B3D3F',
    background: '#FAF5E9',
    fontFamily: 'ui-monospace, "SF Mono", Monaco, Consolas, monospace',
    fontSize: '0.875rem',
    textAlign: 'left',
    whiteSpace: 'pre',
    wordSpacing: 'normal',
    wordBreak: 'normal',
    wordWrap: 'normal',
    lineHeight: '1.6',
    tabSize: '2',
    hyphens: 'none',
    padding: '1em',
    margin: '0.75em 0',
    overflow: 'auto',
    borderRadius: '8px',
    border: '1px solid rgba(83, 125, 150, 0.15)',
    boxShadow: '0 2px 8px rgba(59, 61, 63, 0.06)',
  },
  comment: { color: '#8E9196', fontStyle: 'italic' },
  prolog: { color: '#8E9196' },
  doctype: { color: '#8E9196' },
  cdata: { color: '#8E9196' },
  punctuation: { color: '#6B6F73' },
  property: { color: '#537D96' },
  tag: { color: '#537D96' },
  boolean: { color: '#C4846C' },
  number: { color: '#C4846C' },
  constant: { color: '#C4846C' },
  symbol: { color: '#C4846C' },
  deleted: { color: '#cf222e' },
  selector: { color: '#7BAE7F' },
  'attr-name': { color: '#7BAE7F' },
  string: { color: '#7BAE7F' },
  char: { color: '#7BAE7F' },
  builtin: { color: '#7BAE7F' },
  inserted: { color: '#7BAE7F' },
  operator: { color: '#6B6F73' },
  entity: { color: '#537D96', cursor: 'help' },
  url: { color: '#537D96' },
  'atrule': { color: '#537D96' },
  'attr-value': { color: '#7BAE7F' },
  keyword: { color: '#537D96', fontWeight: 'normal' },
  function: { color: '#456A80' },
  'class-name': { color: '#456A80' },
  regex: { color: '#C4846C' },
  important: { color: '#C4846C', fontWeight: 'bold' },
  variable: { color: '#C4846C' },
  bold: { fontWeight: 'bold' },
  italic: { fontStyle: 'italic' },
};

// Custom code component for syntax highlighting
const CodeBlock = ({ className, children }: { className?: string; children?: React.ReactNode }) => {
  const match = /language-(\w+)/.exec(className || '');
  const inline = !match;
  return !inline ? (
    <SyntaxHighlighter
      language={match[1]}
      style={warmPaperStyle}
      PreTag="div"
    >
      {String(children).replace(/\n$/, '')}
    </SyntaxHighlighter>
  ) : (
    <code className={className}>{children}</code>
  );
};

/**
 * Single message bubble.
 * - User: right-aligned, dark background
 * - Assistant: left-aligned, light background, supports Markdown + tool events + thinking process
 */
export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
}) => {
  const isUser = message.role === 'user';

  // Parse thinking content from assistant messages
  const parsedContent = useMemo(() => {
    if (isUser) return null;
    return parseThinkingContent(message.content);
  }, [message.content, isUser]);

  return (
    <div className={`message-bubble message-${isUser ? 'user' : 'assistant'}`}>
      {!isUser && (
        <div className="message-avatar">
          <img src={ASSISTANT_AVATAR} alt="Assistant" />
        </div>
      )}
      <div className="message-content">
        {isUser ? (
          <p className="message-text">{message.content}</p>
        ) : parsedContent ? (
          <>
            {parsedContent.thinking.length > 0 && (
              <ThinkingBlock thinking={parsedContent.thinking} />
            )}
            {parsedContent.text && (
              <div className="message-markdown">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={{ code: CodeBlock }}>
                  {parsedContent.text}
                </ReactMarkdown>
              </div>
            )}
            {message.events.length > 0 && <ToolGroup events={message.events} />}
          </>
        ) : (
          // Fallback for messages without thinking tags (legacy or simple text)
          <>
            <div className="message-markdown">
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={{ code: CodeBlock }}>
                {message.content}
              </ReactMarkdown>
            </div>
            {message.events.length > 0 && <ToolGroup events={message.events} />}
          </>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;