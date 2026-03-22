import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from './index';

describe('Badge', () => {
  it('renders children', () => {
    render(<Badge>New</Badge>);
    expect(screen.getByText('New')).toBeInTheDocument();
  });

  it('renders as span element', () => {
    render(<Badge>Label</Badge>);
    expect(screen.getByText('Label')).toBeInstanceOf(HTMLSpanElement);
  });

  it('applies badge class', () => {
    render(<Badge>Text</Badge>);
    expect(screen.getByText('Text')).toHaveClass('badge');
  });

  it('applies variant class', () => {
    render(<Badge variant="accent">Accent</Badge>);
    expect(screen.getByText('Accent')).toHaveClass('badge-accent');
  });

  it('applies size class', () => {
    render(<Badge size="sm">Small</Badge>);
    expect(screen.getByText('Small')).toHaveClass('badge-sm');
  });

  it('merges custom className', () => {
    render(<Badge className="custom-badge">Custom</Badge>);
    expect(screen.getByText('Custom')).toHaveClass('custom-badge');
  });
});
