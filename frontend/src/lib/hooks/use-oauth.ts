import { useState, useEffect, useCallback } from 'react';

interface ServiceStatus {
  outlook: boolean;
  pipedrive: boolean;
  openai: boolean;
  anthropic: boolean;
}

interface OAuthHookReturn {
  serviceStatus: ServiceStatus | null;
  loading: boolean;
  error: string | null;
  connectOAuth: (provider: string, userId: string) => Promise<void>;
  refreshStatus: (userId: string) => Promise<void>;
}

export function useOAuth(): OAuthHookReturn {
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<number>(0);

  const connectOAuth = async (provider: string, userId: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/oauth/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider,
          user_id: userId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to connect OAuth provider');
      }

      const data = await response.json();
      
      // If successful, redirect to the OAuth URL
      if (data.oauth_url) {
        window.location.href = data.oauth_url;
      } else {
        // If no redirect URL, refresh the status
        await refreshStatus(userId);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const refreshStatus = useCallback(async (userId: string) => {
    // Debounce: only refresh if it's been more than 2 seconds since last refresh
    const now = Date.now();
    if (now - lastRefresh < 2000) {
      return;
    }
    
    setLoading(true);
    setError(null);
    setLastRefresh(now);

    try {
      const response = await fetch(`/api/services/status?user_id=${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get service status');
      }

      const data = await response.json();
      setServiceStatus(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [lastRefresh]);

  return {
    serviceStatus,
    loading,
    error,
    connectOAuth,
    refreshStatus,
  };
} 