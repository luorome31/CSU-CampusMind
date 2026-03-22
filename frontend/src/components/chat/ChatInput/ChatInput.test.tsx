import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInput } from './index';

describe('ChatInput', () => {
  it('renders input field', () => {
    render(<ChatInput onSend={vi.fn()} />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('renders send button', () => {
    render(<ChatInput onSend={vi.fn()} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('displays placeholder text when not disabled', () => {
    render(<ChatInput onSend={vi.fn()} />);
    expect(screen.getByPlaceholderText('输入消息...')).toBeInTheDocument();
  });

  it('displays waiting placeholder when disabled', () => {
    render(<ChatInput onSend={vi.fn()} disabled />);
    expect(screen.getByPlaceholderText('等待回复中...')).toBeInTheDocument();
  });

  it('calls onSend with trimmed value when form is submitted', () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: '  Hello world  ' } });

    const form = screen.getByRole('textbox').closest('form');
    fireEvent.submit(form!);

    expect(onSend).toHaveBeenCalledWith('Hello world');
  });

  it('does not call onSend for empty/whitespace-only input', () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: '   ' } });

    const form = screen.getByRole('textbox').closest('form');
    fireEvent.submit(form!);

    expect(onSend).not.toHaveBeenCalled();
  });

  it('clears input after successful submission', () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Test message' } });

    const form = screen.getByRole('textbox').closest('form');
    fireEvent.submit(form!);

    expect((input as HTMLInputElement).value).toBe('');
  });

  it('disables input when disabled prop is true', () => {
    render(<ChatInput onSend={vi.fn()} disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('disables send button when disabled', () => {
    render(<ChatInput onSend={vi.fn()} disabled />);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('disables send button when input is empty', () => {
    render(<ChatInput onSend={vi.fn()} />);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('enables send button when input has content', () => {
    render(<ChatInput onSend={vi.fn()} />);
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Hello' } });
    expect(screen.getByRole('button')).not.toBeDisabled();
  });

  it('prevents submission when disabled', () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} disabled />);

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Test' } });

    const form = screen.getByRole('textbox').closest('form');
    fireEvent.submit(form!);

    expect(onSend).not.toHaveBeenCalled();
  });
});
