import React from 'react';
import { render } from '@testing-library/react-native';
import { StatsGrid } from '../StatsGrid';

jest.mock('../../profileStore', () => ({
  useProfileStore: () => ({
    stats: {
      conversation_count: 12,
      message_count: 156,
      knowledge_base_count: 3,
      join_date: '2024-01-01',
    },
    user: null,
  }),
}));

describe('StatsGrid', () => {
  it('should render stats correctly', () => {
    const { getByText } = render(<StatsGrid />);

    expect(getByText('12')).toBeTruthy();
    expect(getByText('156')).toBeTruthy();
    expect(getByText('3')).toBeTruthy();
  });

  it('should render stat labels', () => {
    const { getByText } = render(<StatsGrid />);

    expect(getByText('对话数')).toBeTruthy();
    expect(getByText('消息数')).toBeTruthy();
    expect(getByText('知识库数')).toBeTruthy();
  });
});
