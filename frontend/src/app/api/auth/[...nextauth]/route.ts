import NextAuth from "next-auth";
import { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

// Extend the built-in session types
declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      email: string;
      name?: string;
      image?: string;
    };
  }
  
  interface User {
    id: string;
    email: string;
    name?: string;
    image?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id: string;
  }
}

const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          console.log("Attempting to authenticate with backend API...");
          const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/auth/users/email/${credentials.email}`;
          console.log("API URL:", apiUrl);
          
          const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });
          
          console.log("API Response status:", response.status);
          
          if (response.ok) {
            const user = await response.json();
            console.log("User data from API:", user);
            return {
              id: user.id,
              email: user.email,
              name: user.name || credentials.email.split('@')[0], // Fallback to email prefix
              image: user.image,
            };
          } else {
            console.log("API returned error status:", response.status);
            const errorText = await response.text();
            console.log("API error response:", errorText);
          }
          
          // If API fails, create a user with email-based name
          console.log("Creating fallback user for:", credentials.email);
          return {
            id: `user-${credentials.email}`,
            email: credentials.email,
            name: credentials.email.split('@')[0], // Use email prefix as name
            image: null,
          };
          
        } catch (error) {
          console.error("Auth error:", error);
          // Fallback: create user with email-based name
          console.log("Using fallback authentication due to API error");
          return {
            id: `user-${credentials.email}`,
            email: credentials.email,
            name: credentials.email.split('@')[0], // Use email prefix as name
            image: null,
          };
        }
      }
    })
  ],
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (token && session.user) {
        session.user.id = token.id;
      }
      return session;
    },
  },
  pages: {
    signIn: "/auth/signin",
  },
  secret: process.env.NEXTAUTH_SECRET,
  debug: process.env.NODE_ENV === 'development',
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST }; 