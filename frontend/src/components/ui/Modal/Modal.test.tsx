import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Modal } from './index';

describe('Modal', () => {
  it('renders without error when isOpen=true', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        Modal content
      </Modal>
    );
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  });

  it('renders without error when isOpen=false', () => {
    render(
      <Modal isOpen={false} onClose={() => {}}>
        Modal content
      </Modal>
    );
    expect(screen.queryByText('Modal content')).not.toBeInTheDocument();
  });

  it('renders title when provided', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} title="Test Title">
        Content
      </Modal>
    );
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('renders close button', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        Content
      </Modal>
    );
    expect(screen.getByRole('button', { name: 'Close modal' })).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose}>
        Content
      </Modal>
    );
    screen.getByRole('button', { name: 'Close modal' }).click();
    expect(onClose).toHaveBeenCalledOnce();
  });
});
