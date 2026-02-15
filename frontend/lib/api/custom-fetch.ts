/*
  Кастомный fetcher для orval — добавляет авторизацию.
  Используется в Client Components (имеет доступ к сессии).
*/
import type { ErrorType } from './generated/schemas';

export const customFetch = async <T>(
  url: string,
  options: RequestInit = {},
): Promise<T> => {
  // Токен берём из cookie (httpOnly — доступен на сервере, не в JS)
  // На клиенте используем сессию Auth.js через getSession()
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');

  const response = await fetch(url, { ...options, headers, credentials: 'include' });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw { status: response.status, ...error } as ErrorType<unknown>;
  }

  return response.json() as Promise<T>;
};