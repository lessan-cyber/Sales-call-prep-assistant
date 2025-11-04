import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from './auth-provider';
import { createClient } from '@/lib/supabase/client';
import { useRouter } from 'next/navigation';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock supabase client
jest.mock('@/lib/supabase/client', () => ({
  createClient: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn();

const mockPush = jest.fn();
const mockSupabase = {
  auth: {
    onAuthStateChange: jest.fn(),
    getSession: jest.fn(),
  },
};

// Test component to use the hook
function TestComponent() {
  const { session, user, loading } = useAuth();
  return (
    <div>
      <div data-testid="loading">{loading ? 'loading' : 'not loading'}</div>
      <div data-testid="session">{session ? 'has session' : 'no session'}</div>
      <div data-testid="user">{user ? user.company_name : 'no user'}</div>
    </div>
  );
}

describe('AuthProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (createClient as jest.Mock).mockReturnValue(mockSupabase);
    (global.fetch as jest.Mock).mockClear();
  });

  it('should provide initial loading state', () => {
    const mockSubscription = { unsubscribe: jest.fn() };
    mockSupabase.auth.onAuthStateChange.mockReturnValue({
      data: { subscription: mockSubscription },
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('loading')).toHaveTextContent('loading');
  });

  it('should handle authenticated user with profile', async () => {
    const mockSession = {
      user: { id: 'user-123' },
      access_token: 'mock-token',
    };

    const mockProfile = {
      id: 'user-123',
      company_name: 'Test Company',
      company_description: 'Test Description',
      industries_served: ['Tech'],
      portfolio: [],
    };

    const mockSubscription = { unsubscribe: jest.fn() };
    let authCallback: any;
    mockSupabase.auth.onAuthStateChange.mockImplementation((callback) => {
      authCallback = callback;
      return { data: { subscription: mockSubscription } };
    });

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockProfile,
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Trigger auth state change
    authCallback('SIGNED_IN', mockSession);

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('not loading');
      expect(screen.getByTestId('session')).toHaveTextContent('has session');
      expect(screen.getByTestId('user')).toHaveTextContent('Test Company');
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/auth/profile', {
      headers: {
        Authorization: 'Bearer mock-token',
      },
    });
  });

  it('should handle authenticated user without profile', async () => {
    const mockSession = {
      user: { id: 'user-123' },
      access_token: 'mock-token',
    };

    const mockSubscription = { unsubscribe: jest.fn() };
    let authCallback: any;
    mockSupabase.auth.onAuthStateChange.mockImplementation((callback) => {
      authCallback = callback;
      return { data: { subscription: mockSubscription } };
    });

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    authCallback('SIGNED_IN', mockSession);

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('not loading');
      expect(screen.getByTestId('session')).toHaveTextContent('has session');
      expect(screen.getByTestId('user')).toHaveTextContent('no user');
    });
  });

  it('should handle unauthenticated user', async () => {
    const mockSubscription = { unsubscribe: jest.fn() };
    let authCallback: any;
    mockSupabase.auth.onAuthStateChange.mockImplementation((callback) => {
      authCallback = callback;
      return { data: { subscription: mockSubscription } };
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    authCallback('SIGNED_OUT', null);

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('not loading');
      expect(screen.getByTestId('session')).toHaveTextContent('no session');
      expect(screen.getByTestId('user')).toHaveTextContent('no user');
    });
  });

  it('should handle profile fetch error', async () => {
    const mockSession = {
      user: { id: 'user-123' },
      access_token: 'mock-token',
    };

    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

    const mockSubscription = { unsubscribe: jest.fn() };
    let authCallback: any;
    mockSupabase.auth.onAuthStateChange.mockImplementation((callback) => {
      authCallback = callback;
      return { data: { subscription: mockSubscription } };
    });

    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    authCallback('SIGNED_IN', mockSession);

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('not loading');
      expect(screen.getByTestId('user')).toHaveTextContent('no user');
    });

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'Error fetching user profile:',
      expect.any(Error)
    );

    consoleErrorSpy.mockRestore();
  });

  it('should unsubscribe on unmount', () => {
    const mockSubscription = { unsubscribe: jest.fn() };
    mockSupabase.auth.onAuthStateChange.mockReturnValue({
      data: { subscription: mockSubscription },
    });

    const { unmount } = render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    unmount();

    expect(mockSubscription.unsubscribe).toHaveBeenCalled();
  });

  it('should throw error when useAuth is used outside AuthProvider', () => {
    // Suppress console.error for this test
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAuth must be used within an AuthProvider');

    consoleErrorSpy.mockRestore();
  });
});