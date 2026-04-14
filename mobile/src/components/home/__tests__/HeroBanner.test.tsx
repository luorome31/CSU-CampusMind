// mobile/src/components/home/__tests__/HeroBanner.test.tsx
import React from 'react';
import { render } from '@testing-library/react-native';
import { HeroBanner } from '../HeroBanner';

describe('HeroBanner', () => {
  it('should render brand title', () => {
    const { getByText } = render(<HeroBanner />);
    expect(getByText('CampusMind')).toBeTruthy();
  });

  it('should render subtitle', () => {
    const { getByText } = render(<HeroBanner />);
    expect(getByText('你的智能校园助手')).toBeTruthy();
  });
});
