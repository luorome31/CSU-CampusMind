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

    await knowledgeApi.fetchKnowledgeBases();
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/knowledge'),
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

  it('createKnowledgeBase calls POST /knowledge/create with name and description', async () => {
    const mockResponse = {
      id: 'kb2',
      name: 'New KB',
      description: 'New description',
      user_id: 'user1',
      create_time: '2026-03-23T00:00:00Z',
      update_time: '2026-03-23T00:00:00Z',
    };
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
      text: async () => JSON.stringify(mockResponse),
    });

    const result = await knowledgeApi.createKnowledgeBase('New KB', 'New description');
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/knowledge/create'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ name: 'New KB', description: 'New description' }),
      })
    );
    expect(result).toEqual(mockResponse);
  });
});
