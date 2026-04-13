import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { LoginScreen } from '../LoginScreen';
import { useAuthStore } from '../authStore';

// Mock the auth store
jest.mock('../authStore', () => ({
  useAuthStore: jest.fn(),
}));

const mockLogin = jest.fn();
const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

describe('LoginScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuthStore.mockReturnValue({
      login: mockLogin,
      isLoading: false,
      isAuthenticated: false,
      user: null,
      token: null,
      sessionId: null,
      initAuth: jest.fn(),
      logout: jest.fn(),
    });
  });

  it('should render login form', () => {
    const { getByPlaceholderText, getByText } = render(<LoginScreen />);

    expect(getByPlaceholderText('请输入学号')).toBeTruthy();
    expect(getByPlaceholderText('请输入密码')).toBeTruthy();
    expect(getByText('登录')).toBeTruthy();
  });

  it('should update username and password inputs', () => {
    const { getByPlaceholderText } = render(<LoginScreen />);

    const usernameInput = getByPlaceholderText('请输入学号');
    const passwordInput = getByPlaceholderText('请输入密码');

    fireEvent.changeText(usernameInput, 'student123');
    fireEvent.changeText(passwordInput, 'password123');

    expect(usernameInput.props.value).toBe('student123');
    expect(passwordInput.props.value).toBe('password123');
  });

  it('should call login on submit', async () => {
    mockLogin.mockResolvedValue(undefined);

    const { getByPlaceholderText, getByText } = render(<LoginScreen />);

    fireEvent.changeText(getByPlaceholderText('请输入学号'), 'student123');
    fireEvent.changeText(getByPlaceholderText('请输入密码'), 'password123');
    fireEvent.press(getByText('登录'));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('student123', 'password123');
    });
  });

  it('should show error on login failure', async () => {
    mockLogin.mockRejectedValue(new Error('Invalid'));

    const { getByPlaceholderText, getByText, findByText } = render(<LoginScreen />);

    fireEvent.changeText(getByPlaceholderText('请输入学号'), 'student123');
    fireEvent.changeText(getByPlaceholderText('请输入密码'), 'wrongpassword');
    fireEvent.press(getByText('登录'));

    const errorText = await findByText('登录失败，请检查学号和密码');
    expect(errorText).toBeTruthy();
  });

  it('should show loading indicator when isLoading is true', () => {
    mockUseAuthStore.mockReturnValue({
      login: mockLogin,
      isLoading: true,
      isAuthenticated: false,
      user: null,
      token: null,
      sessionId: null,
      initAuth: jest.fn(),
      logout: jest.fn(),
    });

    const { getByTestId } = render(<LoginScreen />);
    // ActivityIndicator should be present
    expect(getByTestId('activity-indicator')).toBeTruthy();
  });

  it('should toggle password visibility', () => {
    const { getByPlaceholderText, getByText } = render(<LoginScreen />);

    const toggleButton = getByText('👁️‍🗨️');

    fireEvent.press(toggleButton);
    // After toggle, should show different icon
    expect(getByText('👁️')).toBeTruthy();
  });
});
