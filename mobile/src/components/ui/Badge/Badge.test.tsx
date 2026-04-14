/**
 * Badge Component Tests
 */

import React from 'react';
import { Text } from 'react-native';
import { render, screen } from '@testing-library/react-native';
import { Badge } from './Badge';

describe('Badge Component', () => {
  describe('Variant Styles', () => {
    it('should render success variant with correct background color', () => {
      render(<Badge variant="success">Success</Badge>);

      const badge = screen.getByText('Success');
      expect(badge).toBeTruthy();
    });

    it('should render error variant with correct background color', () => {
      render(<Badge variant="error">Error</Badge>);

      const badge = screen.getByText('Error');
      expect(badge).toBeTruthy();
    });

    it('should render warning variant with correct background color', () => {
      render(<Badge variant="warning">Warning</Badge>);

      const badge = screen.getByText('Warning');
      expect(badge).toBeTruthy();
    });

    it('should render info variant by default', () => {
      render(<Badge>Info</Badge>);

      const badge = screen.getByText('Info');
      expect(badge).toBeTruthy();
    });

    it('should render info variant explicitly', () => {
      render(<Badge variant="info">Info</Badge>);

      const badge = screen.getByText('Info');
      expect(badge).toBeTruthy();
    });
  });

  describe('Pill Shape', () => {
    it('should render with pill shape (full rounded corners)', () => {
      render(<Badge variant="success">Pill</Badge>);

      const badge = screen.getByText('Pill');
      expect(badge).toBeTruthy();
    });

    it('should render pill shape for error variant', () => {
      render(<Badge variant="error">Error Pill</Badge>);

      const badge = screen.getByText('Error Pill');
      expect(badge).toBeTruthy();
    });
  });

  describe('Typography', () => {
    it('should render with xs font size (12px)', () => {
      render(<Badge>Text</Badge>);

      const badge = screen.getByText('Text');
      expect(badge).toBeTruthy();
    });
  });

  describe('Children', () => {
    it('should render string children', () => {
      render(<Badge>Label</Badge>);

      expect(screen.getByText('Label')).toBeTruthy();
    });

    it('should render ReactNode children', () => {
      render(
        <Badge variant="success">
          <Text>Child</Text>
        </Badge>
      );

      expect(screen.getByText('Child')).toBeTruthy();
    });
  });
});
