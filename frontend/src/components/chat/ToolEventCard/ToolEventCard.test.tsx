import { describe, it, expect } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { ToolEventCard } from './index';
import type { ToolEvent } from '../../../features/chat/chatStore';

describe('ToolEventCard', () => {
  const mockEvent: ToolEvent = {
    id: 'event-1',
    status: 'START',
    title: 'JWC Query',
    message: 'Querying grade data...',
  };

  it('renders event title', () => {
    render(<ToolEventCard event={mockEvent} />);
    expect(screen.getByText('JWC Query')).toBeInTheDocument();
  });

  it('renders status text for START status', () => {
    render(<ToolEventCard event={mockEvent} />);
    expect(screen.getByText('进行中')).toBeInTheDocument();
  });

  it('renders status text for END status', () => {
    const endEvent = { ...mockEvent, status: 'END' as const };
    render(<ToolEventCard event={endEvent} />);
    expect(screen.getByText('完成')).toBeInTheDocument();
  });

  it('renders status text for ERROR status', () => {
    const errorEvent = { ...mockEvent, status: 'ERROR' as const };
    render(<ToolEventCard event={errorEvent} />);
    expect(screen.getByText('错误')).toBeInTheDocument();
  });

  it('collapses details by default', () => {
    render(<ToolEventCard event={mockEvent} />);
    expect(screen.queryByText('Querying grade data...')).not.toBeInTheDocument();
  });

  it('expands to show details when clicked', async () => {
    render(<ToolEventCard event={mockEvent} />);
    const header = screen.getByText('JWC Query').closest('.tool-event-header') as HTMLElement | null;

    await act(async () => {
      header?.click();
    });

    expect(screen.getByText('Querying grade data...')).toBeInTheDocument();
  });

  it('toggles expanded state on multiple clicks', async () => {
    render(<ToolEventCard event={mockEvent} />);
    const header = screen.getByText('JWC Query').closest('.tool-event-header');

    // Expand
    await act(async () => {
      (header as HTMLElement)?.click();
    });
    expect(screen.getByText('Querying grade data...')).toBeInTheDocument();

    // Collapse
    await act(async () => {
      (header as HTMLElement)?.click();
    });
    expect(screen.queryByText('Querying grade data...')).not.toBeInTheDocument();
  });

  it('applies correct class for START status', () => {
    render(<ToolEventCard event={mockEvent} />);
    const card = screen.getByText('JWC Query').closest('.tool-event-card');
    expect(card).toHaveClass('tool-event-start');
  });

  it('applies correct class for END status', () => {
    const endEvent = { ...mockEvent, status: 'END' as const };
    render(<ToolEventCard event={endEvent} />);
    const card = screen.getByText('JWC Query').closest('.tool-event-card');
    expect(card).toHaveClass('tool-event-end');
  });

  it('applies correct class for ERROR status', () => {
    const errorEvent = { ...mockEvent, status: 'ERROR' as const };
    render(<ToolEventCard event={errorEvent} />);
    const card = screen.getByText('JWC Query').closest('.tool-event-card');
    expect(card).toHaveClass('tool-event-error');
  });

  it('renders loading icon for START status', () => {
    render(<ToolEventCard event={mockEvent} />);
    const card = screen.getByText('JWC Query').closest('.tool-event-card');
    expect(card?.querySelector('.tool-icon-loading')).toBeInTheDocument();
  });

  it('renders success icon for END status', () => {
    const endEvent = { ...mockEvent, status: 'END' as const };
    render(<ToolEventCard event={endEvent} />);
    const card = screen.getByText('JWC Query').closest('.tool-event-card');
    expect(card?.querySelector('.tool-icon-success')).toBeInTheDocument();
  });

  it('renders error icon for ERROR status', () => {
    const errorEvent = { ...mockEvent, status: 'ERROR' as const };
    render(<ToolEventCard event={errorEvent} />);
    const card = screen.getByText('JWC Query').closest('.tool-event-card');
    expect(card?.querySelector('.tool-icon-error')).toBeInTheDocument();
  });
});
