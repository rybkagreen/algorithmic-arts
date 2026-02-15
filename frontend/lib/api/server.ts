/*
  Server-side fetcher: использует токен из сессии Auth.js.
  Вызывается напрямую в async Server Components.
*/
import { auth } from '@/lib/auth';
import type { NextFetchRequestConfig } from 'next/dist/shared/lib/utils';

const API_URL = process.env.API_GATEWAY_URL ?? 'http://localhost:8000';

export async function serverFetch<T>(
  path: string,
  options: RequestInit & { next?: NextFetchRequestConfig } = {},
): Promise<T> {
  const session = await auth();

  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  if (session?.accessToken) {
    headers.set('Authorization', `Bearer ${session.accessToken}`);
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    // Next.js 16 Cache Components: используй 'use cache' вместо next.revalidate
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(error.detail);
  }

  return res.json() as Promise<T>;
}