'use client';
import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { Session } from '@supabase/supabase-js';

import { createClient } from '@/lib/supabase/client';
import { UserProfile } from '@/types/user_profile';

interface AuthContextType {
  session: Session | null;
  user: UserProfile | null;
  loading: boolean;
  profileLoading: boolean;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [profileLoading, setProfileLoading] = useState(true);
  const [logoutLoading, setLogoutLoading] = useState(false);
  const router = useRouter();
  const supabase = createClient();

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session) {
        // Set profileLoading to true when starting to fetch
        setProfileLoading(true);
        // Fetch user profile from backend
        fetchUserProfile(session.user.id, session.access_token);
      } else {
        setUserProfile(null);
        setProfileLoading(false);
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const fetchUserProfile = async (userId: string, accessToken: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/auth/profile`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (response.ok) {
        const profile: UserProfile = await response.json();
        setUserProfile(profile);
      } else if (response.status === 404) {
        // Profile not found, user needs to create one
        setUserProfile(null);
      } else {
        console.error('Failed to fetch user profile:', response.statusText);
        setUserProfile(null);
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
      setUserProfile(null);
    } finally {
      // Always set profileLoading to false when done
      setProfileLoading(false);
    }
  };

  const logout = async () => {
    try {
      setLogoutLoading(true);
      await supabase.auth.signOut();
      setSession(null);
      setUserProfile(null);
      router.push('/login');
    } catch (error) {
      console.error('Logout error:', error);
      // Still redirect even if there's an error
      router.push('/login');
    } finally {
      setLogoutLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ session, user: userProfile, loading, profileLoading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
