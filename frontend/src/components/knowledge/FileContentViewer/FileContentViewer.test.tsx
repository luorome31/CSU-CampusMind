import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FileContentViewer } from './FileContentViewer';

describe('FileContentViewer', () => {
  const markdownContent = '# Hello\n\nThis is **bold** and `code`.';

  it('renders markdown content', () => {
    render(<FileContentViewer content={markdownContent} />);
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Hello');
    expect(screen.getByText('bold')).toBeInTheDocument();
    expect(screen.getByText('code')).toBeInTheDocument();
  });

  it('renders read-only badge', () => {
    render(<FileContentViewer content={markdownContent} />);
    expect(screen.getByText('只读')).toBeInTheDocument();
  });

  it('handles empty content', () => {
    render(<FileContentViewer content="" />);
    expect(screen.getByText('暂无内容')).toBeInTheDocument();
  });
});
