import { describe, it, expect, vi, beforeEach } from 'vitest';
import { knowledgeApi } from './knowledge';

describe('knowledgeApi', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it('fetchKnowledgeBases calls correct endpoint', async () => {
    const mockResponse = [
      { id: 'kb1', name: 'KB 1', description: 'desc', user_id: 'user1', create_time: '', update_time: '' }
    ];
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
      text: async () => JSON.stringify(mockResponse),
    });

    await knowledgeApi.fetchKnowledgeBases('user1');
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/users/user1/knowledge'),
      expect.any(Object)
    );
  });

  it('fetchFiles calls correct endpoint', async () => {
    const mockResponse = [{ id: 'file1', file_name: 'test.md' }];
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
      text: async () => JSON.stringify(mockResponse),
    });

    await knowledgeApi.fetchFiles('kb1');
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/knowledge/kb1/files'),
      expect.any(Object)
    );
  });

  it('fetchFileContent returns raw markdown string', async () => {
    const markdownContent = '# Hello\n\nThis is markdown.';
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      text: async () => markdownContent,
    });

    const result = await knowledgeApi.fetchFileContent('file1');
    expect(result).toBe(markdownContent);
  });
});
