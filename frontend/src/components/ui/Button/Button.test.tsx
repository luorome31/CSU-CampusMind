import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Button } from './index';
import { Plus } from 'lucide-react';

describe('Button', () => {
  it('renders children text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('renders with correct default variant', () => {
    render(<Button>Submit</Button>);
    const button = screen.getByRole('button', { name: 'Submit' });
    expect(button).toHaveClass('btn-primary');
  });

  it('applies custom variant class', () => {
    render(<Button variant="ghost">Ghost</Button>);
    const button = screen.getByRole('button', { name: 'Ghost' });
    expect(button).toHaveClass('btn-ghost');
  });

  it('applies size class for non-default sizes', () => {
    render(<Button size="sm">Small</Button>);
    const button = screen.getByRole('button', { name: 'Small' });
    expect(button).toHaveClass('btn-sm');
  });

  it('applies fullWidth class when fullWidth is true', () => {
    render(<Button fullWidth>Wide</Button>);
    const button = screen.getByRole('button', { name: 'Wide' });
    expect(button).toHaveClass('btn-full');
  });

  it('renders left icon when provided', () => {
    render(<Button leftIcon={Plus}>With Icon</Button>);
    const button = screen.getByRole('button', { name: 'With Icon' });
    const icon = button.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('renders right icon when provided', () => {
    render(<Button rightIcon={Plus}>With Icon</Button>);
    const button = screen.getByRole('button', { name: 'With Icon' });
    // Icons are rendered as siblings, so button should have an svg
    expect(button.querySelector('svg')).toBeInTheDocument();
  });

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    const button = screen.getByRole('button', { name: 'Disabled' });
    expect(button).toBeDisabled();
  });

  it('disables button when isLoading prop is true', () => {
    render(<Button isLoading>Loading</Button>);
    const button = screen.getByRole('button', { name: 'Loading' });
    expect(button).toBeDisabled();
  });

  it('applies loading class when isLoading is true', () => {
    render(<Button isLoading>Loading</Button>);
    const button = screen.getByRole('button', { name: 'Loading' });
    expect(button).toHaveClass('btn-loading');
  });

  it('forwards ref to the button element', () => {
    let ref: HTMLButtonElement | null = null;
    render(
      <Button ref={(el) => { ref = el; }}>
        Ref Test
      </Button>
    );
    expect(ref).toBeInstanceOf(HTMLButtonElement);
  });

  it('passes through additional props', () => {
    render(<Button type="submit" aria-label="Submit form">Submit</Button>);
    const button = screen.getByRole('button', { name: 'Submit form' });
    expect(button).toHaveAttribute('type', 'submit');
  });
});
