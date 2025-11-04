import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import NewPrepPage from './page';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/providers/auth-provider';

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/components/providers/auth-provider', () => ({
  useAuth: jest.fn(),
}));

global.fetch = jest.fn();

const mockPush = jest.fn();
const mockSession = {
  access_token: 'mock-token',
  user: { id: 'user-123' },
};

describe('NewPrepPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (useAuth as jest.Mock).mockReturnValue({
      session: mockSession,
      loading: false,
    });
    (global.fetch as jest.Mock).mockClear();

    // Mock environment variable
    process.env.NEXT_PUBLIC_BACKEND_API_URL = 'http://localhost:8000';
  });

  it('should render prep creation form', () => {
    render(<NewPrepPage />);

    expect(screen.getByLabelText(/company name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/meeting objective/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contact person name/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /generate prep/i })).toBeInTheDocument();
  });

  it('should handle successful prep creation', async () => {
    const user = userEvent.setup();
    const mockPrepId = 'prep-123';

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: mockPrepId }),
    });

    render(<NewPrepPage />);

    await user.type(screen.getByLabelText(/company name/i), 'Acme Corp');
    await user.type(
      screen.getByLabelText(/meeting objective/i),
      'Discuss AI implementation'
    );
    await user.click(screen.getByRole('button', { name: /generate prep/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/preps',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            Authorization: 'Bearer mock-token',
          }),
          body: expect.stringContaining('Acme Corp'),
        })
      );
      expect(mockPush).toHaveBeenCalledWith(`/prep/${mockPrepId}`);
    });
  });

  it('should display error on prep creation failure', async () => {
    const user = userEvent.setup();

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Failed to create prep' }),
    });

    render(<NewPrepPage />);

    await user.type(screen.getByLabelText(/company name/i), 'Acme Corp');
    await user.type(screen.getByLabelText(/meeting objective/i), 'Test objective');
    await user.click(screen.getByRole('button', { name: /generate prep/i }));

    await waitFor(() => {
      expect(screen.getByText(/failed to create prep/i)).toBeInTheDocument();
    });

    expect(mockPush).not.toHaveBeenCalled();
  });

  it('should require company name and meeting objective', async () => {
    const user = userEvent.setup();

    render(<NewPrepPage />);

    const submitButton = screen.getByRole('button', { name: /generate prep/i });
    await user.click(submitButton);

    // Form validation should prevent submission
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('should handle optional fields', async () => {
    const user = userEvent.setup();

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 'prep-123' }),
    });

    render(<NewPrepPage />);

    await user.type(screen.getByLabelText(/company name/i), 'Acme Corp');
    await user.type(screen.getByLabelText(/meeting objective/i), 'Test objective');
    await user.type(screen.getByLabelText(/contact person name/i), 'John Doe');
    await user.type(
      screen.getByLabelText(/linkedin url/i),
      'https://linkedin.com/in/johndoe'
    );
    await user.click(screen.getByRole('button', { name: /generate prep/i }));

    await waitFor(() => {
      const fetchCall = (global.fetch as jest.Mock).mock.calls[0];
      const requestBody = JSON.parse(fetchCall[1].body);
      expect(requestBody.contact_person_name).toBe('John Doe');
      expect(requestBody.contact_linkedin_url).toBe('https://linkedin.com/in/johndoe');
    });
  });

  it('should redirect to login if not authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue({
      session: null,
      loading: false,
    });

    render(<NewPrepPage />);

    expect(mockPush).toHaveBeenCalledWith('/login');
  });

  it('should disable button while submitting', async () => {
    const user = userEvent.setup();

    (global.fetch as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ ok: true, json: async () => ({ id: '123' }) }), 100))
    );

    render(<NewPrepPage />);

    await user.type(screen.getByLabelText(/company name/i), 'Acme Corp');
    await user.type(screen.getByLabelText(/meeting objective/i), 'Test');

    const submitButton = screen.getByRole('button', { name: /generate prep/i });
    await user.click(submitButton);

    expect(submitButton).toBeDisabled();

    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    }, { timeout: 3000 });
  });

  it('should handle network errors', async () => {
    const user = userEvent.setup();

    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(<NewPrepPage />);

    await user.type(screen.getByLabelText(/company name/i), 'Acme Corp');
    await user.type(screen.getByLabelText(/meeting objective/i), 'Test');
    await user.click(screen.getByRole('button', { name: /generate prep/i }));

    await waitFor(() => {
      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });
  });
});