import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Chip } from './index';
import { Mail } from 'lucide-react';

describe('Chip', () => {
  it('renders children', () => {
    render(<Chip>Label</Chip>);
    expect(screen.getByRole('button', { name: 'Label' })).toBeInTheDocument();
  });

  it('renders as button element', () => {
    render(<Chip>Clickable</Chip>);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('applies chip class', () => {
    render(<Chip>Chip</Chip>);
    expect(screen.getByRole('button')).toHaveClass('chip');
  });

  it('applies variant class', () => {
    render(<Chip variant="active">Active</Chip>);
    expect(screen.getByRole('button')).toHaveClass('chip-active');
  });

  it('applies size class for non-default sizes', () => {
    render(<Chip size="sm">Small</Chip>);
    expect(screen.getByRole('button')).toHaveClass('chip-sm');
  });

  it('renders icon when provided', () => {
    render(<Chip icon={Mail}>Email</Chip>);
    const button = screen.getByRole('button', { name: 'Email' });
    expect(button.querySelector('svg')).toBeInTheDocument();
  });

  it('merges custom className', () => {
    render(<Chip className="custom-chip">Custom</Chip>);
    expect(screen.getByRole('button')).toHaveClass('custom-chip');
  });

  it('passes through button props', () => {
    render(<Chip type="submit" aria-label="Select option">Option</Chip>);
    const button = screen.getByRole('button', { name: 'Select option' });
    expect(button).toHaveAttribute('type', 'submit');
  });
});
