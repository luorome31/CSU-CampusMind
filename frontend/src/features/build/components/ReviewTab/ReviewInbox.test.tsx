import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ReviewInbox } from './ReviewInbox';

describe('ReviewInbox', () => {
  it('should render empty state when no files', () => {
    render(<ReviewInbox />);
    expect(screen.getByText(/暂无待审核文件/)).toBeInTheDocument();
  });
});
