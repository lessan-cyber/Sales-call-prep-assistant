import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SignupPage from './page';
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
const mockSignUp = jest.fn();
const mockSignInWithOAuth = jest.fn();

describe('SignupPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (createClient as jest.Mock).mockReturnValue({
      auth: {
        signUp: mockSignUp,
        signInWithOAuth: mockSignInWithOAuth,
      },
    });
    (useAuth as jest.Mock).mockReturnValue({
      session: null,
      loading: false,
    });
  });

  it('should render signup form', () => {
    render(<SignupPage />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
  });

  it('should handle successful signup', async () => {
    const user = userEvent.setup();
    mockSignUp.mockResolvedValueOnce({ error: null });

    render(<SignupPage />);

    await user.type(screen.getByLabelText(/email/i), 'newuser@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign up/i }));

    await waitFor(() => {
      expect(mockSignUp).toHaveBeenCalledWith({
        email: 'newuser@example.com',
        password: 'password123',
      });
    });
  });

  it('should show error when passwords do not match', async () => {
    const user = userEvent.setup();

    render(<SignupPage />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password456');
    await user.click(screen.getByRole('button', { name: /sign up/i }));

    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });

    expect(mockSignUp).not.toHaveBeenCalled();
  });

  it('should display API error on failed signup', async () => {
    const user = userEvent.setup();
    mockSignUp.mockResolvedValueOnce({
      error: { message: 'Email already registered' },
    });

    render(<SignupPage />);

    await user.type(screen.getByLabelText(/email/i), 'existing@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign up/i }));

    await waitFor(() => {
      expect(screen.getByText(/email already registered/i)).toBeInTheDocument();
    });
  });

  it('should validate password strength', async () => {
    const user = userEvent.setup();

    render(<SignupPage />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/^password$/i), '123');
    await user.type(screen.getByLabelText(/confirm password/i), '123');

    const submitButton = screen.getByRole('button', { name: /sign up/i });
    expect(submitButton).toBeDisabled();
  });

  it('should redirect if already logged in', () => {
    (useAuth as jest.Mock).mockReturnValue({
      session: { user: { id: 'user-123' } },
      loading: false,
    });

    render(<SignupPage />);

    expect(mockPush).toHaveBeenCalledWith('/profile');
  });

  it('should have link to login page', () => {
    render(<SignupPage />);

    const loginLink = screen.getByRole('link', { name: /login/i });
    expect(loginLink).toBeInTheDocument();
    expect(loginLink).toHaveAttribute('href', '/login');
  });

  it('should handle Google OAuth signup', async () => {
    const user = userEvent.setup();
    mockSignInWithOAuth.mockResolvedValueOnce({ error: null });

    render(<SignupPage />);

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
});