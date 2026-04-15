// mobile/src/components/home/__tests__/FeatureGrid.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { FeatureGrid } from '../FeatureGrid';

const mockNavigate = jest.fn();

jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({ navigate: mockNavigate }),
}));

describe('FeatureGrid', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('should render 2 feature tiles', () => {
    const { getByText, queryByText } = render(<FeatureGrid />);
    expect(getByText('知识库')).toBeTruthy();
    expect(getByText('知识构建')).toBeTruthy();
    
    // "新建对话" moved to HeroBanner, "个人中心" might be removed or moved
    expect(queryByText('新建对话')).toBeNull();
  });

  it('should navigate to KnowledgeTab when pressing 知识库', () => {
    const { getByText } = render(<FeatureGrid />);
    fireEvent.press(getByText('知识库'));
    expect(mockNavigate).toHaveBeenCalledWith('KnowledgeTab');
  });
});
