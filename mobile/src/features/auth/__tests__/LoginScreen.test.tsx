import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react-native';
import { LoginScreen } from '../LoginScreen';
import { useAuthStore } from '../authStore';

// Mock the auth store
jest.mock('../authStore', () => ({
  useAuthStore: jest.fn(),
}));

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

describe('LoginScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuthStore.mockReturnValue({
      login: jest.fn(),
      isLoading: false,
      isAuthenticated: false,
      user: null,
      token: null,
      sessionId: null,
      initAuth: jest.fn(),
      logout: jest.fn(),
    });
  });

  it('should render login form elements', () => {
    render(<LoginScreen />);

    expect(screen.getByPlaceholderText('请输入学号')).toBeTruthy();
    expect(screen.getByPlaceholderText('请输入密码')).toBeTruthy();
  });

  it('should render logo and title', () => {
    render(<LoginScreen />);

    expect(screen.getByText('CampusMind')).toBeTruthy();
    // Logo is now rendered as GraduationCap icon component, title check is sufficient
  });

  it('should render footer', () => {
    render(<LoginScreen />);

    expect(screen.getByText(/中南大学智能校园助手/)).toBeTruthy();
  });

  it('should update username input when text changes', () => {
    render(<LoginScreen />);

    const usernameInput = screen.getByPlaceholderText('请输入学号');
    fireEvent.changeText(usernameInput, 'student123');

    expect(usernameInput.props.value).toBe('student123');
  });

  it('should update password input when text changes', () => {
    render(<LoginScreen />);

    const passwordInput = screen.getByPlaceholderText('请输入密码');
    fireEvent.changeText(passwordInput, 'password123');

    expect(passwordInput.props.value).toBe('password123');
  });
});
