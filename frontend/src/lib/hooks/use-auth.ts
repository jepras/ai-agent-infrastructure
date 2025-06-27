import { useSession, signIn, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export interface AuthUser {
  id: string;
  email: string;
  name?: string;
  image?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignUpData {
  email: string;
  name?: string;
}

export const useAuth = () => {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const user: AuthUser | null = session?.user || null;
  const isAuthenticated = !!user;
  const isAuthLoading = status === "loading";

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await signIn("credentials", {
        email: credentials.email,
        password: credentials.password,
        redirect: false,
      });

      if (result?.error) {
        setError("Invalid credentials");
        return false;
      }

      if (result?.ok) {
        router.push("/dashboard");
        return true;
      }

      return false;
    } catch (err) {
      setError("An error occurred during login");
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (data: SignUpData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to create account");
        return false;
      }

      // After successful signup, automatically log in
      const loginResult = await signIn("credentials", {
        email: data.email,
        password: "temp-password", // This should be handled differently in production
        redirect: false,
      });

      if (loginResult?.ok) {
        router.push("/dashboard");
        return true;
      }

      return false;
    } catch (err) {
      setError("An error occurred during signup");
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await signOut({ redirect: false });
      router.push("/");
    } catch (err) {
      setError("An error occurred during logout");
    } finally {
      setIsLoading(false);
    }
  };

  const requireAuth = (callback?: () => void) => {
    if (!isAuthenticated && !isAuthLoading) {
      router.push("/auth/signin");
      return false;
    }
    
    if (callback && isAuthenticated) {
      callback();
    }
    
    return true;
  };

  return {
    user,
    isAuthenticated,
    isAuthLoading,
    isLoading,
    error,
    login,
    signup,
    logout,
    requireAuth,
    clearError: () => setError(null),
  };
}; 