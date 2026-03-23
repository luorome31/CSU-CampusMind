import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KnowledgeListPage } from './KnowledgeListPage';
import { MemoryRouter } from 'react-router-dom';
import { knowledgeListStore } from './knowledgeListStore';

vi.mock('./knowledgeListStore');

describe('KnowledgeListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders page title', () => {
    vi.mocked(knowledgeListStore).mockReturnValue({
      fetchKnowledgeBases: vi.fn(),
      knowledgeBases: [],
      currentKB: null,
      files: [],
      currentFile: null,
      currentFileContent: '',
      isLoadingKBs: false,
      isLoadingFiles: false,
      isLoadingContent: false,
      error: null,
      setCurrentKB: vi.fn(),
      clearError: vi.fn(),
      fetchFiles: vi.fn(),
      fetchFileContent: vi.fn(),
    } as any);

    render(<MemoryRouter><KnowledgeListPage /></MemoryRouter>);
    expect(screen.getByText('知识库')).toBeInTheDocument();
  });

  it('shows loading when isLoadingKBs is true', () => {
    vi.mocked(knowledgeListStore).mockReturnValue({
      fetchKnowledgeBases: vi.fn(),
      knowledgeBases: [],
      currentKB: null,
      files: [],
      currentFile: null,
      currentFileContent: '',
      isLoadingKBs: true,
      isLoadingFiles: false,
      isLoadingContent: false,
      error: null,
      setCurrentKB: vi.fn(),
      clearError: vi.fn(),
      fetchFiles: vi.fn(),
      fetchFileContent: vi.fn(),
    } as any);

    render(<MemoryRouter><KnowledgeListPage /></MemoryRouter>);
    expect(document.querySelector('.knowledge-list-loading')).toBeInTheDocument();
  });

  it('renders knowledge cards when loaded', () => {
    const mockKBs = [
      { id: 'kb1', name: 'KB 1', description: 'Desc 1', user_id: 'u1', create_time: '', update_time: '' }
    ];
    vi.mocked(knowledgeListStore).mockReturnValue({
      fetchKnowledgeBases: vi.fn(),
      knowledgeBases: mockKBs,
      currentKB: null,
      files: [],
      currentFile: null,
      currentFileContent: '',
      isLoadingKBs: false,
      isLoadingFiles: false,
      isLoadingContent: false,
      error: null,
      setCurrentKB: vi.fn(),
      clearError: vi.fn(),
      fetchFiles: vi.fn(),
      fetchFileContent: vi.fn(),
    } as any);

    render(<MemoryRouter><KnowledgeListPage /></MemoryRouter>);
    expect(screen.getByText('KB 1')).toBeInTheDocument();
  });
});
