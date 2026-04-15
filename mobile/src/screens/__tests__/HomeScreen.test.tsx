// mobile/src/screens/__tests__/HomeScreen.test.tsx
import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import { HomeScreen } from '../HomeScreen';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Mock API
jest.mock('../../api/dialog', () => ({
  listDialogs: jest.fn().mockResolvedValue([
    { id: '1', title: 'Dialog 1', updated_at: '2024-01-01T00:00:00Z' },
    { id: '2', title: 'Dialog 2', updated_at: '2024-01-01T00:00:00Z' },
  ]),
}));

// Mock sub-components to isolate Screen test
jest.mock('../../components/home', () => ({
  HeroBanner: () => {
    const { Text } = require('react-native');
    return <Text>HeroBanner</Text>;
  },
  FeatureGrid: () => {
    const { Text } = require('react-native');
    return <Text>FeatureGrid</Text>;
  },
  HistoryList: ({ dialogs }: any) => {
    const { Text, View } = require('react-native');
    return (
      <View>
        <Text>最近对话</Text>
        {dialogs.map((d: any) => <Text key={d.id}>{d.title}</Text>)}
      </View>
    );
  },
}));

// Mock safe area insets
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaView: ({ children }: any) => {
    const { View } = require('react-native');
    return <View>{children}</View>;
  },
  useSafeAreaInsets: () => ({ top: 0, bottom: 0, left: 0, right: 0 }),
}));

describe('HomeScreen', () => {
  it('should render header and components correctly', async () => {
    const { getByText } = render(<HomeScreen />);

    expect(getByText('首页')).toBeTruthy();
    expect(getByText('HeroBanner')).toBeTruthy();
    expect(getByText('FeatureGrid')).toBeTruthy();

    await waitFor(() => {
      expect(getByText('最近对话')).toBeTruthy();
      expect(getByText('Dialog 1')).toBeTruthy();
    });
  });
});
