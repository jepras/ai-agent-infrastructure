import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (!code || !state) {
      return NextResponse.redirect(new URL('/dashboard?oauth_error=Missing authorization code', request.url));
    }

    // Get the backend URL from environment variables
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Call the backend OAuth callback endpoint
    const response = await fetch(`${backendUrl}/api/auth/callback/pipedrive?code=${code}&state=${state}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.redirect(new URL(`/dashboard?oauth_error=${errorData.detail || 'Authentication failed'}`, request.url));
    }

    const data = await response.json();
    
    // Redirect to dashboard with success
    return NextResponse.redirect(new URL('/dashboard?oauth_success=true&service=pipedrive', request.url));

  } catch (error) {
    console.error('Pipedrive OAuth callback error:', error);
    return NextResponse.redirect(new URL('/dashboard?oauth_error=Authentication failed', request.url));
  }
} 