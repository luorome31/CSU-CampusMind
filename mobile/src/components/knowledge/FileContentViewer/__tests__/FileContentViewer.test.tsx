import React from 'react';
import { render } from '@testing-library/react-native';
import { FileContentViewer } from '../FileContentViewer';

describe('FileContentViewer', () => {
  it('should render empty state when no content', () => {
    const { getByText } = render(
      <FileContentViewer content="" />
    );
    expect(getByText('暂无内容')).toBeTruthy();
  });

  it('should render content', () => {
    const { getByText } = render(
      <FileContentViewer content="# Hello World" />
    );
    expect(getByText('# Hello World')).toBeTruthy();
  });

  it('should render filename if provided', () => {
    const { getByText } = render(
      <FileContentViewer content="test" fileName="test.txt" />
    );
    expect(getByText('test.txt')).toBeTruthy();
  });
});
