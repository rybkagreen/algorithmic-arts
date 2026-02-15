import type { DefaultSession } from 'next-auth';

declare module 'next-auth' {
  interface Session {
    accessToken: string;
    error?:      string;
    user: {
      role: string;
    } & DefaultSession['user'];
  }
}