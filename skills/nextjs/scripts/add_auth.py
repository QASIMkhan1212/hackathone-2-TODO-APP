#!/usr/bin/env python3
"""Add NextAuth.js authentication to a Next.js project."""

import argparse
from pathlib import Path


def add_auth(base_path: Path, provider: str = "credentials") -> None:
    """Add NextAuth.js authentication setup."""

    app_path = base_path / "app"
    lib_path = base_path / "lib"

    if not app_path.exists():
        print(f"Error: 'app' directory not found at {base_path}")
        return

    lib_path.mkdir(exist_ok=True)

    print("Setting up NextAuth.js authentication...")
    print("=" * 50)

    # Create API route
    auth_api_path = app_path / "api" / "auth" / "[...nextauth]"
    auth_api_path.mkdir(parents=True, exist_ok=True)

    route_content = '''import NextAuth from 'next-auth';
import { authOptions } from '@/lib/auth';

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
'''

    route_file = auth_api_path / "route.ts"
    route_file.write_text(route_content)
    print(f"Created: {route_file}")

    # Create auth config
    if provider == "google":
        auth_config = '''import { NextAuthOptions } from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import { PrismaAdapter } from '@auth/prisma-adapter';
import { db } from '@/lib/db';

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(db),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  session: {
    strategy: 'jwt',
  },
  pages: {
    signIn: '/login',
    error: '/auth/error',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
      }
      return session;
    },
  },
};
'''
    else:  # credentials
        auth_config = '''import { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { PrismaAdapter } from '@auth/prisma-adapter';
import { db } from '@/lib/db';
import bcrypt from 'bcryptjs';

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(db),
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        const user = await db.user.findUnique({
          where: { email: credentials.email },
        });

        if (!user || !user.hashedPassword) {
          return null;
        }

        const isValid = await bcrypt.compare(
          credentials.password,
          user.hashedPassword
        );

        if (!isValid) {
          return null;
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
        };
      },
    }),
  ],
  session: {
    strategy: 'jwt',
  },
  pages: {
    signIn: '/login',
    error: '/auth/error',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
      }
      return session;
    },
  },
};
'''

    auth_file = lib_path / "auth.ts"
    auth_file.write_text(auth_config)
    print(f"Created: {auth_file}")

    # Create providers wrapper
    providers_content = ''''use client';

import { SessionProvider } from 'next-auth/react';

export function Providers({ children }: { children: React.ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>;
}
'''

    providers_file = app_path / "providers.tsx"
    providers_file.write_text(providers_content)
    print(f"Created: {providers_file}")

    # Create login page
    login_path = app_path / "login"
    login_path.mkdir(exist_ok=True)

    if provider == "google":
        login_content = ''''use client';

import { signIn } from 'next-auth/react';
import { useSearchParams } from 'next/navigation';

export default function LoginPage() {
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get('callbackUrl') || '/dashboard';

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full space-y-8 p-8">
        <h2 className="text-center text-3xl font-bold">Sign in</h2>

        <button
          onClick={() => signIn('google', { callbackUrl })}
          className="w-full flex justify-center py-2 px-4 border rounded-md shadow-sm bg-white hover:bg-gray-50"
        >
          Sign in with Google
        </button>
      </div>
    </div>
  );
}
'''
    else:
        login_content = ''''use client';

import { signIn } from 'next-auth/react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get('callbackUrl') || '/dashboard';
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError('');

    const formData = new FormData(e.currentTarget);

    const result = await signIn('credentials', {
      email: formData.get('email'),
      password: formData.get('password'),
      redirect: false,
    });

    setLoading(false);

    if (result?.error) {
      setError('Invalid email or password');
    } else {
      router.push(callbackUrl);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full space-y-8 p-8">
        <h2 className="text-center text-3xl font-bold">Sign in</h2>

        {error && (
          <div className="bg-red-50 text-red-500 p-3 rounded">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="mt-1 block w-full rounded-md border p-2"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              className="mt-1 block w-full rounded-md border p-2"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}
'''

    login_file = login_path / "page.tsx"
    login_file.write_text(login_content)
    print(f"Created: {login_file}")

    # Create middleware
    middleware_content = '''import { withAuth } from 'next-auth/middleware';

export default withAuth({
  pages: {
    signIn: '/login',
  },
});

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*'],
};
'''

    middleware_file = base_path / "middleware.ts"
    middleware_file.write_text(middleware_content)
    print(f"Created: {middleware_file}")

    # Create types extension
    types_path = base_path / "types"
    types_path.mkdir(exist_ok=True)

    types_content = '''import { DefaultSession, DefaultUser } from 'next-auth';

declare module 'next-auth' {
  interface Session {
    user: {
      id: string;
    } & DefaultSession['user'];
  }

  interface User extends DefaultUser {
    id: string;
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    id: string;
  }
}
'''

    types_file = types_path / "next-auth.d.ts"
    types_file.write_text(types_content)
    print(f"Created: {types_file}")

    # Print env variables needed
    print("\n" + "=" * 50)
    print("Authentication setup complete!")
    print("\nAdd these to your .env.local file:")
    print("-" * 50)
    print("NEXTAUTH_SECRET=your-secret-key-here")
    print("NEXTAUTH_URL=http://localhost:3000")
    if provider == "google":
        print("GOOGLE_CLIENT_ID=your-google-client-id")
        print("GOOGLE_CLIENT_SECRET=your-google-client-secret")
    print("-" * 50)
    print("\nInstall required packages:")
    print("npm install next-auth @auth/prisma-adapter")
    if provider == "credentials":
        print("npm install bcryptjs")
        print("npm install -D @types/bcryptjs")
    print("\nUpdate your layout.tsx to wrap with Providers:")
    print('import { Providers } from "./providers";')
    print("<Providers>{children}</Providers>")


def main():
    parser = argparse.ArgumentParser(
        description="Add NextAuth.js authentication to Next.js project"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Project root path (default: current directory)"
    )
    parser.add_argument(
        "--provider",
        choices=["credentials", "google"],
        default="credentials",
        help="Authentication provider (default: credentials)"
    )

    args = parser.parse_args()
    add_auth(args.path, args.provider)


if __name__ == "__main__":
    main()
