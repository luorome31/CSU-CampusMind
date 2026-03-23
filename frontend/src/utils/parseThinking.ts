// src/utils/parseThinking.ts

export interface ParsedContent {
  thinking: string[];
  text: string;
}

/**
 * Parses markdown content containing <think>...</think> thinking tags.
 * Returns separated thinking blocks and the actual text content.
 */
export function parseThinkingContent(content: string): ParsedContent {
  const thinking: string[] = [];
  let text = content;

  // Match <think>...</think> tags (including multiline)
  const thinkTagPattern = /<think>([\s\S]*?)(?=<\/think>|$)/g;

  text = text.replace(thinkTagPattern, (_, thinkContent) => {
    const trimmed = thinkContent.trim();
    if (trimmed) {
      thinking.push(trimmed);
    }
    return '';
  });

  // Clean up any remaining </think> tags that might be orphaned
  text = text.replace(/<\/think>/g, '');

  // Trim whitespace but preserve paragraph structure
  text = text.replace(/\n{3,}/g, '\n\n').trim();

  return { thinking, text };
}
