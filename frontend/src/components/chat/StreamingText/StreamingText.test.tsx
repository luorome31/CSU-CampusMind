import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StreamingText } from './index';

describe('StreamingText', () => {
  it('renders text content', () => {
    render(<StreamingText text="Hello world" isStreaming={false} />);
    expect(screen.getByText('Hello world')).toBeInTheDocument();
  });

  it('renders streaming cursor when isStreaming is true', () => {
    render(<StreamingText text="Loading..." isStreaming={true} />);
    const container = screen.getByText('Loading...');
    expect(container.querySelector('.streaming-cursor')).toBeInTheDocument();
  });

  it('does not render cursor when not streaming', () => {
    render(<StreamingText text="Done" isStreaming={false} />);
    const container = screen.getByText('Done');
    expect(container.querySelector('.streaming-cursor')).not.toBeInTheDocument();
  });

  it('updates displayed text when prop changes', () => {
    const { rerender } = render(<StreamingText text="First" isStreaming={false} />);
    expect(screen.getByText('First')).toBeInTheDocument();

    rerender(<StreamingText text="Second" isStreaming={false} />);
    expect(screen.getByText('Second')).toBeInTheDocument();
  });
});
