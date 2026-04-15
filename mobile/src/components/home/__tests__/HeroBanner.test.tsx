// mobile/src/components/home/__tests__/HeroBanner.test.tsx
import React from 'react';
import { render } from '@testing-library/react-native';
import { HeroBanner } from '../HeroBanner';

// Mock navigation
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({ navigate: jest.fn() }),
}));

// Mock Card component
jest.mock('../../ui/Card', () => ({
  Card: ({ children, style }: any) => {
    const { View } = require('react-native');
    return <View style={style}>{children}</View>;
  },
}));

describe('HeroBanner', () => {
  it('should render brand title', () => {
    const { getByText } = render(<HeroBanner />);
    expect(getByText('CampusMind')).toBeTruthy();
  });

  it('should render correct subtitle', () => {
    const { getByText } = render(<HeroBanner />);
    expect(getByText(/基于 RAG 与 Tool-calling 的智能校园助手/)).toBeTruthy();
  });

  it('should render "新建对话" button', () => {
    const { getByText } = render(<HeroBanner />);
    expect(getByText('新建对话')).toBeTruthy();
  });
});
