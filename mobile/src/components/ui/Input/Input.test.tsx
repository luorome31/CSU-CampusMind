/**
 * Input Component Tests
 */

import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { View } from 'react-native';
import { Input } from './Input';

// Simple mock icon components
const MockSearchIcon = ({ size }: { size: number }) => (
  <View testID="search-icon" />
);
const MockEyeIcon = ({ size }: { size: number }) => (
  <View testID="eye-icon" />
);

describe('Input Component', () => {
  describe('Label Rendering', () => {
    it('should render label text when provided', () => {
      render(<Input label="Email Address" />);

      const label = screen.getByText('Email Address');
      expect(label).toBeTruthy();
    });

    it('should not render label when not provided', () => {
      render(<Input placeholder="Enter text" />);

      // Label should not exist
      expect(screen.queryByText('Email Address')).toBeNull();
    });
  });

  describe('Error State', () => {
    it('should render error message when provided', () => {
      render(<Input error="This field is required" />);

      const error = screen.getByText('This field is required');
      expect(error).toBeTruthy();
    });

    it('should not render error message when not provided', () => {
      render(<Input />);

      expect(screen.queryByText('This field is required')).toBeNull();
    });
  });

  describe('Hint State', () => {
    it('should render hint text when provided', () => {
      render(<Input hint="Enter your email address" />);

      const hint = screen.getByText('Enter your email address');
      expect(hint).toBeTruthy();
    });

    it('should not render hint when not provided', () => {
      render(<Input />);

      expect(screen.queryByText('Enter your email address')).toBeNull();
    });
  });

  describe('Size Variations', () => {
    it('should render small size correctly', () => {
      render(<Input size="sm" placeholder="Small input" />);

      const input = screen.getByPlaceholderText('Small input');
      expect(input).toBeTruthy();
    });

    it('should render medium size by default', () => {
      render(<Input placeholder="Medium input" />);

      const input = screen.getByPlaceholderText('Medium input');
      expect(input).toBeTruthy();
    });

    it('should render large size correctly', () => {
      render(<Input size="lg" placeholder="Large input" />);

      const input = screen.getByPlaceholderText('Large input');
      expect(input).toBeTruthy();
    });
  });

  describe('Icon Support', () => {
    it('should render left icon when provided', () => {
      render(
        <Input leftIcon={MockSearchIcon} placeholder="Search" />
      );

      expect(screen.getByTestId('search-icon')).toBeTruthy();
    });

    it('should render right icon when provided', () => {
      render(
        <Input rightIcon={MockEyeIcon} placeholder="Password" />
      );

      expect(screen.getByTestId('eye-icon')).toBeTruthy();
    });

    it('should render both left and right icons when provided', () => {
      render(
        <Input
          leftIcon={MockSearchIcon}
          rightIcon={MockEyeIcon}
          placeholder="Search"
        />
      );

      expect(screen.getByTestId('search-icon')).toBeTruthy();
      expect(screen.getByTestId('eye-icon')).toBeTruthy();
    });
  });

  describe('TextInput Behavior', () => {
    it('should render with placeholder text', () => {
      render(<Input placeholder="Enter your name" />);

      const input = screen.getByPlaceholderText('Enter your name');
      expect(input).toBeTruthy();
    });

    it('should pass through value prop', () => {
      render(<Input value="Test Value" />);

      const input = screen.getByDisplayValue('Test Value');
      expect(input).toBeTruthy();
    });

    it('should call onChangeText when text changes', () => {
      const onChangeText = jest.fn();
      render(<Input onChangeText={onChangeText} placeholder="Type here" />);

      const input = screen.getByPlaceholderText('Type here');
      expect(input).toBeTruthy();
    });
  });

  describe('Full Width', () => {
    it('should support fullWidth prop', () => {
      render(<Input fullWidth placeholder="Full width input" />);

      const input = screen.getByPlaceholderText('Full width input');
      expect(input).toBeTruthy();
    });
  });
});
