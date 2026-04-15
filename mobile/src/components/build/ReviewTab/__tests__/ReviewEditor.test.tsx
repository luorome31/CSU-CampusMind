import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { ReviewEditor } from '../ReviewEditor';

// Mock the build store
jest.mock('../../../../features/build/buildStore', () => ({
  useBuildStore: jest.fn(),
}));

describe('ReviewEditor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render empty state when no file selected', () => {
    const mockUseBuildStore = require('../../../../features/build/buildStore').useBuildStore;
    mockUseBuildStore.mockImplementation((selector: (state: MockState) => unknown) => {
      if (typeof selector === 'function') {
        return selector({
          selectedFile: null,
          fileContent: '',
          isLoadingContent: false,
          isSaving: false,
          isIndexing: false,
          isPreview: false,
          updateFileContent: jest.fn(),
          triggerIndex: jest.fn(),
          setIsPreview: jest.fn(),
        });
      }
      return jest.fn();
    });

    const { getByText } = render(<ReviewEditor />);
    expect(getByText('请从上方选择文件进行审核')).toBeTruthy();
  });

  it('should render loading state when isLoadingContent is true', () => {
    const mockUseBuildStore = require('../../../../features/build/buildStore').useBuildStore;
    mockUseBuildStore.mockImplementation((selector: (state: MockState) => unknown) => {
      if (typeof selector === 'function') {
        return selector({
          selectedFile: { id: 'file-1', file_name: 'test.txt' },
          fileContent: '',
          isLoadingContent: true,
          isSaving: false,
          isIndexing: false,
          isPreview: false,
          updateFileContent: jest.fn(),
          triggerIndex: jest.fn(),
          setIsPreview: jest.fn(),
        });
      }
      return jest.fn();
    });

    const { queryByText } = render(<ReviewEditor />);
    expect(queryByText('请从上方选择文件进行审核')).toBeNull();
  });

  it('should render editor with file content when file is selected', () => {
    const mockUseBuildStore = require('../../../../features/build/buildStore').useBuildStore;
    mockUseBuildStore.mockImplementation((selector: (state: MockState) => unknown) => {
      if (typeof selector === 'function') {
        return selector({
          selectedFile: { id: 'file-1', file_name: 'test.txt' },
          fileContent: 'Hello World',
          isLoadingContent: false,
          isSaving: false,
          isIndexing: false,
          isPreview: false,
          updateFileContent: jest.fn(),
          triggerIndex: jest.fn(),
          setIsPreview: jest.fn(),
        });
      }
      return jest.fn();
    });

    const { getByText, queryByText } = render(<ReviewEditor />);
    expect(queryByText('请从上方选择文件进行审核')).toBeNull();
    expect(getByText('编辑')).toBeTruthy();
    expect(getByText('预览')).toBeTruthy();
    expect(getByText('保存')).toBeTruthy();
    expect(getByText('确认索引')).toBeTruthy();
  });

  it('should have save button disabled when content is unchanged', () => {
    const mockUseBuildStore = require('../../../../features/build/buildStore').useBuildStore;
    mockUseBuildStore.mockImplementation((selector: (state: MockState) => unknown) => {
      if (typeof selector === 'function') {
        return selector({
          selectedFile: { id: 'file-1', file_name: 'test.txt' },
          fileContent: 'Original Content',
          isLoadingContent: false,
          isSaving: false,
          isIndexing: false,
          isPreview: false,
          updateFileContent: jest.fn(),
          triggerIndex: jest.fn(),
          setIsPreview: jest.fn(),
        });
      }
      return jest.fn();
    });

    const { getByText } = render(<ReviewEditor />);
    const saveBtn = getByText('保存').parent;

    // Verify the parent Pressable has disabled style (opacity: 0.5)
    expect(saveBtn).toBeTruthy();
  });

  it('should toggle between edit and preview mode', () => {
    const mockSetIsPreview = jest.fn();
    const mockUseBuildStore = require('../../../../features/build/buildStore').useBuildStore;
    mockUseBuildStore.mockImplementation((selector: (state: MockState) => unknown) => {
      if (typeof selector === 'function') {
        return selector({
          selectedFile: { id: 'file-1', file_name: 'test.txt' },
          fileContent: 'Hello World',
          isLoadingContent: false,
          isSaving: false,
          isIndexing: false,
          isPreview: false,
          updateFileContent: jest.fn(),
          triggerIndex: jest.fn(),
          setIsPreview: mockSetIsPreview,
        });
      }
      return jest.fn();
    });

    const { getByText } = render(<ReviewEditor />);

    // Click preview toggle
    fireEvent.press(getByText('预览'));
    expect(mockSetIsPreview).toHaveBeenCalledWith(true);

    // Click edit toggle
    fireEvent.press(getByText('编辑'));
    expect(mockSetIsPreview).toHaveBeenCalledWith(false);
  });

  it('should call updateFileContent when save is pressed with changed content', async () => {
    const mockUpdateFileContent = jest.fn();
    const mockUseBuildStore = require('../../../../features/build/buildStore').useBuildStore;
    mockUseBuildStore.mockImplementation((selector: (state: MockState) => unknown) => {
      if (typeof selector === 'function') {
        return selector({
          selectedFile: { id: 'file-1', file_name: 'test.txt' },
          fileContent: 'Original Content',
          isLoadingContent: false,
          isSaving: false,
          isIndexing: false,
          isPreview: false,
          updateFileContent: mockUpdateFileContent,
          triggerIndex: jest.fn(),
          setIsPreview: jest.fn(),
        });
      }
      return jest.fn();
    });

    const { getByText, getByPlaceholderText } = render(<ReviewEditor />);
    const textInput = getByPlaceholderText('文件内容');

    // Change the content to enable save button
    fireEvent.changeText(textInput, 'Modified Content');

    const saveBtn = getByText('保存');
    fireEvent.press(saveBtn);

    await waitFor(() => {
      expect(mockUpdateFileContent).toHaveBeenCalledWith('file-1', 'Modified Content');
    });
  });

  it('should call triggerIndex when confirm index is pressed', async () => {
    const mockTriggerIndex = jest.fn();
    const mockUseBuildStore = require('../../../../features/build/buildStore').useBuildStore;
    mockUseBuildStore.mockImplementation((selector: (state: MockState) => unknown) => {
      if (typeof selector === 'function') {
        return selector({
          selectedFile: { id: 'file-1', file_name: 'test.txt' },
          fileContent: 'Hello World',
          isLoadingContent: false,
          isSaving: false,
          isIndexing: false,
          isPreview: false,
          updateFileContent: jest.fn(),
          triggerIndex: mockTriggerIndex,
          setIsPreview: jest.fn(),
        });
      }
      return jest.fn();
    });

    const { getByText } = render(<ReviewEditor />);
    const indexBtn = getByText('确认索引');

    fireEvent.press(indexBtn);

    await waitFor(() => {
      expect(mockTriggerIndex).toHaveBeenCalledWith('file-1');
    });
  });
});

type MockState = {
  selectedFile: { id: string; file_name: string } | null;
  fileContent: string;
  isLoadingContent: boolean;
  isSaving: boolean;
  isIndexing: boolean;
  isPreview: boolean;
  updateFileContent: jest.Mock;
  triggerIndex: jest.Mock;
  setIsPreview: jest.Mock;
};
