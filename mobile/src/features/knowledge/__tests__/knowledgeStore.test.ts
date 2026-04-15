import { renderHook, act } from '@testing-library/react-native';
import { useKnowledgeStore } from '../knowledgeStore';

describe('useKnowledgeStore', () => {
  it('should have initial state', () => {
    const { result } = renderHook(() => useKnowledgeStore());
    expect(result.current.knowledgeBases).toEqual([]);
    expect(result.current.files).toEqual([]);
    expect(result.current.currentFileContent).toBe('');
    expect(result.current.isLoadingKBs).toBe(false);
  });
});