import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Input } from './index';
import { Mail } from 'lucide-react';

describe('Input', () => {
  it('renders an input element', () => {
    render(<Input />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('renders with label when provided', () => {
    render(<Input label="Email" />);
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
  });

  it('associates label with input via htmlFor', () => {
    render(<Input label="Username" />);
    const input = screen.getByLabelText('Username');
    const label = screen.getByText('Username');
    expect(label).toHaveAttribute('for', input.id);
  });

  it('displays error message when provided', () => {
    render(<Input error="This field is required" />);
    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  it('applies error class to input when error is provided', () => {
    render(<Input error="Error" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('input-error');
  });

  it('displays hint text when provided and no error', () => {
    render(<Input hint="Enter your email" />);
    expect(screen.getByText('Enter your email')).toBeInTheDocument();
  });

  it('does not display hint when error is present', () => {
    render(<Input error="Error" hint="Hint" />);
    expect(screen.queryByText('Hint')).not.toBeInTheDocument();
  });

  it('renders left icon when provided', () => {
    render(<Input leftIcon={Mail} />);
    const input = screen.getByRole('textbox');
    const icon = input.previousElementSibling;
    expect(icon?.tagName.toLowerCase()).toBe('svg');
  });

  it('renders right icon when provided', () => {
    render(<Input rightIcon={Mail} />);
    const input = screen.getByRole('textbox');
    const icon = input.nextElementSibling;
    expect(icon?.tagName.toLowerCase()).toBe('svg');
  });

  it('applies input-with-left-icon class when leftIcon is provided', () => {
    render(<Input leftIcon={Mail} />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('input-with-left-icon');
  });

  it('applies size class for non-default sizes', () => {
    render(<Input size="sm" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('input-sm');
  });

  it('forwards ref to the input element', () => {
    let ref: HTMLInputElement | null = null;
    render(
      <Input ref={(el) => { ref = el; }} />
    );
    expect(ref).toBeInstanceOf(HTMLInputElement);
  });

  it('passes through input props', () => {
    render(<Input type="email" placeholder="you@example.com" autoComplete="email" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('type', 'email');
    expect(input).toHaveAttribute('placeholder', 'you@example.com');
    expect(input).toHaveAttribute('autocomplete', 'email');
  });

  it('uses custom id when provided', () => {
    render(<Input id="custom-id" label="Test" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('id', 'custom-id');
  });

  it('generates unique id when not provided', () => {
    render(<Input label="Test" />);
    const input = screen.getByRole('textbox');
    expect(input.id).toMatch(/^input-/);
  });
});
