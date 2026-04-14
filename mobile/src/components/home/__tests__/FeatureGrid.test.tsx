// mobile/src/components/home/__tests__/FeatureGrid.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import { FeatureGrid } from '../FeatureGrid';

const mockNavigate = jest.fn();

jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({ navigate: mockNavigate }),
}));

describe('FeatureGrid', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('should render 4 feature tiles', () => {
    const { getByText } = render(<FeatureGrid />);
    expect(getByText('新建对话')).toBeTruthy();
    expect(getByText('知识库')).toBeTruthy();
    expect(getByText('知识构建')).toBeTruthy();
    expect(getByText('个人中心')).toBeTruthy();
  });

  it('should navigate to ChatsTab when pressing 新建对话', () => {
    const { getByText } = render(<FeatureGrid />);
    fireEvent.press(getByText('新建对话'));
    expect(mockNavigate).toHaveBeenCalledWith('ChatsTab');
  });
});
