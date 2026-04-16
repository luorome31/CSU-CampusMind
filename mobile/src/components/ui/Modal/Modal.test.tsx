/**
 * Modal Component Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { Text } from '@/components/ui/StyledText';
import { Modal } from './Modal';

describe('Modal Component', () => {
  describe('Visibility', () => {
    it('should not render when visible is false', () => {
      render(
        <Modal visible={false} onClose={jest.fn()} title="Test Modal">
          <React.Fragment>Content</React.Fragment>
        </Modal>
      );

      // Modal should not be visible
      expect(screen.queryByText('Test Modal')).toBeNull();
    });

    it('should render when visible is true', () => {
      render(
        <Modal visible={true} onClose={jest.fn()} title="Test Modal">
          <React.Fragment>Content</React.Fragment>
        </Modal>
      );

      expect(screen.getByText('Test Modal')).toBeTruthy();
    });
  });

  describe('Title', () => {
    it('should display the title correctly', () => {
      render(
        <Modal visible={true} onClose={jest.fn()} title="Modal Title">
          <React.Fragment>Content</React.Fragment>
        </Modal>
      );

      expect(screen.getByText('Modal Title')).toBeTruthy();
    });
  });

  describe('onClose Callback', () => {
    it('should call onClose when close button is pressed', () => {
      const mockOnClose = jest.fn();

      render(
        <Modal visible={true} onClose={mockOnClose} title="Test Modal">
          <React.Fragment>Content</React.Fragment>
        </Modal>
      );

      const closeButton = screen.getByRole('button', { name: /close/i });
      fireEvent.press(closeButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should call onClose when backdrop is pressed', () => {
      const mockOnClose = jest.fn();

      render(
        <Modal visible={true} onClose={mockOnClose} title="Test Modal">
          <React.Fragment>Content</React.Fragment>
        </Modal>
      );

      // Find and press the backdrop (the overlay behind the modal)
      const backdrop = screen.getByTestId('modal-backdrop');
      fireEvent.press(backdrop);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Children', () => {
    it('should render children content', () => {
      render(
        <Modal visible={true} onClose={jest.fn()} title="Test Modal">
          <Text>Children Content</Text>
        </Modal>
      );

      expect(screen.getByText('Children Content')).toBeTruthy();
    });
  });
});
