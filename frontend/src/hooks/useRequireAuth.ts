"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/components/providers/auth-provider";

interface RequireAuthOptions {
  requireProfile?: boolean;
  redirectTo?: string;
}

/**
 * Hook to protect routes and manage authentication-based redirection.
 *
 * @param options - Configuration options
 * @param options.requireProfile - If true, requires user to have a completed profile
 * @param options.redirectTo - Custom redirect path (default depends on auth state)
 */
export function useRequireAuth(options: RequireAuthOptions = {}) {
  const { requireProfile = false, redirectTo } = options;
  const router = useRouter();
  const searchParams = useSearchParams();
  const { session, user, loading, profileLoading } = useAuth();

  // Get returnTo from search params (for post-login redirect)
  const returnTo = searchParams.get("returnTo") || redirectTo;

  useEffect(() => {
    // Wait for auth and profile loading to complete
    if (loading || profileLoading) {
      return;
    }

    // Not authenticated - redirect to login
    if (!session) {
      const loginPath = returnTo
        ? `/login?returnTo=${encodeURIComponent(returnTo)}`
        : "/login";
      router.push(loginPath);
      return;
    }

    // Authenticated but no profile - redirect to profile
    if (requireProfile && !user) {
      router.push("/profile");
      return;
    }

    // Authenticated and has profile (or profile not required) - stay where you are
    if (user || !requireProfile) {
      return;
    }
  }, [session, user, loading, profileLoading, requireProfile, router, returnTo]);

  // Return auth state for components to use
  return {
    session,
    user,
    loading: loading || profileLoading,
    isAuthenticated: !!session,
    hasProfile: !!user,
  };
}

/**
 * Hook for pages that should redirect authenticated users away
 * (like login/signup pages)
 */
export function useRedirectAuthenticated() {
  const router = useRouter();
  const { session, user, loading } = useAuth();

  useEffect(() => {
    // Wait for auth to load
    if (loading) {
      return;
    }

    // If authenticated, redirect to dashboard or returnTo
    if (session) {
      router.push("/dashboard");
      return;
    }
  }, [session, user, loading, router]);

  return {
    session,
    user,
    loading,
    isAuthenticated: !!session,
  };
}
