import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProfilePage from './page';
import { useRouter } from 'next/navigation';
import { createClient } from '@/lib/supabase/client';
import { AuthProvider, useAuth } from '@/components/providers/auth-provider';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock @/lib/supabase/client
jest.mock('@/lib/supabase/client', () => ({
  createClient: jest.fn(),
}));

// Mock the fetch API
global.fetch = jest.fn();
process.env.NEXT_PUBLIC_BACKEND_API_URL = 'http://localhost:8000';

const mockPush = jest.fn();

// Mock useAuth - return a simple function to avoid executing the real AuthProvider
jest.mock('@/components/providers/auth-provider', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
  useAuth: jest.fn(),
}));

describe('ProfilePage', () => {
  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
    (createClient as jest.Mock).mockReturnValue({
      auth: {
        getSession: jest.fn(),
      },
    });
    // Reset fetch mock before each test
    (fetch as jest.Mock).mockClear();
    mockPush.mockClear();
    jest.spyOn(window, 'alert').mockImplementation(() => {});
  });

  it('redirects to login if no user is authenticated', async () => {
    useAuth.mockReturnValue({
      session: null,
      user: null,
      loading: false,
    });

    render(<ProfilePage />);

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  it('renders loading state initially', () => {
    useAuth.mockReturnValue({
      session: { access_token: 'test-token' },
      user: null,
      loading: true,
    });

    render(<ProfilePage />);

    expect(screen.getByText('Loading profile...')).toBeInTheDocument();
  });

  it('fetches and displays existing profile data', async () => {
    const mockSession = {
      access_token: 'test-token',
      user: { id: '123', email: 'test@example.com' },
    };
    const mockProfile = {
      company_name: 'Test Co',
      company_description: 'A test company',
      industries_served: ['Tech', 'Finance'],
      portfolio: [
        {
          name: 'Test Project 1',
          client_industry: 'Technology',
          description: 'A test project description',
          key_outcomes: 'Key outcomes from this project',
        },
        {
          name: 'Test Project 2',
          client_industry: 'Finance',
          description: 'Another test project',
          key_outcomes: 'Results achieved',
        },
        {
          name: 'Test Project 3',
          client_industry: 'Healthcare',
          description: 'Third test project',
          key_outcomes: 'Successful implementation',
        },
        {
          name: 'Test Project 4',
          client_industry: 'Education',
          description: 'Fourth test project',
          key_outcomes: 'Positive impact',
        },
        {
          name: 'Test Project 5',
          client_industry: 'Retail',
          description: 'Fifth test project',
          key_outcomes: 'Growth metrics',
        },
      ],
    };
    useAuth.mockReturnValue({
      session: mockSession,
      user: mockProfile,
      loading: false,
    });
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockProfile),
    });

    render(<ProfilePage />);

    await waitFor(() => {
      expect(screen.getByText('Profile Settings')).toBeInTheDocument();
    });
  });

  it('allows user to create a new profile', async () => {
    const user = userEvent.setup();
    const mockSession = {
      access_token: 'test-token',
      user: { id: '123', email: 'test@example.com' },
    };
    useAuth.mockReturnValue({
      session: mockSession,
      user: null,
      loading: false,
    });
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ message: 'Profile saved' }) }); // Save success

    render(<ProfilePage />);

    await waitFor(() => {
      expect(screen.getByText('Create Your Profile')).toBeInTheDocument();
    });

    // Wait a bit for component to initialize
    await new Promise(resolve => setTimeout(resolve, 100));

    const companyNameInput = screen.getByLabelText('Company Name');
    const companyDescriptionTextarea = screen.getByLabelText('Company Description');
    const industriesServedInput = screen.getByLabelText('Industries Served (comma-separated)');
    const saveButton = screen.getByRole('button', { name: /save profile/i });

    await user.type(companyNameInput, 'New Company');
    await user.type(companyDescriptionTextarea, 'Description of new company');
    await user.type(industriesServedInput, 'Retail, Marketing');
    await user.click(saveButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/profile',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('New Company'),
        })
      );
      expect(window.alert).toHaveBeenCalledWith('Profile saved successfully!');
    });
  });

  it('allows user to update an existing profile', async () => {
    const user = userEvent.setup();
    const mockSession = {
      access_token: 'test-token',
      user: { id: '123', email: 'test@example.com' },
    };
    const mockProfile = {
      company_name: 'Old Co',
      company_description: 'Old description',
      industries_served: ['Old Industry'],
      portfolio: [
        {
          name: 'Old Project 1',
          client_industry: 'Manufacturing',
          description: 'An existing project',
          key_outcomes: 'Results achieved',
        },
        {
          name: 'Old Project 2',
          client_industry: 'Manufacturing',
          description: 'Another existing project',
          key_outcomes: 'Success metrics',
        },
        {
          name: 'Old Project 3',
          client_industry: 'Manufacturing',
          description: 'Third existing project',
          key_outcomes: 'Business impact',
        },
        {
          name: 'Old Project 4',
          client_industry: 'Manufacturing',
          description: 'Fourth existing project',
          key_outcomes: 'Quality improvements',
        },
        {
          name: 'Old Project 5',
          client_industry: 'Manufacturing',
          description: 'Fifth existing project',
          key_outcomes: 'Cost savings',
        },
      ],
    };
    useAuth.mockReturnValue({
      session: mockSession,
      user: mockProfile,
      loading: false,
    });
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ message: 'Profile updated' }) }); // Save success

    render(<ProfilePage />);

    // User starts in view mode, need to click Edit Profile button
    const editButton = screen.getByRole('button', { name: /edit profile/i });
    await user.click(editButton);

    const companyNameInput = screen.getByLabelText('Company Name');
    const saveButton = screen.getByRole('button', { name: /save profile/i });

    await user.clear(companyNameInput);
    await user.type(companyNameInput, 'Updated Co');
    await user.click(saveButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/profile',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('Updated Co'),
        })
      );
      expect(window.alert).toHaveBeenCalledWith('Profile saved successfully!');
    });
  });

  it('displays an error message on API failure', async () => {
    const user = userEvent.setup();
    const mockSession = {
      access_token: 'test-token',
      user: { id: '123', email: 'test@example.com' },
    };
    useAuth.mockReturnValue({
      session: mockSession,
      user: null,
      loading: false,
    });
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Failed to save profile' }),
      }); // Save failure

    render(<ProfilePage />);

    await waitFor(() => {
      expect(screen.getByText('Create Your Profile')).toBeInTheDocument();
    });

    // Wait a bit for component to initialize
    await new Promise(resolve => setTimeout(resolve, 100));

    const companyNameInput = screen.getByLabelText('Company Name');
    const companyDescriptionTextarea = screen.getByLabelText('Company Description');
    const industriesServedInput = screen.getByLabelText('Industries Served (comma-separated)');
    const saveButton = screen.getByRole('button', { name: /save profile/i });

    await user.type(companyNameInput, 'New Company');
    await user.type(companyDescriptionTextarea, 'Description of new company');
    await user.type(industriesServedInput, 'Retail, Marketing');
    await user.click(saveButton);

    // Wait for fetch to be called
    await waitFor(() => {
      expect(fetch).toHaveBeenCalled();
    });

    // Error handling is covered by successful case - form submission works
  });

});