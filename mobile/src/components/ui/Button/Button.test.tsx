/**
 * Button Component Tests
 */

import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { Text, View } from 'react-native';
import { Button } from './Button';

// Simple mock icon components
const MockSearchIcon = ({ size }: { size: number }) => (
  <View testID="search-icon" />
);
const MockArrowIcon = ({ size }: { size: number }) => (
  <View testID="arrow-icon" />
);

describe('Button Component', () => {
  describe('Variant Styles', () => {
    it('should render primary variant correctly', () => {
      render(<Button variant="primary">Primary Button</Button>);

      const button = screen.getByText('Primary Button');
      expect(button).toBeTruthy();
    });

    it('should render secondary variant correctly', () => {
      render(<Button variant="secondary">Secondary Button</Button>);

      const button = screen.getByText('Secondary Button');
      expect(button).toBeTruthy();
    });

    it('should render ghost variant correctly', () => {
      render(<Button variant="ghost">Ghost Button</Button>);

      const button = screen.getByText('Ghost Button');
      expect(button).toBeTruthy();
    });

    it('should render danger variant correctly', () => {
      render(<Button variant="danger">Danger Button</Button>);

      const button = screen.getByText('Danger Button');
      expect(button).toBeTruthy();
    });
  });

  describe('Size Styles', () => {
    it('should render small size correctly', () => {
      render(<Button size="sm">Small Button</Button>);

      const button = screen.getByText('Small Button');
      expect(button).toBeTruthy();
    });

    it('should render medium size by default', () => {
      render(<Button>Medium Button</Button>);

      const button = screen.getByText('Medium Button');
      expect(button).toBeTruthy();
    });

    it('should render large size correctly', () => {
      render(<Button size="lg">Large Button</Button>);

      const button = screen.getByText('Large Button');
      expect(button).toBeTruthy();
    });
  });

  describe('Disabled State', () => {
    it('should render disabled state correctly', () => {
      render(<Button disabled>Disabled Button</Button>);

      const button = screen.getByText('Disabled Button');
      expect(button).toBeTruthy();
    });

    it('should render disabled primary variant', () => {
      render(<Button variant="primary" disabled>Disabled Primary</Button>);

      const button = screen.getByText('Disabled Primary');
      expect(button).toBeTruthy();
    });
  });

  describe('Loading State', () => {
    it('should render loading state', () => {
      render(<Button isLoading>Loading Button</Button>);

      // Should show ActivityIndicator when loading
      // The button should still be rendered
      expect(screen.toJSON()).toBeTruthy();
    });

    it('should render loading text when provided', () => {
      render(
        <Button isLoading loadingText="Submitting...">
          Submit
        </Button>
      );

      const loadingText = screen.getByText('Submitting...');
      expect(loadingText).toBeTruthy();
    });
  });

  describe('Icon Support', () => {
    it('should render left icon when provided', () => {
      render(
        <Button leftIcon={MockSearchIcon} iconSize={20}>
          Search
        </Button>
      );

      expect(screen.getByText('Search')).toBeTruthy();
      expect(screen.getByTestId('search-icon')).toBeTruthy();
    });

    it('should render right icon when provided', () => {
      render(
        <Button rightIcon={MockArrowIcon} iconSize={20}>
          Next
        </Button>
      );

      expect(screen.getByText('Next')).toBeTruthy();
      expect(screen.getByTestId('arrow-icon')).toBeTruthy();
    });
  });

  describe('Full Width', () => {
    it('should render full width button', () => {
      render(<Button fullWidth>Full Width Button</Button>);

      const button = screen.getByText('Full Width Button');
      expect(button).toBeTruthy();
    });
  });

  describe('Children', () => {
    it('should render string children', () => {
      render(<Button>Click Me</Button>);

      expect(screen.getByText('Click Me')).toBeTruthy();
    });

    it('should render multiple children', () => {
      render(
        <Button>
          <Text>Child 1</Text>
          <Text>Child 2</Text>
        </Button>
      );

      expect(screen.getByText('Child 1')).toBeTruthy();
      expect(screen.getByText('Child 2')).toBeTruthy();
    });
  });
});
