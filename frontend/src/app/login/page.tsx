'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { createClient } from '@/lib/supabase/client';
import { useAuth } from '@/components/providers/auth-provider';
import { info, error } from '@/lib/logger';
import { useRedirectAuthenticated } from '@/hooks/useRequireAuth';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

function isValidRedirectPath(path: string | null): path is string {
  if (!path) return false;
  if (!path.startsWith('/')) return false;
  if (path.includes('//')) return false;
  if (/^https?:/i.test(path)) return false;
  return true;
}

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const supabase = createClient();
  const { session, user, loading: authLoading } = useAuth();

  // Redirect authenticated users to dashboard
  const { loading: redirectLoading } = useRedirectAuthenticated();

  // Get returnTo parameter for post-login redirect (validated to prevent open-redirect)
  const rawReturnTo = searchParams.get('returnTo');
  const returnTo = isValidRedirectPath(rawReturnTo) ? rawReturnTo : '/dashboard';

  useEffect(() => {
    info("LoginPage mounted.");
  }, []);

  // Render loading state while checking auth
  if (authLoading || redirectLoading) {
    return <div className="flex min-h-screen items-center justify-center"><p>Loading authentication state...</p></div>;
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLoginError(null);

    const { data, error: signInError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (signInError) {
      error(`Login failed: ${signInError.message}`);
      setLoginError(signInError.message);
    } else if (data.session) {
      // Fetch user profile and redirect based on whether profile exists
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/auth/profile`, {
          headers: {
            Authorization: `Bearer ${data.session.access_token}`,
          },
        });
        // Use returnTo if specified, otherwise determine based on profile status
        const destination = response.ok ? returnTo : '/profile';
        info(`Login successful, redirecting to ${destination}`);
        router.push(destination);
      } catch (err) {
        // On error, default to profile page
        info("Login successful, redirecting to profile.");
        router.push('/profile');
      }
    }
    setLoading(false);
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    setLoginError(null);
    const { error: googleSignInError } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    if (googleSignInError) {
      error(`Google login failed: ${googleSignInError.message}`);
      setLoginError(googleSignInError.message);
    }
    setLoading(false);
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl">Login</CardTitle>
          <CardDescription>Enter your email and password to sign in</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          {loginError && <p className="text-sm text-red-500">{loginError}</p>}
          <form onSubmit={handleLogin} className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (loginError) setLoginError(null);
                }}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (loginError) setLoginError(null);
                }}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </form>
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                Or continue with
              </span>
            </div>
          </div>
          <Button variant="outline" className="w-full" onClick={handleGoogleLogin} disabled={loading}>
            Google
          </Button>
        </CardContent>
        <CardFooter className="flex justify-center">
          <p className="text-sm text-muted-foreground">
            Don't have an account?{" "}
            <Link href="/signup" className="text-primary hover:underline">
              Sign Up
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
