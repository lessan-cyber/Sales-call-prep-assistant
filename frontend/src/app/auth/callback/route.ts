import { createClient } from '@/lib/supabase/client';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');

  if (code) {
    const supabase = createClient();
    const { data: { session }, error } = await supabase.auth.exchangeCodeForSession(code);

    if (session && !error) {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL;

      try {
        const profileResponse = await fetch(`${backendUrl}/api/auth/profile`, {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });

        if (profileResponse.status === 404) {
          return NextResponse.redirect(new URL('/profile', requestUrl.origin));
        }

        if (profileResponse.ok) {
          return NextResponse.redirect(new URL('/dashboard', requestUrl.origin));
        }

        throw new Error(`Profile fetch failed: ${profileResponse.status}`);
      } catch {
        return NextResponse.redirect(new URL('/login', requestUrl.origin));
      }
    }
  }

  return NextResponse.redirect(new URL('/login', requestUrl.origin));
}
