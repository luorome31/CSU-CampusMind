// src/utils/parseThinking.test.ts
import { describe, it, expect } from 'vitest';
import { parseThinkingContent } from './parseThinking';

describe('parseThinkingContent', () => {
  it('should parse single thinking block', () => {
    const input = '<think>用户想查询成绩，我需要使用 jwc_grade 工具来查询。</think>你好！我来帮你查询成绩。';
    const result = parseThinkingContent(input);

    expect(result.thinking).toHaveLength(1);
    expect(result.thinking[0]).toBe('用户想查询成绩，我需要使用 jwc_grade 工具来查询。');
    expect(result.text).toBe('你好！我来帮你查询成绩。');
  });

  it('should parse multiple thinking blocks', () => {
    const input = '<think>第一步分析：用户想查询成绩。</think>你好！<think>第二步：调用工具。</think>正在查询...';
    const result = parseThinkingContent(input);

    expect(result.thinking).toHaveLength(2);
    expect(result.thinking[0]).toBe('第一步分析：用户想查询成绩。');
    expect(result.thinking[1]).toBe('第二步：调用工具。');
    // Paragraphs are merged when thinking tags are removed
    expect(result.text).toBe('你好！正在查询...');
  });

  it('should handle empty thinking blocks', () => {
    const input = '<think></think>你好！</think>';
    const result = parseThinkingContent(input);

    expect(result.thinking).toHaveLength(0);
    expect(result.text).toBe('你好！');
  });

  it('should handle content without thinking tags', () => {
    const input = '这是一个普通的回复，没有任何思考标签。';
    const result = parseThinkingContent(input);

    expect(result.thinking).toHaveLength(0);
    expect(result.text).toBe('这是一个普通的回复，没有任何思考标签。');
  });

  it('should handle only thinking content', () => {
    const input = '<think>这是一个纯思考过程。</think>';
    const result = parseThinkingContent(input);

    expect(result.thinking).toHaveLength(1);
    expect(result.text).toBe('');
  });

  it('should trim whitespace in thinking content', () => {
    const input = '<think>   思考内容有空格  </think>文本';
    const result = parseThinkingContent(input);

    expect(result.thinking[0]).toBe('思考内容有空格');
    expect(result.text).toBe('文本');
  });

  it('should handle multiline thinking content', () => {
    const input = `<think>第一行
第二行
第三行</think>文本`;
    const result = parseThinkingContent(input);

    expect(result.thinking[0]).toBe('第一行\n第二行\n第三行');
    expect(result.text).toBe('文本');
  });

  it('should normalize excessive newlines in text', () => {
    const input = '<think>思考1</think>段落1\n\n\n\n段落2';
    const result = parseThinkingContent(input);

    expect(result.text).toBe('段落1\n\n段落2');
  });

  it('should handle the full example from the user', () => {
    const input = `<think>用户想查询成绩，我需要使用 jwc_grade 工具来查询。用户没有指定学期，所以我可以查询所有学期的成绩。</think>你好！我来帮你查询成绩。<think>教务系统会话已过期，这意味着用户需要重新登录。但是根据系统设定，用户已登录（学号: 8209220131）。可能是后端的教务系统认证出现了问题。我需要告知用户这个情况，并建议用户重新登录或稍后重试。
</think>

抱歉，目前无法查询到你的成绩信息。系统提示"教务系统会话已过期"。这可能是因为：1. 教务系统的登录状态已失效2. 系统连接问题**建议你可以尝试：**1. 稍后重新发起查询2. 如果问题持续，可能需要重新登录教务系统请问还有其他我可以帮助你的吗？`;

    const result = parseThinkingContent(input);

    expect(result.thinking).toHaveLength(2);
    expect(result.thinking[0]).toContain('用户想查询成绩');
    expect(result.thinking[1]).toContain('教务系统会话已过期');
    expect(result.text).toContain('你好！我来帮你查询成绩。');
    expect(result.text).toContain('抱歉，目前无法查询到你的成绩信息');
  });
});
