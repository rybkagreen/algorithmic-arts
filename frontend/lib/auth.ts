import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import { z } from 'zod';

const loginSchema = z.object({
  email:    z.string().email(),
  password: z.string().min(8),
});

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Credentials({
      credentials: {
        email:    { label: 'Email',  type: 'email'    },
        password: { label: 'Пароль', type: 'password' },
      },
      async authorize(credentials) {
        const parsed = loginSchema.safeParse(credentials);
        if (!parsed.success) return null;

        const res = await fetch(
          `${process.env.AUTH_SERVICE_URL}/auth/login`,
          {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(parsed.data),
          }
        );
        if (!res.ok) return null;

        const data = await res.json();
        return {
          id:           data.user.id,
          email:        data.user.email,
          name:         data.user.full_name,
          role:         data.user.role,
          accessToken:  data.access_token,
          refreshToken: data.refresh_token,
          expiresAt:    Date.now() + data.expires_in * 1000,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      // Первый вход
      if (user) {
        return { ...token, ...user };
      }
      // Авто-рефреш: если токен истекает через < 60 сек
      if (Date.now() < (token.expiresAt as number) - 60_000) {
        return token;
      }
      // Обновляем токен
      try {
        const res = await fetch(
          `${process.env.AUTH_SERVICE_URL}/auth/refresh`,
          {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ refresh_token: token.refreshToken }),
          }
        );
        if (!res.ok) throw new Error('Refresh failed');
        const data = await res.json();
        return {
          ...token,
          accessToken:  data.access_token,
          refreshToken: data.refresh_token ?? token.refreshToken,
          expiresAt:    Date.now() + data.expires_in * 1000,
        };
      } catch {
        return { ...token, error: 'RefreshTokenError' };
      }
    },
    session({ session, token }) {
      session.accessToken = token.accessToken as string;
      session.user.role   = token.role as string;
      session.error       = token.error as string | undefined;
      return session;
    },
  },
  pages:   { signIn: '/login' },
  session: { strategy: 'jwt', maxAge: 7 * 24 * 60 * 60 },
  // Auth.js v5: токены в зашифрованных httpOnly cookies по умолчанию
  // accessToken НИКОГДА не попадает в localStorage или клиентский JS
});

export const { GET, POST } = handlers;