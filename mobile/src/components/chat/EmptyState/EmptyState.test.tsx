/**
 * EmptyState Component Tests
 */

import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { EmptyState } from './EmptyState';

describe('EmptyState Component', () => {
  describe('Rendering', () => {
    it('should render the component without crashing', () => {
      render(<EmptyState />);

      expect(screen.toJSON()).toBeTruthy();
    });

    it('should render the assistant avatar', () => {
      render(<EmptyState />);

      expect(screen.getByTestId('empty-state-avatar')).toBeTruthy();
    });

    it('should render the title "CampusMind"', () => {
      render(<EmptyState />);

      expect(screen.getByTestId('empty-state-title')).toBeTruthy();
      expect(screen.getByText('CampusMind')).toBeTruthy();
    });

    it('should render the subtitle "你的智能校园助手"', () => {
      render(<EmptyState />);

      expect(screen.getByTestId('empty-state-subtitle')).toBeTruthy();
      expect(screen.getByText('你的智能校园助手')).toBeTruthy();
    });
  });

  describe('Feature List', () => {
    it('should render all feature items', () => {
      render(<EmptyState />);

      expect(screen.getByText('查询成绩和课表')).toBeTruthy();
      expect(screen.getByText('了解校园通知和活动')).toBeTruthy();
      expect(screen.getByText('获取选课和教务信息')).toBeTruthy();
    });

    it('should render three feature items', () => {
      render(<EmptyState />);

      const features = screen.getAllByText(/查询成绩|了解校园|获取选课/);
      expect(features).toHaveLength(3);
    });
  });

  describe('Visual Elements', () => {
    it('should render bullet points for features', () => {
      render(<EmptyState />);

      const bullets = screen.getAllByText('•');
      expect(bullets).toHaveLength(3);
    });
  });
});
