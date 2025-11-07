import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginPage from './page';
import { useRouter } from 'next/navigation';
import { createClient } from '@/lib/supabase/client';
import { useAuth } from '@/components/providers/auth-provider';

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/lib/supabase/client', () => ({
  createClient: jest.fn(),
}));

jest.mock('@/components/providers/auth-provider', () => ({
  useAuth: jest.fn(),
}));

const mockPush = jest.fn();
const mockSignInWithPassword = jest.fn();
const mockSignInWithOAuth = jest.fn();

// Set up environment variable
process.env.NEXT_PUBLIC_BACKEND_API_URL = 'http://localhost:8000';

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (createClient as jest.Mock).mockReturnValue({
      auth: {
        signInWithPassword: mockSignInWithPassword,
        signInWithOAuth: mockSignInWithOAuth,
      },
    });
    (useAuth as jest.Mock).mockReturnValue({
      session: null,
      loading: false,
    });
  });

  it('should render login form', () => {
    render(<LoginPage />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /google/i })).toBeInTheDocument();
  });

  it('should handle successful email/password login', async () => {
    const user = userEvent.setup();
    const mockData = {
      session: { access_token: 'token' },
    };
    mockSignInWithPassword.mockResolvedValueOnce({ data: mockData, error: null });

    // Mock fetch to return profile exists
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({}),
    });

    render(<LoginPage />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockSignInWithPassword).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('should display error on failed login', async () => {
    const user = userEvent.setup();
    mockSignInWithPassword.mockResolvedValueOnce({
      error: { message: 'Invalid credentials' },
    });

    render(<LoginPage />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'wrongpassword');
    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });

    expect(mockPush).not.toHaveBeenCalled();
  });

  it('should handle Google OAuth login', async () => {
    const user = userEvent.setup();
    mockSignInWithOAuth.mockResolvedValueOnce({ error: null });

    render(<LoginPage />);

    await user.click(screen.getByRole('button', { name: /google/i }));

    await waitFor(() => {
      expect(mockSignInWithOAuth).toHaveBeenCalledWith({
        provider: 'google',
        options: {
          redirectTo: expect.stringMatching(/\/auth\/callback$/),
        },
      });
    });
  });

  it('should display error on Google login failure', async () => {
    const user = userEvent.setup();
    mockSignInWithOAuth.mockResolvedValueOnce({
      error: { message: 'OAuth failed' },
    });

    render(<LoginPage />);

    await user.click(screen.getByRole('button', { name: /google/i }));

    await waitFor(() => {
      expect(screen.getByText(/oauth failed/i)).toBeInTheDocument();
    });
  });

  it('should disable submit button while loading', async () => {
    const user = userEvent.setup();
    // Mock to return data with session
    mockSignInWithPassword.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ data: { session: { access_token: 'test-token' } }, error: null }), 100))
    );

    // Mock fetch to return profile exists
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({}),
    });

    render(<LoginPage />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');

    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);

    expect(submitButton).toBeDisabled();

    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    }, { timeout: 3000 });
  });

  it('should redirect to home if already logged in', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      session: { user: { id: 'user-123' } },
      user: { company_name: 'Test Co' },
      loading: false,
    });

    render(<LoginPage />);

    // Wait for async effect to complete and assert redirect
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/');
      expect(mockPush).toHaveBeenCalledTimes(1);
    });
  });

  it('should show loading state while auth is loading', () => {
    (useAuth as jest.Mock).mockReturnValue({
      session: null,
      loading: true,
    });

    render(<LoginPage />);

    expect(screen.getByText(/loading authentication state/i)).toBeInTheDocument();
  });

  it('should have link to signup page', () => {
    render(<LoginPage />);

    const signupLink = screen.getByRole('link', { name: /sign up/i });
    expect(signupLink).toBeInTheDocument();
    expect(signupLink).toHaveAttribute('href', '/signup');
  });

  it('should clear error when user starts typing', async () => {
    const user = userEvent.setup();
    mockSignInWithPassword.mockResolvedValueOnce({
      error: { message: 'Invalid credentials' },
    });

    render(<LoginPage />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'wrong');
    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });

    // Start typing again should clear error
    await user.type(screen.getByLabelText(/email/i), 'a');

    await waitFor(() => {
      expect(screen.queryByText(/invalid credentials/i)).not.toBeInTheDocument();
    });
  });
});