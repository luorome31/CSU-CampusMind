import { describe, it, expect, beforeEach, vi } from 'vitest';
import { knowledgeListStore } from './knowledgeListStore';
import * as knowledgeApi from '../../api/knowledge';

vi.mock('../../api/knowledge');

describe('knowledgeListStore', () => {
  beforeEach(() => {
    knowledgeListStore.setState({
      knowledgeBases: [],
      currentKB: null,
      files: [],
      currentFile: null,
      currentFileContent: '',
      isLoadingKBs: false,
      isLoadingFiles: false,
      isLoadingContent: false,
      error: null,
    });
  });

  it('fetchKnowledgeBases loads KBs successfully', async () => {
    const mockKBs: knowledgeApi.KnowledgeBase[] = [
      { id: 'kb1', name: 'KB 1', description: 'desc', user_id: 'user1', create_time: '', update_time: '' }
    ];
    vi.mocked(knowledgeApi.knowledgeApi.fetchKnowledgeBases).mockResolvedValue(mockKBs);

    await knowledgeListStore.getState().fetchKnowledgeBases();

    expect(knowledgeListStore.getState().knowledgeBases).toEqual(mockKBs);
    expect(knowledgeListStore.getState().isLoadingKBs).toBe(false);
  });

  it('fetchKnowledgeBases handles error', async () => {
    vi.mocked(knowledgeApi.knowledgeApi.fetchKnowledgeBases).mockRejectedValue(new Error('API Error'));

    await knowledgeListStore.getState().fetchKnowledgeBases();

    expect(knowledgeListStore.getState().error).toBe('API Error');
    expect(knowledgeListStore.getState().isLoadingKBs).toBe(false);
  });

  it('fetchFiles loads files for given KB', async () => {
    const mockFiles: knowledgeApi.KnowledgeFile[] = [
      { id: 'f1', file_name: 'test.md', knowledge_id: 'kb1', user_id: 'u1', status: 'success', oss_url: '', file_size: 1024, create_time: '', update_time: '' }
    ];
    vi.mocked(knowledgeApi.knowledgeApi.fetchFiles).mockResolvedValue(mockFiles);

    await knowledgeListStore.getState().fetchFiles('kb1');

    expect(knowledgeListStore.getState().files).toEqual(mockFiles);
  });

  it('fetchFileContent loads content and sets currentFile', async () => {
    const mockFile: knowledgeApi.KnowledgeFile = {
      id: 'f1', file_name: 'test.md', knowledge_id: 'kb1', user_id: 'u1',
      status: 'success', oss_url: '', file_size: 1024, create_time: '', update_time: ''
    };
    const mockContent = '# Markdown Content';
    vi.mocked(knowledgeApi.knowledgeApi.fetchFileContent).mockResolvedValue(mockContent);
    vi.mocked(knowledgeApi.knowledgeApi.fetchFiles).mockResolvedValue([mockFile]);

    await knowledgeListStore.getState().fetchFileContent('f1');

    expect(knowledgeListStore.getState().currentFileContent).toBe(mockContent);
  });

  it('clearError resets error state', async () => {
    knowledgeListStore.setState({ error: 'Some error' });
    knowledgeListStore.getState().clearError();
    expect(knowledgeListStore.getState().error).toBeNull();
  });

  it('createKnowledgeBase adds new KB to knowledgeBases array', async () => {
    const newKB: knowledgeApi.KnowledgeBase = {
      id: 'kb-new', name: 'Test KB', description: 'Test desc', user_id: 'user1', create_time: '', update_time: ''
    };
    vi.mocked(knowledgeApi.knowledgeApi.createKnowledgeBase).mockResolvedValue(newKB);

    await knowledgeListStore.getState().createKnowledgeBase('Test KB', 'Test desc');

    expect(knowledgeListStore.getState().knowledgeBases).toContainEqual(newKB);
    expect(knowledgeListStore.getState().error).toBeNull();
  });

  it('createKnowledgeBase handles error', async () => {
    vi.mocked(knowledgeApi.knowledgeApi.createKnowledgeBase).mockRejectedValue(new Error('Create failed'));

    await knowledgeListStore.getState().createKnowledgeBase('Test KB', 'Test desc');

    expect(knowledgeListStore.getState().error).toBe('Create failed');
  });
});