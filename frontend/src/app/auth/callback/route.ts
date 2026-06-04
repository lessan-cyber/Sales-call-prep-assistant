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
      const profileResponse = await fetch(`${backendUrl}/api/auth/profile`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      const redirectPath = profileResponse.ok ? '/dashboard' : '/profile';
      return NextResponse.redirect(new URL(redirectPath, requestUrl.origin));
    }
  }

  return NextResponse.redirect(new URL('/login', requestUrl.origin));
}
