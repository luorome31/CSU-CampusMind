import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { FileContentViewer } from '../FileContentViewer';

// Mock react-native-markdown-display
jest.mock('react-native-markdown-display', () => {
  const { Text } = require('react-native');
  return {
    __esModule: true,
    default: ({ children }: { children: string }) => (
      <Text testID="markdown-content">{children}</Text>
    ),
  };
});

describe('FileContentViewer', () => {
  it('should render empty state when no content', () => {
    const { getByText } = render(
      <FileContentViewer content="" />
    );
    expect(getByText('暂无内容')).toBeTruthy();
  });

  it('should render markdown content', () => {
    render(
      <FileContentViewer content="# Hello World" />
    );
    expect(screen.getByTestId('markdown-content')).toBeTruthy();
  });

  it('should render filename if provided', () => {
    const { getByText } = render(
      <FileContentViewer content="test" fileName="test.txt" />
    );
    expect(getByText('test.txt')).toBeTruthy();
  });

  it('should render markdown with proper content', () => {
    render(
      <FileContentViewer content="## Test Header\nSome content here" />
    );
    expect(screen.getByTestId('markdown-content')).toBeTruthy();
  });
});
