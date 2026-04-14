// mobile/src/screens/__tests__/HomeScreen.test.tsx
import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import { HomeScreen } from '../HomeScreen';
import * as dialogApi from '../../api/dialog';

jest.mock('../../api/dialog');

const mockDialogs: dialogApi.Dialog[] = [
  { id: '1', title: 'Dialog 1', updatedAt: new Date().toISOString() },
  { id: '2', title: 'Dialog 2', updatedAt: new Date().toISOString() },
];

function renderWithNavigation(ui: React.ReactElement) {
  return render(<NavigationContainer>{ui}</NavigationContainer>);
}

describe('HomeScreen', () => {
  beforeEach(() => {
    (dialogApi.listDialogs as jest.Mock).mockResolvedValue(mockDialogs);
  });

  it('should render HeroBanner', async () => {
    const { getByText } = renderWithNavigation(<HomeScreen />);
    await waitFor(() => {
      expect(getByText('CampusMind')).toBeTruthy();
    });
  });

  it('should render FeatureGrid', async () => {
    const { getByText } = renderWithNavigation(<HomeScreen />);
    await waitFor(() => {
      expect(getByText('快捷入口')).toBeTruthy();
    });
  });

  it('should render HistoryList with dialogs', async () => {
    const { getByText } = renderWithNavigation(<HomeScreen />);
    await waitFor(() => {
      expect(getByText('Dialog 1')).toBeTruthy();
      expect(getByText('Dialog 2')).toBeTruthy();
    });
  });
});
