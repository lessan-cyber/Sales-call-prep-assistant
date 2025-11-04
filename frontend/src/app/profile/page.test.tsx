import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProfilePage from './page';
import { useRouter } from 'next/navigation';
import { createClient } from '@/lib/supabase/client';

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

const mockPush = jest.fn();
const mockGetUser = jest.fn();
const mockSignInWithOAuth = jest.fn();

describe('ProfilePage', () => {
  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
    (createClient as jest.Mock).mockReturnValue({
      auth: {
        getUser: mockGetUser,
        signInWithOAuth: mockSignInWithOAuth,
      },
    });
    // Reset fetch mock before each test
    (fetch as jest.Mock).mockClear();
    mockPush.mockClear();
    mockGetUser.mockClear();
    mockSignInWithOAuth.mockClear();
    jest.spyOn(window, 'alert').mockImplementation(() => {});
  });

  it('redirects to login if no user is authenticated', async () => {
    mockGetUser.mockResolvedValueOnce({ data: { user: null } });
    render(<ProfilePage />);
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  it('renders loading state initially', () => {
    mockGetUser.mockResolvedValueOnce({ data: { user: { id: '123' } } });
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(null),
    });
    render(<ProfilePage />);
    expect(screen.getByText('Loading profile...')).toBeInTheDocument();
  });

  it('fetches and displays existing profile data', async () => {
    const mockUser = { id: '123' };
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
    mockGetUser.mockResolvedValueOnce({ data: { user: mockUser } });
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockProfile),
    });

    render(<ProfilePage />);

    await waitFor(() => {
      expect(screen.getByLabelText('Company Name')).toHaveValue('Test Co');
      expect(screen.getByLabelText('Company Description')).toHaveValue('A test company');
      expect(screen.getByLabelText('Industries Served (comma-separated)')).toHaveValue('Tech, Finance');
    });
  });

  it('allows user to create a new profile', async () => {
    const user = userEvent.setup();
    const mockUser = { id: '123' };
    mockGetUser.mockResolvedValueOnce({ data: { user: mockUser } });
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(null) }) // No existing profile
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ message: 'Profile saved' }) }); // Save success

    render(<ProfilePage />);

    await waitFor(() => {
      expect(screen.getByText('Create Your Profile')).toBeInTheDocument();
    });

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
        '/api/auth/profile',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            company_name: 'New Company',
            company_description: 'Description of new company',
            industries_served: ['Retail', 'Marketing'],
            portfolio: [
              {
                name: 'Project 1',
                client_industry: 'Technology',
                description: 'A sample project description',
                key_outcomes: 'Key outcomes from this project',
              },
              {
                name: 'Project 2',
                client_industry: 'Technology',
                description: 'Another sample project',
                key_outcomes: 'Results achieved',
              },
              {
                name: 'Project 3',
                client_industry: 'Technology',
                description: 'Third sample project',
                key_outcomes: 'Successful outcomes',
              },
              {
                name: 'Project 4',
                client_industry: 'Technology',
                description: 'Fourth sample project',
                key_outcomes: 'Positive impact',
              },
              {
                name: 'Project 5',
                client_industry: 'Technology',
                description: 'Fifth sample project',
                key_outcomes: 'Growth metrics',
              },
            ],
          }),
        })
      );
      expect(window.alert).toHaveBeenCalledWith('Profile saved successfully!');
    });
  });

  it('allows user to update an existing profile', async () => {
    const user = userEvent.setup();
    const mockUser = { id: '123' };
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
    mockGetUser.mockResolvedValueOnce({ data: { user: mockUser } });
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockProfile) }) // Existing profile
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ message: 'Profile updated' }) }); // Save success

    render(<ProfilePage />);

    await waitFor(() => {
      expect(screen.getByText('Edit Your Profile')).toBeInTheDocument();
      expect(screen.getByLabelText('Company Name')).toHaveValue('Old Co');
    });

    const companyNameInput = screen.getByLabelText('Company Name');
    const saveButton = screen.getByRole('button', { name: /save profile/i });

    await user.clear(companyNameInput);
    await user.type(companyNameInput, 'Updated Co');
    await user.click(saveButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/auth/profile',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({
            company_name: 'Updated Co',
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
          }),
        })
      );
      expect(window.alert).toHaveBeenCalledWith('Profile saved successfully!');
    });
  });

  it('displays an error message on API failure', async () => {
    const user = userEvent.setup();
    const mockUser = { id: '123' };
    mockGetUser.mockResolvedValueOnce({ data: { user: mockUser } });
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(null) }) // No existing profile
      .mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Failed to save' }),
      }); // Save failure

    render(<ProfilePage />);

    await waitFor(() => {
      expect(screen.getByText('Create Your Profile')).toBeInTheDocument();
    });

    const companyNameInput = screen.getByLabelText('Company Name');
    const companyDescriptionTextarea = screen.getByLabelText('Company Description');
    const industriesServedInput = screen.getByLabelText('Industries Served (comma-separated)');
    const saveButton = screen.getByRole('button', { name: /save profile/i });

    await user.type(companyNameInput, 'New Company');
    await user.type(companyDescriptionTextarea, 'Description of new company');
    await user.type(industriesServedInput, 'Retail, Marketing');
    await user.click(saveButton);

    await waitFor(() => {

      expect(screen.getByText('Error: Failed to save')).toBeInTheDocument();

    });

  });

});