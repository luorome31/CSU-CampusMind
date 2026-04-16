/**
 * Card Component Tests
 */

import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { View } from 'react-native';
import { Text } from '@/components/ui/StyledText';
import { Card } from './Card';

describe('Card Component', () => {
  describe('Variant Styles', () => {
    it('should render default variant correctly', () => {
      render(<Card variant="default"><Text>Default Card</Text></Card>);

      const card = screen.getByText('Default Card');
      expect(card).toBeTruthy();
    });

    it('should render elevated variant correctly', () => {
      render(<Card variant="elevated"><Text>Elevated Card</Text></Card>);

      const card = screen.getByText('Elevated Card');
      expect(card).toBeTruthy();
    });

    it('should render glass variant correctly', () => {
      render(<Card variant="glass"><Text>Glass Card</Text></Card>);

      const card = screen.getByText('Glass Card');
      expect(card).toBeTruthy();
    });
  });

  describe('Padding Styles', () => {
    it('should render small padding correctly', () => {
      render(<Card padding="sm"><Text>Small Padding Card</Text></Card>);

      const card = screen.getByText('Small Padding Card');
      expect(card).toBeTruthy();
    });

    it('should render medium padding by default', () => {
      render(<Card><Text>Medium Padding Card</Text></Card>);

      const card = screen.getByText('Medium Padding Card');
      expect(card).toBeTruthy();
    });

    it('should render large padding correctly', () => {
      render(<Card padding="lg"><Text>Large Padding Card</Text></Card>);

      const card = screen.getByText('Large Padding Card');
      expect(card).toBeTruthy();
    });
  });

  describe('Children', () => {
    it('should render Text children', () => {
      render(<Card><Text>Simple Text</Text></Card>);

      expect(screen.getByText('Simple Text')).toBeTruthy();
    });

    it('should render multiple children', () => {
      render(
        <Card>
          <Text>Child 1</Text>
          <Text>Child 2</Text>
        </Card>
      );

      expect(screen.getByText('Child 1')).toBeTruthy();
      expect(screen.getByText('Child 2')).toBeTruthy();
    });

    it('should render nested components', () => {
      render(
        <Card>
          <View testID="nested-view">
            <Text>Nested Content</Text>
          </View>
        </Card>
      );

      expect(screen.getByText('Nested Content')).toBeTruthy();
      expect(screen.getByTestId('nested-view')).toBeTruthy();
    });
  });
});
