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
      portfolio: [],
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
            portfolio: [],
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
      portfolio: [],
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
            portfolio: [],
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