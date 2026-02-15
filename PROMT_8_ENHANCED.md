# ALGORITHMIC ARTS — Улучшенный Промпт №8

**Версия:** 3.1 (Enhanced)
**Дата:** 14 Февраля 2026
**Статус:** Production Ready

### Задача
Создай полноценный Next.js 16 frontend для платформы ALGORITHMIC ARTS.

═══════════════════════════════════════════════════════════
ЧАСТЬ 1: ТЕХНОЛОГИИ И ВЕРСИИ
═══════════════════════════════════════════════════════════

Next.js        16.1   (App Router, Cache Components, Turbopack stable)
React          19.1   (use(), useOptimistic(), useFormStatus(), compiler)
TypeScript     5.8    (strict + noUncheckedIndexedAccess + exactOptionalPropertyTypes)
Tailwind CSS   4.x    (CSS-first, @theme директива, НЕТ tailwind.config.ts)
shadcn/ui      latest (совместим с Tailwind v4)
TanStack Query 5.x   (серверное состояние)
Zustand        5.x   (клиентское состояние, БЕЗ persist для токенов)
Auth.js        5.x   (httpOnly cookies, JWT в памяти)
orval          7.x   (кодогенерация API-клиента из OpenAPI FastAPI)
ofetch         1.x   (HTTP для Server Components)
Sonner                (уведомления — де-факто стандарт shadcn/ui)
Zod            3.x   (валидация)
react-hook-form 7.x
Playwright     1.x   (e2e-тесты)
Storybook      8.x   (компонентная документация)

package.json:
{
  "scripts": {
    "dev":          "next dev",               // Turbopack включён по умолчанию в Next.js 16
    "build":        "next build",
    "start":        "next start",
    "type-check":   "tsc --noEmit",
    "lint":         "next lint",
    "test:e2e":     "playwright test",
    "generate:api": "orval",                  // кодогенерация из OpenAPI
    "storybook":    "storybook dev -p 6006"
  }
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 2: ПОЛНАЯ ФАЙЛОВАЯ СТРУКТУРА
═══════════════════════════════════════════════════════════

frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── layout.tsx
│   │
│   ├── (dashboard)/
│   │   ├── companies/
│   │   │   ├── page.tsx           # Server Component (async)
│   │   │   ├── loading.tsx        # Skeleton
│   │   │   ├── error.tsx          # Error boundary
│   │   │   ├── [id]/page.tsx
│   │   │   └── new/page.tsx       # Server Action форма
│   │   ├── partnerships/
│   │   │   ├── page.tsx
│   │   │   ├── loading.tsx
│   │   │   ├── recommendations/page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── analytics/page.tsx
│   │   ├── settings/
│   │   │   └── page.tsx           # CRM-подключения + профиль
│   │   └── layout.tsx
│   │
│   ├── actions/                   # Server Actions (мутации)
│   │   ├── companies.ts
│   │   ├── partnerships.ts
│   │   └── auth.ts
│   │
│   ├── api/
│   │   └── auth/[...nextauth]/route.ts
│   │
│   ├── layout.tsx                 # Root: providers, Inter шрифт, metadata
│   ├── page.tsx                   # Landing
│   ├── loading.tsx
│   ├── error.tsx
│   └── not-found.tsx
│
├── components/
│   ├── ui/                        # shadcn/ui компоненты
│   ├── companies/
│   │   ├── CompanyCard.tsx
│   │   ├── CompanyCardSkeleton.tsx
│   │   ├── CompanyFilters.tsx
│   │   ├── CompanySearch.tsx      # debounce 300ms
│   │   ├── CompanyForm.tsx        # react-hook-form + Server Action
│   │   └── TechStackBadges.tsx
│   ├── partnerships/
│   │   ├── PartnershipCard.tsx
│   │   ├── CompatibilityScore.tsx
│   │   ├── OutreachDialog.tsx
│   │   └── PartnershipTimeline.tsx
│   ├── analytics/
│   │   ├── StatsCard.tsx
│   │   ├── PartnershipChart.tsx   # recharts, dynamic import
│   │   └── IndustryPieChart.tsx   # recharts, dynamic import
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── ThemeToggle.tsx
│   └── providers/
│       ├── QueryProvider.tsx      # TanStack Query
│       ├── RealtimeProvider.tsx   # WebSocket context
│       └── ThemeProvider.tsx      # next-themes
│
├── lib/
│   ├── api/
│   │   ├── server.ts              # ofetch клиент для Server Components
│   │   └── generated/            # ← orval генерирует сюда (НЕ редактировать вручную)
│   │       ├── companies.ts
│   │       ├── partnerships.ts
│   │       ├── auth.ts
│   │       └── schemas.ts        # Zod-схемы из OpenAPI
│   ├── hooks/
│   │   ├── useCompanies.ts       # TanStack Query обёртки над orval
│   │   ├── usePartnerships.ts
│   │   ├── useRealtimeUpdates.ts # нативный WebSocket
│   │   └── useDebounce.ts
│   ├── stores/
│   │   └── filterStore.ts        # Zustand: только UI-состояние (фильтры)
│   └── utils/
│       ├── cn.ts                 # clsx + tailwind-merge
│       └── formatters.ts         # деньги, даты, скоры
│
├── types/
│   ├── auth.ts                   # Session, NextAuth типы
│   └── global.d.ts               # Расширение Session
│
├── orval.config.ts               # Конфигурация кодогенерации
├── proxy.ts                      # Next.js 16: защита роутов (заменяет middleware.ts)
├── next.config.ts
├── tsconfig.json
├── styles/globals.css            # Tailwind v4: @import + @theme
├── playwright.config.ts
└── .env.local.example


═══════════════════════════════════════════════════════════
ЧАСТЬ 3: TAILWIND CSS V4 — CSS-FIRST КОНФИГУРАЦИЯ
═══════════════════════════════════════════════════════════

## styles/globals.css:

@import "tailwindcss";

/*
  Tailwind v4: конфигурация через @theme, НЕТ tailwind.config.ts
  Все токены автоматически становятся CSS-переменными
*/
@theme {
  /* Цвета бренда */
  --color-brand-50:  #eff6ff;
  --color-brand-500: #3b82f6;
  --color-brand-900: #1e3a8a;

  /* shadcn/ui совместимые переменные */
  --color-background:        hsl(0 0% 100%);
  --color-foreground:        hsl(222.2 84% 4.9%);
  --color-primary:           hsl(221.2 83.2% 53.3%);
  --color-primary-foreground:hsl(210 40% 98%);
  --color-muted:             hsl(210 40% 96.1%);
  --color-muted-foreground:  hsl(215.4 16.3% 46.9%);
  --color-border:            hsl(214.3 31.8% 91.4%);
  --color-card:              hsl(0 0% 100%);

  /* Шрифты */
  --font-sans: 'Inter', ui-sans-serif, system-ui;
  --font-mono: 'JetBrains Mono', ui-monospace;

  /* Радиусы */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
}

/* Dark mode через .dark класс */
.dark {
  --color-background:        hsl(222.2 84% 4.9%);
  --color-foreground:        hsl(210 40% 98%);
  --color-primary:           hsl(217.2 91.2% 59.8%);
  --color-muted:             hsl(217.2 32.6% 17.5%);
  --color-muted-foreground:  hsl(215 20.2% 65.1%);
  --color-border:            hsl(217.2 32.6% 17.5%);
  --color-card:              hsl(222.2 84% 4.9%);
}

/*
  ВАЖНО для Next.js 16 + Tailwind v4:
  Добавь в next.config.ts плагин @tailwindcss/postcss
*/


## next.config.ts:

import type { NextConfig } from 'next';

const config: NextConfig = {
  // Tailwind v4 через PostCSS плагин
  // В package.json: "@tailwindcss/postcss": "^4"
  // В postcss.config.mjs: plugins: { '@tailwindcss/postcss': {} }

  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**.yandexcloud.net' },
      { protocol: 'https', hostname: 'storage.yandexcloud.net' },
    ],
  },

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Frame-Options',           value: 'DENY' },
          { key: 'X-Content-Type-Options',     value: 'nosniff' },
          { key: 'Referrer-Policy',            value: 'strict-origin-when-cross-origin' },
          { key: 'Permissions-Policy',         value: 'camera=(), microphone=(), geolocation=()' },
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline'", // eval нужен Next.js dev
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: https://storage.yandexcloud.net",
              "connect-src 'self' ws://localhost:* wss://*.algorithmic-arts.ru",
            ].join('; '),
          },
        ],
      },
    ];
  },

  async rewrites() {
    return [
      {
        source:      '/api/v1/:path*',
        destination: `${process.env.API_GATEWAY_URL}/api/v1/:path*`,
      },
    ];
  },

  // Cache Components — замена PPR в Next.js 16
  // experimental.ppr удалён, используй 'use cache' директиву
};

export default config;


═══════════════════════════════════════════════════════════
ЧАСТЬ 4: PROXY.TS — защита роутов (Next.js 16)
═══════════════════════════════════════════════════════════

## proxy.ts:

/*
  Next.js 16: middleware.ts → proxy.ts
  proxy выполняется в Node.js runtime (не Edge)
  Экспортируемая функция называется proxy (не middleware)
*/
import { auth } from '@/lib/auth';
import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Публичные пути
  const publicPaths = ['/login', '/register', '/', '/api/auth'];
  if (publicPaths.some(p => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // Защита /dashboard/*
  const session = await auth();
  if (!session) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('callbackUrl', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // RBAC: только admin видит /admin/*
  if (pathname.startsWith('/admin') && session.user.role !== 'admin') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};


═══════════════════════════════════════════════════════════
ЧАСТЬ 5: КОДОГЕНЕРАЦИЯ API (orval)
═══════════════════════════════════════════════════════════

## orval.config.ts:

import { defineConfig } from 'orval';

export default defineConfig({
  algorithmic_arts: {
    input: {
      target: process.env.API_GATEWAY_URL
        ? `${process.env.API_GATEWAY_URL}/openapi.json`
        : 'http://localhost:8000/openapi.json',
    },
    output: {
      mode:   'tags-split',              // разбивка по тегам OpenAPI
      target: 'lib/api/generated',
      schemas: 'lib/api/generated/schemas',
      client: 'fetch',                   // нативный fetch, не axios
      httpClient: 'fetch',
      override: {
        mutator: {
          path: 'lib/api/custom-fetch.ts',
          name: 'customFetch',           // добавляем auth заголовок
        },
        query: {
          useQuery: true,
          useMutation: true,
          signal: true,                  // AbortSignal поддержка
        },
      },
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write lib/api/generated/**/*.ts',
    },
  },
});


## lib/api/custom-fetch.ts:

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


## lib/api/server.ts — для Server Components:

/*
  Server-side fetcher: использует токен из сессии Auth.js.
  Вызывается напрямую в async Server Components.
*/
import { auth } from '@/lib/auth';

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


═══════════════════════════════════════════════════════════
ЧАСТЬ 6: АУТЕНТИФИКАЦИЯ (Auth.js v5 + httpOnly cookies)
═══════════════════════════════════════════════════════════

## lib/auth.ts:

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


## types/global.d.ts — расширение Session:

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


═══════════════════════════════════════════════════════════
ЧАСТЬ 7: ZUSTAND — только UI-состояние
═══════════════════════════════════════════════════════════

/*
  ВАЖНО: Zustand НЕ хранит токены. Только UI-состояние:
  фильтры, открытые панели, локальные настройки.
  Токены — исключительно в httpOnly cookies через Auth.js.
*/

## lib/stores/filterStore.ts:

import { create } from 'zustand';

interface CompanyFilters {
  search?:          string;
  industry?:        string;
  employees_range?: string;
  funding_stage?:   string;
  tech_stack?:      string[];
  page:             number;
  size:             number;
}

interface FilterState {
  companyFilters:       CompanyFilters;
  setCompanyFilter:    <K extends keyof CompanyFilters>(k: K, v: CompanyFilters[K]) => void;
  resetCompanyFilters: () => void;
}

const defaults: CompanyFilters = { page: 1, size: 12 };

export const useFilterStore = create<FilterState>((set) => ({
  companyFilters: defaults,
  setCompanyFilter: (key, value) =>
    set(s => ({ companyFilters: { ...s.companyFilters, [key]: value, page: 1 } })),
  resetCompanyFilters: () => set({ companyFilters: defaults }),
}));


═══════════════════════════════════════════════════════════
ЧАСТЬ 8: SERVER ACTIONS — мутации
═══════════════════════════════════════════════════════════

/*
  Next.js 16 + React 19: мутации через Server Actions.
  Преимущества:
  - Progressive Enhancement (работает без JS)
  - Нет отдельного API-route для каждой формы
  - useFormStatus(), useOptimistic() из React 19 работают нативно
*/

## app/actions/companies.ts:

'use server';

import { z } from 'zod';
import { revalidatePath } from 'next/cache';
import { auth } from '@/lib/auth';
import { serverFetch } from '@/lib/api/server';
import type { Company } from '@/lib/api/generated/schemas';

const createCompanySchema = z.object({
  name:              z.string().min(2).max(100),
  description:       z.string().max(1000).optional(),
  industry:          z.string(),
  website:           z.string().url().optional().or(z.literal('')),
  headquarters_city: z.string().optional(),
  employees_range:   z.enum(['1-10','11-50','51-200','201-500','500+']),
  funding_stage:     z.enum(['pre_seed','seed','series_a','series_b','bootstrapped','ipo']),
});

export type CreateCompanyState = {
  errors?: Record<string, string[]>;
  message?: string;
  company?: Company;
};

export async function createCompanyAction(
  _prevState: CreateCompanyState,
  formData: FormData,
): Promise<CreateCompanyState> {
  const session = await auth();
  if (!session) return { message: 'Unauthorized' };

  const raw = Object.fromEntries(formData.entries());
  const parsed = createCompanySchema.safeParse(raw);

  if (!parsed.success) {
    return { errors: parsed.error.flatten().fieldErrors };
  }

  const company = await serverFetch<Company>('/companies', {
    method: 'POST',
    body:   JSON.stringify(parsed.data),
  });

  revalidatePath('/companies');
  return { company };
}


## app/actions/partnerships.ts:

'use server';

import { revalidatePath } from 'next/cache';
import { auth } from '@/lib/auth';
import { serverFetch } from '@/lib/api/server';

export async function updatePartnershipStatusAction(
  partnershipId: string,
  status: string,
): Promise<{ success: boolean }> {
  const session = await auth();
  if (!session) throw new Error('Unauthorized');

  await serverFetch(`/partnerships/${partnershipId}`, {
    method: 'PATCH',
    body:   JSON.stringify({ status }),
  });

  revalidatePath('/partnerships');
  revalidatePath(`/partnerships/${partnershipId}`);
  return { success: true };
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 9: TANSTACK QUERY ХУКИ
═══════════════════════════════════════════════════════════

## lib/hooks/useCompanies.ts:

/*
  Используем сгенерированные orval-функции, обёрнутые в TanStack Query.
  Orval генерирует useGetCompanies(), useCreateCompany() и т.д.
  Здесь — только дополнительная логика поверх них.
*/

import { keepPreviousData, useQueryClient } from '@tanstack/react-query';
import { useGetCompanies, useGetCompanyById } from '@/lib/api/generated/companies';
import { useFilterStore } from '@/lib/stores/filterStore';
import { toast } from 'sonner';

export function useCompanies() {
  const filters = useFilterStore(s => s.companyFilters);
  return useGetCompanies(filters, {
    query: {
      placeholderData: keepPreviousData,
      staleTime:       30_000,
    },
  });
}

export function useCompany(id: string) {
  return useGetCompanyById(id, {
    query: {
      enabled:   !!id,
      staleTime: 60_000,
    },
  });
}


## lib/hooks/usePartnerships.ts:

import {
  useGetPartnerships,
  useGetRecommendations,
  useUpdatePartnership,
} from '@/lib/api/generated/partnerships';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

export function usePartnerships(params = {}) {
  return useGetPartnerships(params, {
    query: { staleTime: 30_000 },
  });
}

export function useRecommendations() {
  return useGetRecommendations({ limit: 20 }, {
    query: {
      staleTime: 120_000,    // 2 мин — AI дорогой
      gcTime:    300_000,
    },
  });
}

export function useUpdatePartnershipStatus() {
  const qc = useQueryClient();
  return useUpdatePartnership({
    mutation: {
      onSuccess: () => {
        qc.invalidateQueries({ queryKey: ['partnerships'] });
        toast.success('Статус партнёрства обновлён');
      },
      onError: () => toast.error('Не удалось обновить статус'),
    },
  });
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 10: WEBSOCKET (нативный, без socket.io)
═══════════════════════════════════════════════════════════

## lib/hooks/useRealtimeUpdates.ts:

'use client';

import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8080/ws';

type WSStatus = 'connecting' | 'connected' | 'disconnected';

export function useRealtimeUpdates(enabled = true) {
  const qc     = useQueryClient();
  const wsRef  = useRef<WebSocket | null>(null);
  const retryRef = useRef<ReturnType<typeof setTimeout>>(null);
  const [status, setStatus] = useState<WSStatus>('disconnected');

  useEffect(() => {
    if (!enabled) return;

    function connect() {
      setStatus('connecting');
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen  = () => setStatus('connected');
      ws.onerror = () => ws.close();

      ws.onmessage = ({ data }) => {
        try {
          const msg = JSON.parse(data as string) as { type: string };
          switch (msg.type) {
            case 'company.created':
            case 'company.updated':
              void qc.invalidateQueries({ queryKey: ['companies'] });
              break;
            case 'partnership.matched':
              void qc.invalidateQueries({ queryKey: ['partnerships'] });
              toast.success('Найдено новое партнёрство!', {
                description: 'Проверь раздел Рекомендации',
                action: { label: 'Открыть', onClick: () => window.location.href = '/partnerships/recommendations' },
              });
              break;
            case 'ai.analysis.completed':
              void qc.invalidateQueries({ queryKey: ['partnerships', 'recommendations'] });
              break;
          }
        } catch { /* игнорируем некорректные сообщения */ }
      };

      ws.onclose = () => {
        setStatus('disconnected');
        retryRef.current = setTimeout(connect, 5_000);
      };
    }

    connect();
    return () => {
      clearTimeout(retryRef.current!);
      wsRef.current?.close();
    };
  }, [enabled, qc]);

  return { status };
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 11: КЛЮЧЕВЫЕ КОМПОНЕНТЫ
═══════════════════════════════════════════════════════════

## components/companies/CompanyCard.tsx:

'use client';

import Link from 'next/link';
import Image from 'next/image';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BadgeCheck } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import type { Company } from '@/lib/api/generated/schemas';

interface Props {
  company:        Company;
  onFindPartners?: (id: string) => void;
}

export function CompanyCard({ company, onFindPartners }: Props) {
  const techs = Object.entries(company.tech_stack ?? {})
    .filter(([, v]) => v)
    .map(([k]) => k)
    .slice(0, 5);

  return (
    <Card className="flex flex-col hover:shadow-lg transition-shadow duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="relative size-12 shrink-0 rounded-xl overflow-hidden bg-muted">
              {company.logo_url
                ? <Image src={company.logo_url} alt={company.name}
                    fill className="object-contain" sizes="48px" />
                : <span className="flex size-full items-center justify-center
                                   text-lg font-bold text-muted-foreground">
                    {company.name[0]}
                  </span>
              }
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1.5">
                <h3 className="truncate font-semibold">{company.name}</h3>
                {company.is_verified && (
                  <BadgeCheck className="size-4 shrink-0 text-blue-500"
                    aria-label="Верифицирована" />
                )}
              </div>
              <p className="truncate text-xs text-muted-foreground">
                {company.industry}
                {company.headquarters_city ? ` • ${company.headquarters_city}` : ''}
              </p>
            </div>
          </div>
          <Badge variant="secondary" className="shrink-0 text-xs">
            {company.employees_range}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="flex flex-1 flex-col gap-3">
        {(company.ai_summary ?? company.description) && (
          <p className="line-clamp-2 text-sm text-muted-foreground">
            {company.ai_summary ?? company.description}
          </p>
        )}

        {techs.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {techs.map(tech => (
              <Badge key={tech} variant="outline" className="text-xs">{tech}</Badge>
            ))}
          </div>
        )}

        {company.compatibility_score !== undefined && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Совместимость</span>
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
              <div
                className={cn(
                  'h-full rounded-full transition-all',
                  company.compatibility_score >= 0.8 ? 'bg-green-500' :
                  company.compatibility_score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                )}
                style={{ width: `${company.compatibility_score * 100}%` }}
              />
            </div>
            <span className="text-xs font-medium tabular-nums">
              {Math.round(company.compatibility_score * 100)}%
            </span>
          </div>
        )}

        <div className="mt-auto flex gap-2 pt-1">
          <Button variant="default" size="sm" className="flex-1" asChild>
            <Link href={`/companies/${company.id}`}>Подробнее</Link>
          </Button>
          <Button variant="outline" size="sm" className="flex-1"
            onClick={() => onFindPartners?.(company.id)}>
            Найти партнёров
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}


## components/companies/CompanyForm.tsx — Server Action форма:

'use client';

import { useActionState } from 'react';         // React 19
import { useFormStatus } from 'react-dom';       // React 19
import { createCompanyAction, type CreateCompanyState } from '@/app/actions/companies';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <Button type="submit" disabled={pending}>
      {pending ? 'Создание...' : 'Создать компанию'}
    </Button>
  );
}

export function CompanyForm() {
  const [state, formAction] = useActionState<CreateCompanyState, FormData>(
    createCompanyAction,
    {},
  );

  return (
    <form action={formAction} className="space-y-4">
      <div className="space-y-1.5">
        <Label htmlFor="name">Название</Label>
        <Input
          id="name" name="name" required
          aria-describedby={state.errors?.name ? 'name-error' : undefined}
        />
        {state.errors?.name && (
          <p id="name-error" className="text-sm text-red-500" role="alert">
            {state.errors.name[0]}
          </p>
        )}
      </div>

      {/* Остальные поля аналогично */}

      <SubmitButton />

      {state.message && (
        <p className="text-sm text-red-500" role="alert">{state.message}</p>
      )}
    </form>
  );
}


## components/partnerships/OutreachDialog.tsx:

'use client';

import { useState } from 'react';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Copy, RefreshCw, Mail } from 'lucide-react';
import { useGenerateOutreachMessage } from '@/lib/api/generated/ai';

type Style = 'formal' | 'friendly' | 'technical';

export function OutreachDialog({
  partnershipId, partnerName,
}: { partnershipId: string; partnerName: string }) {
  const [style, setStyle]     = useState<Style>('formal');
  const [message, setMessage] = useState('');
  const { mutate, isPending }  = useGenerateOutreachMessage();

  const generate = () => {
    mutate(
      { data: { partnership_id: partnershipId, style } },
      { onSuccess: (data) => setMessage(data.message) },
    );
  };

  const copy = () => {
    navigator.clipboard.writeText(message).then(() =>
      toast.success('Скопировано в буфер')
    );
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Mail className="mr-2 size-4" /> Написать письмо
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Письмо для {partnerName}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="flex gap-3">
            <Select value={style} onValueChange={v => setStyle(v as Style)}>
              <SelectTrigger className="w-44">
                <SelectValue placeholder="Стиль" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="formal">Официальный</SelectItem>
                <SelectItem value="friendly">Дружественный</SelectItem>
                <SelectItem value="technical">Технический</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={generate} disabled={isPending} className="gap-2">
              <RefreshCw className={`size-4 ${isPending ? 'animate-spin' : ''}`} />
              {message ? 'Перегенерировать' : 'Сгенерировать'}
            </Button>
          </div>
          {message && (
            <>
              <Textarea value={message} onChange={e => setMessage(e.target.value)}
                rows={12} className="resize-none font-mono text-sm" />
              <div className="flex justify-end">
                <Button variant="outline" onClick={copy} className="gap-2">
                  <Copy className="size-4" /> Копировать
                </Button>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 12: СТРАНИЦЫ
═══════════════════════════════════════════════════════════

## app/(dashboard)/companies/page.tsx:

/*
  Next.js 16: 'use cache' вместо fetch revalidate / PPR флага.
  Server Component получает данные напрямую через serverFetch.
  searchParams в Next.js 15+ — это Promise.
*/

import { Suspense } from 'react';
import { CompanyCard } from '@/components/companies/CompanyCard';
import { CompanyCardSkeleton } from '@/components/companies/CompanyCardSkeleton';
import { CompanySearch } from '@/components/companies/CompanySearch';
import { CompanyFilters } from '@/components/companies/CompanyFilters';
import { PageHeader } from '@/components/common/PageHeader';
import { serverFetch } from '@/lib/api/server';
import type { Metadata } from 'next';
import type { Company } from '@/lib/api/generated/schemas';
import type { PaginatedResponse } from '@/lib/api/generated/schemas';

interface PageProps {
  searchParams: Promise<Record<string, string>>;
}

export default async function CompaniesPage({ searchParams }: PageProps) {
  'use cache';                       // Next.js 16 Cache Components

  const params   = await searchParams;
  const page     = Number(params.page) || 1;
  const data     = await serverFetch<PaginatedResponse<Company>>(
    `/companies?${new URLSearchParams({ ...params, page: String(page), size: '12' })}`
  );

  return (
    <div className="space-y-6">
      <PageHeader title="Компании" description={`Найдено: ${data.total}`} />
      <div className="flex flex-col gap-3 sm:flex-row">
        <CompanySearch />
        <CompanyFilters />
      </div>
      <Suspense fallback={
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }, (_, i) => <CompanyCardSkeleton key={i} />)}
        </div>
      }>
        {data.items.length === 0
          ? <EmptyState title="Компании не найдены" description="Измените фильтры" />
          : <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {data.items.map(c => <CompanyCard key={c.id} company={c} />)}
            </div>
        }
      </Suspense>
      {data.pages > 1 && <Pagination currentPage={page} totalPages={data.pages} />}
    </div>
  );
}

export const metadata: Metadata = {
  title:       'Компании — ALGORITHMIC ARTS',
  description: 'Каталог технологических компаний для B2B-партнёрств',
};


## app/(dashboard)/layout.tsx:

import { Sidebar }   from '@/components/layout/Sidebar';
import { Header }    from '@/components/layout/Header';
import { RealtimeProvider } from '@/components/providers/RealtimeProvider';
import { auth }      from '@/lib/auth';
import { redirect }  from 'next/navigation';

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const session = await auth();
  if (!session)        redirect('/login');
  if (session.error === 'RefreshTokenError') redirect('/login?error=session_expired');

  return (
    <RealtimeProvider>
      <div className="flex h-svh overflow-hidden bg-background">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Header user={session.user} />
          <main className="flex-1 overflow-y-auto p-6" id="main-content">
            {children}
          </main>
        </div>
      </div>
    </RealtimeProvider>
  );
}


## app/layout.tsx:

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Toaster } from 'sonner';                          // Sonner, не react-hot-toast
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import { QueryProvider } from '@/components/providers/QueryProvider';
import '@/styles/globals.css';

const inter = Inter({
  subsets:  ['latin', 'cyrillic'],
  variable: '--font-sans',           // передаём в @theme через CSS переменную
  display:  'swap',
});

export const metadata: Metadata = {
  title: {
    default:  'ALGORITHMIC ARTS — Partnership Intelligence',
    template: '%s — ALGORITHMIC ARTS',
  },
  description:  'B2B платформа для поиска технологических партнёров',
  metadataBase: new URL('https://algorithmic-arts.ru'),
  openGraph: {
    type:   'website',
    locale: 'ru_RU',
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru" suppressHydrationWarning className={inter.variable}>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem
          disableTransitionOnChange>
          <QueryProvider>
            {children}
            <Toaster position="bottom-right" richColors closeButton />
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 13: УТИЛИТЫ
═══════════════════════════════════════════════════════════

## lib/utils/cn.ts:

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));


## lib/utils/formatters.ts:

export const formatMoney = (kopecks: number | null): string => {
  if (kopecks == null) return '—';
  const rub = kopecks / 100;
  if (rub >= 1e9) return `${(rub / 1e9).toFixed(1)} млрд ₽`;
  if (rub >= 1e6) return `${(rub / 1e6).toFixed(1)} млн ₽`;
  if (rub >= 1e3) return `${(rub / 1e3).toFixed(0)} тыс ₽`;
  return `${rub.toFixed(0)} ₽`;
};

export const formatDate = (iso: string): string =>
  new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
    .format(new Date(iso));

export const formatScore = (score: number): string =>
  `${Math.round(score * 100)}%`;

export const employeesLabel: Record<string, string> = {
  '1-10':    'до 10 чел',
  '11-50':   '11–50 чел',
  '51-200':  '51–200 чел',
  '201-500': '201–500 чел',
  '500+':    'более 500 чел',
};


═══════════════════════════════════════════════════════════
ЧАСТЬ 14: .ENV И TSCONFIG
═══════════════════════════════════════════════════════════

## .env.local.example:

NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8080/ws
API_GATEWAY_URL=http://localhost:8000
AUTH_SERVICE_URL=http://localhost:8001
AUTH_SECRET=min-32-chars-random-string-here
NEXTAUTH_URL=http://localhost:3000


## tsconfig.json:

{
  "compilerOptions": {
    "target":               "ES2022",
    "lib":                  ["dom", "dom.iterable", "ES2022"],
    "module":               "ESNext",
    "moduleResolution":     "bundler",
    "jsx":                  "preserve",
    "strict":               true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride":   true,
    "paths":                { "@/*": ["./*"] },
    "plugins":              [{ "name": "next" }],
    "skipLibCheck":         true
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules", "lib/api/generated/**"]  // orval генерирует, не проверяем
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 15: ТРЕБОВАНИЯ К РЕАЛИЗАЦИИ
═══════════════════════════════════════════════════════════

БЕЗОПАСНОСТЬ (обязательно):
- accessToken ТОЛЬКО в памяти (JWT в httpOnly cookie через Auth.js v5)
- refreshToken ТОЛЬКО в httpOnly cookie
- Никаких токенов в localStorage / sessionStorage / Zustand persist
- proxy.ts защищает /dashboard/* до рендера (не после)
- Security headers в next.config.ts (CSP, X-Frame-Options и др.)
- Авто-рефреш токена в jwt() callback Auth.js

АРХИТЕКТУРА Server vs Client:
- 'use client' только для: форм, onClick/onChange, хуков
  (useState, useEffect, TanStack Query, Zustand, WebSocket, Sonner)
- Server Components вызывают serverFetch() напрямую
- Мутации → Server Actions через useActionState() + useFormStatus()
- 'use cache' на страницах вместо устаревшего fetch(url, {next:{revalidate}})

API КЛИЕНТ:
- lib/api/generated/ — генерируется orval из OpenAPI, НЕ редактировать вручную
- Регенерация: npm run generate:api (при изменении бэкенда)
- Server Components используют serverFetch() из lib/api/server.ts
- Client Components используют сгенерированные хуки через TanStack Query

ПРОИЗВОДИТЕЛЬНОСТЬ:
- Все <img> → next/image, все <a href> → next/link
- Тяжёлые компоненты (recharts) → dynamic(() => import(...), { ssr: false })
- Skeleton для каждого async-сегмента (loading.tsx рядом с page.tsx)
- keepPreviousData в useQuery для плавной пагинации
- Tailwind v4: CSS-переменные вместо JIT-классов для динамических цветов

ДОСТУПНОСТЬ:
- Все интерактивные элементы: aria-label или видимый текст
- Формы: aria-describedby для ошибок, role="alert" для сообщений
- DialogTitle обязателен в каждом Dialog
- Цветовые индикаторы не только цветом (текст + значок)
- Skip link: <a href="#main-content"> в layout.tsx

ТЁМНАЯ ТЕМА:
- Через CSS-переменные в @theme (не через Tailwind dark: префикс где возможно)
- ThemeProvider из next-themes с attribute="class"
- Системная тема по умолчанию (defaultTheme="system")

ТЕСТИРОВАНИЕ:
- Playwright: e2e-тесты для критических флоу (логин, создание компании,
  поиск партнёров)
- Storybook: истории для CompanyCard, CompatibilityScore, OutreachDialog
- Типы: tsc --noEmit в CI

НЕ ИСПОЛЬЗОВАТЬ:
- axios (заменён на ofetch / нативный fetch)
- react-hot-toast (заменён на Sonner)
- socket.io-client (заменён на нативный WebSocket)
- next-themes устанавливать отдельно (встроен в shadcn/ui ThemeProvider)
- tailwind.config.ts (Tailwind v4 — конфигурация в globals.css)
- middleware.ts (Next.js 16 — переименован в proxy.ts)
- experimental.ppr (удалён в Next.js 16 — используй 'use cache')
- localStorage для токенов

```markdown
═══════════════════════════════════════════════════════════
ЧАСТЬ 16: АНАЛИТИКА — динамические компоненты с recharts
═══════════════════════════════════════════════════════════

## app/(dashboard)/analytics/page.tsx:

import { Suspense } from 'react';
import { serverFetch } from '@/lib/api/server';
import { PageHeader } from '@/components/common/PageHeader';
import { StatsCard } from '@/components/analytics/StatsCard';
import dynamic from 'next/dynamic';

// recharts тяжёлый — только client-side
const PartnershipChart = dynamic(
  () => import('@/components/analytics/PartnershipChart').then(m => m.PartnershipChart),
  { ssr: false, loading: () => <div className="h-64 animate-pulse rounded-lg bg-muted" /> }
);
const IndustryPieChart = dynamic(
  () => import('@/components/analytics/IndustryPieChart').then(m => m.IndustryPieChart),
  { ssr: false, loading: () => <div className="h-64 animate-pulse rounded-lg bg-muted" /> }
);

interface AnalyticsData {
  total_companies:    number;
  total_partnerships: number;
  active_partnerships: number;
  avg_compatibility:  number;
  partnerships_by_month: { month: string; count: number }[];
  partnerships_by_industry: { industry: string; count: number }[];
}

export default async function AnalyticsPage() {
  'use cache';

  const data = await serverFetch<AnalyticsData>('/analytics/summary');

  return (
    <div className="space-y-6">
      <PageHeader title="Аналитика" />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatsCard
          title="Компаний"
          value={data.total_companies}
          description="в базе данных"
        />
        <StatsCard
          title="Партнёрств"
          value={data.total_partnerships}
          description="всего создано"
        />
        <StatsCard
          title="Активных"
          value={data.active_partnerships}
          description="партнёрств сейчас"
          variant="success"
        />
        <StatsCard
          title="Ср. совместимость"
          value={`${Math.round(data.avg_compatibility * 100)}%`}
          description="по платформе"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border bg-card p-6">
          <h3 className="mb-4 font-semibold">Партнёрства по месяцам</h3>
          <PartnershipChart data={data.partnerships_by_month} />
        </div>
        <div className="rounded-xl border bg-card p-6">
          <h3 className="mb-4 font-semibold">По индустриям</h3>
          <IndustryPieChart data={data.partnerships_by_industry} />
        </div>
      </div>
    </div>
  );
}

export const metadata = { title: 'Аналитика' };


## components/analytics/StatsCard.tsx:

import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils/cn';

interface Props {
  title:       string;
  value:       string | number;
  description?: string;
  variant?:    'default' | 'success' | 'warning';
}

export function StatsCard({ title, value, description, variant = 'default' }: Props) {
  return (
    <Card>
      <CardContent className="pt-6">
        <p className="text-sm text-muted-foreground">{title}</p>
        <p className={cn(
          'mt-1 text-3xl font-bold tabular-nums',
          variant === 'success' && 'text-green-600 dark:text-green-400',
          variant === 'warning' && 'text-yellow-600 dark:text-yellow-400',
        )}>
          {value}
        </p>
        {description && (
          <p className="mt-1 text-xs text-muted-foreground">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}


## components/analytics/PartnershipChart.tsx:

'use client';

import {
  ResponsiveContainer, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip,
} from 'recharts';

interface Props {
  data: { month: string; count: number }[];
}

export function PartnershipChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="hsl(var(--primary))" stopOpacity={0.3} />
            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}   />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        <XAxis dataKey="month" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
        <Tooltip
          contentStyle={{
            background: 'hsl(var(--card))',
            border:     '1px solid hsl(var(--border))',
            borderRadius: '8px',
          }}
        />
        <Area
          type="monotone" dataKey="count" name="Партнёрства"
          stroke="hsl(var(--primary))" fill="url(#colorCount)" strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}


## components/analytics/IndustryPieChart.tsx:

'use client';

import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend,
} from 'recharts';

const COLORS = [
  'hsl(221 83% 53%)', 'hsl(142 71% 45%)', 'hsl(38 92% 50%)',
  'hsl(280 68% 60%)', 'hsl(12 76% 61%)',  'hsl(189 94% 43%)',
];

interface Props {
  data: { industry: string; count: number }[];
}

export function IndustryPieChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie
          data={data} dataKey="count" nameKey="industry"
          cx="50%" cy="50%" outerRadius={80} innerRadius={50}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background:   'hsl(var(--card))',
            border:       '1px solid hsl(var(--border))',
            borderRadius: '8px',
          }}
        />
        <Legend
          formatter={(value) => (
            <span className="text-xs text-muted-foreground">{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 17: НАСТРОЙКИ — подключение CRM
═══════════════════════════════════════════════════════════

## app/(dashboard)/settings/page.tsx:

import { serverFetch } from '@/lib/api/server';
import { PageHeader }  from '@/components/common/PageHeader';
import { CRMConnections } from '@/components/settings/CRMConnections';
import { ProfileForm }    from '@/components/settings/ProfileForm';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { Metadata } from 'next';

export default async function SettingsPage() {
  const connections = await serverFetch<CRMConnection[]>('/crm/connections');

  return (
    <div className="space-y-6">
      <PageHeader title="Настройки" />
      <Tabs defaultValue="profile">
        <TabsList>
          <TabsTrigger value="profile">Профиль</TabsTrigger>
          <TabsTrigger value="crm">CRM интеграции</TabsTrigger>
        </TabsList>
        <TabsContent value="profile" className="mt-6">
          <ProfileForm />
        </TabsContent>
        <TabsContent value="crm" className="mt-6">
          <CRMConnections connections={connections} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export const metadata: Metadata = { title: 'Настройки' };


## components/settings/CRMConnections.tsx:

'use client';

import { Badge }  from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle }
  from '@/components/ui/card';
import { CheckCircle, Link as LinkIcon, Unlink } from 'lucide-react';
import { toast } from 'sonner';

const CRM_LIST = [
  { type: 'amocrm',    label: 'amoCRM',      description: 'Основная CRM для российского рынка' },
  { type: 'bitrix24',  label: 'Битрикс24',   description: 'Корпоративный портал и CRM'         },
  { type: 'megaplan',  label: 'Мегаплан',    description: 'CRM и управление задачами'           },
  { type: 'hubspot',   label: 'HubSpot',     description: 'Международная CRM платформа'         },
  { type: 'salesforce',label: 'Salesforce',  description: 'Enterprise CRM'                      },
  { type: 'pipedrive', label: 'Pipedrive',   description: 'CRM для отделов продаж'              },
];

interface CRMConnection { id: string; crm_type: string; is_active: boolean; }
interface Props { connections: CRMConnection[]; }

export function CRMConnections({ connections }: Props) {
  const connected = new Set(connections.map(c => c.crm_type));

  const handleConnect = async (crmType: string) => {
    const res  = await fetch(`/api/v1/crm/connect/${crmType}`, { method: 'POST' });
    const data = await res.json() as { authorization_url?: string };
    if (data.authorization_url) {
      window.location.href = data.authorization_url;
    }
  };

  const handleDisconnect = async (crmType: string) => {
    const conn = connections.find(c => c.crm_type === crmType);
    if (!conn) return;
    await fetch(`/api/v1/crm/connections/${conn.id}`, { method: 'DELETE' });
    toast.success(`${crmType} отключён`);
    window.location.reload();
  };

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {CRM_LIST.map(crm => (
        <Card key={crm.type}>
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <CardTitle className="text-base">{crm.label}</CardTitle>
              {connected.has(crm.type)
                ? <Badge className="bg-green-100 text-green-800
                                    dark:bg-green-900 dark:text-green-200 gap-1">
                    <CheckCircle className="size-3" /> Подключено
                  </Badge>
                : <Badge variant="secondary">Не подключено</Badge>
              }
            </div>
            <CardDescription>{crm.description}</CardDescription>
          </CardHeader>
          <CardContent>
            {connected.has(crm.type)
              ? <Button variant="outline" size="sm" className="w-full gap-2"
                  onClick={() => handleDisconnect(crm.type)}>
                  <Unlink className="size-4" /> Отключить
                </Button>
              : <Button variant="default" size="sm" className="w-full gap-2"
                  onClick={() => handleConnect(crm.type)}>
                  <LinkIcon className="size-4" /> Подключить
                </Button>
            }
          </CardContent>
        </Card>
      ))}
    </div>
  );
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 18: LANDING PAGE
═══════════════════════════════════════════════════════════

## app/page.tsx:

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge }  from '@/components/ui/badge';
import { ArrowRight, Brain, Network, Zap } from 'lucide-react';
import type { Metadata } from 'next';

const FEATURES = [
  {
    icon: Brain,
    title: 'AI-анализ совместимости',
    description: 'Нейросеть оценивает синергию технологических стеков, бизнес-моделей и рыночных позиций',
  },
  {
    icon: Network,
    title: 'Граф партнёрств',
    description: 'Визуализация экосистемы партнёров и выявление скрытых связей между компаниями',
  },
  {
    icon: Zap,
    title: 'Авто-аутрич',
    description: 'Генерация персонализированных писем партнёрам с учётом контекста и стиля коммуникации',
  },
];

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Nav */}
      <header className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <span className="font-bold text-lg tracking-tight">ALGORITHMIC ARTS</span>
          <div className="flex items-center gap-3">
            <Button variant="ghost" asChild>
              <Link href="/login">Войти</Link>
            </Button>
            <Button asChild>
              <Link href="/register">Начать бесплатно</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="flex-1 container mx-auto px-4 py-24 text-center">
        <Badge variant="secondary" className="mb-6">
          AI-powered Partnership Intelligence
        </Badge>
        <h1 className="mx-auto max-w-3xl text-5xl font-bold tracking-tight
                       text-foreground lg:text-6xl">
          Найди идеального технологического партнёра
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
          Платформа для B2B-партнёрств: AI анализирует тысячи компаний
          и находит тех, с кем ваш продукт даст синергию.
        </p>
        <div className="mt-10 flex justify-center gap-4">
          <Button size="lg" asChild>
            <Link href="/register">
              Начать бесплатно <ArrowRight className="ml-2 size-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/login">Войти в платформу</Link>
          </Button>
        </div>
      </section>

      {/* Features */}
      <section className="border-t bg-muted/40 py-24">
        <div className="container mx-auto px-4">
          <h2 className="mb-12 text-center text-3xl font-bold">Как это работает</h2>
          <div className="grid gap-8 md:grid-cols-3">
            {FEATURES.map(({ icon: Icon, title, description }) => (
              <div key={title} className="rounded-xl border bg-card p-6 text-center">
                <div className="mx-auto mb-4 flex size-12 items-center justify-center
                                rounded-lg bg-primary/10">
                  <Icon className="size-6 text-primary" />
                </div>
                <h3 className="mb-2 font-semibold">{title}</h3>
                <p className="text-sm text-muted-foreground">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        © 2026 ALGORITHMIC ARTS. Все права защищены.
      </footer>
    </div>
  );
}

export const metadata: Metadata = {
  title: 'ALGORITHMIC ARTS — AI Partnership Intelligence Platform',
};


═══════════════════════════════════════════════════════════
ЧАСТЬ 19: ОБЩИЕ КОМПОНЕНТЫ
═══════════════════════════════════════════════════════════

## components/common/PageHeader.tsx:

interface Props {
  title:        string;
  description?: string;
  action?:      React.ReactNode;
}

export function PageHeader({ title, description, action }: Props) {
  return (
    <div className="flex items-start justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        {description && (
          <p className="mt-1 text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}


## components/common/EmptyState.tsx:

import { PackageSearch } from 'lucide-react';

interface Props { title: string; description?: string; action?: React.ReactNode; }

export function EmptyState({ title, description, action }: Props) {
  return (
    <div className="flex flex-col items-center justify-center
                    rounded-xl border border-dashed py-16 text-center">
      <PackageSearch className="mb-4 size-10 text-muted-foreground" />
      <p className="font-semibold">{title}</p>
      {description && (
        <p className="mt-1 text-sm text-muted-foreground">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}


## components/common/RealtimeIndicator.tsx:

'use client';

import { useRealtimeUpdates } from '@/lib/hooks/useRealtimeUpdates';
import { cn } from '@/lib/utils/cn';

export function RealtimeIndicator() {
  const { status } = useRealtimeUpdates();
  return (
    <div className="flex items-center gap-1.5" title={`WebSocket: ${status}`}>
      <span className={cn(
        'size-2 rounded-full',
        status === 'connected'    && 'bg-green-500 animate-pulse',
        status === 'connecting'   && 'bg-yellow-500 animate-pulse',
        status === 'disconnected' && 'bg-red-500',
      )} />
      <span className="hidden text-xs text-muted-foreground sm:inline">
        {status === 'connected' ? 'Live' : status === 'connecting' ? 'Подключение...' : 'Офлайн'}
      </span>
    </div>
  );
}


## components/layout/Header.tsx:

import { ThemeToggle }       from './ThemeToggle';
import { RealtimeIndicator } from '@/components/common/RealtimeIndicator';
import { Button }            from '@/components/ui/button';
import { signOut }           from '@/lib/auth';
import { LogOut, User }      from 'lucide-react';
import type { Session }      from 'next-auth';

interface Props { user: Session['user']; }

export function Header({ user }: Props) {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between
                       border-b bg-background px-6 gap-4">
      <a href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50
                   focus:rounded focus:bg-background focus:px-3 focus:py-2
                   focus:text-sm focus:outline-none focus:ring-2 focus:ring-ring">
        Перейти к содержимому
      </a>

      <div className="flex items-center gap-3">
        <RealtimeIndicator />
      </div>

      <div className="flex items-center gap-2">
        <ThemeToggle />
        <div className="flex items-center gap-2 text-sm">
          <User className="size-4 text-muted-foreground" />
          <span className="hidden text-muted-foreground sm:inline">{user.name}</span>
        </div>
        <form action={async () => { 'use server'; await signOut({ redirectTo: '/login' }); }}>
          <Button type="submit" variant="ghost" size="icon" aria-label="Выйти">
            <LogOut className="size-4" />
          </Button>
        </form>
      </div>
    </header>
  );
}


## components/layout/Sidebar.tsx:

'use client';

import Link     from 'next/link';
import { usePathname } from 'next/navigation';
import { cn }   from '@/lib/utils/cn';
import {
  Building2, Handshake, BarChart2, Settings, Sparkles,
} from 'lucide-react';

const NAV = [
  { href: '/companies',                    label: 'Компании',       icon: Building2  },
  { href: '/partnerships',                 label: 'Партнёрства',    icon: Handshake  },
  { href: '/partnerships/recommendations', label: 'AI-подборка',    icon: Sparkles   },
  { href: '/analytics',                    label: 'Аналитика',      icon: BarChart2  },
  { href: '/settings',                     label: 'Настройки',      icon: Settings   },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="flex w-56 shrink-0 flex-col border-r bg-background">
      <div className="flex h-14 items-center border-b px-4">
        <span className="font-bold text-sm tracking-tight">ALGORITHMIC ARTS</span>
      </div>
      <nav className="flex-1 space-y-1 p-3" aria-label="Основная навигация">
        {NAV.map(({ href, label, icon: Icon }) => (
          <Link
            key={href} href={href}
            className={cn(
              'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
              pathname === href || pathname.startsWith(href + '/')
                ? 'bg-primary/10 text-primary font-medium'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground',
            )}
            aria-current={pathname === href ? 'page' : undefined}
          >
            <Icon className="size-4 shrink-0" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}


## components/layout/ThemeToggle.tsx:

'use client';

import { useTheme } from 'next-themes';
import { Button }   from '@/components/ui/button';
import { Sun, Moon, Monitor } from 'lucide-react';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const next = theme === 'light' ? 'dark' : theme === 'dark' ? 'system' : 'light';
  const Icon = theme === 'light' ? Sun : theme === 'dark' ? Moon : Monitor;
  return (
    <Button variant="ghost" size="icon" onClick={() => setTheme(next)}
      aria-label="Переключить тему">
      <Icon className="size-4" />
    </Button>
  );
}


## components/providers/QueryProvider.tsx:

'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        retry:              1,
        staleTime:          30_000,
        refetchOnWindowFocus: false,
      },
    },
  }));
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}


## components/providers/RealtimeProvider.tsx:

'use client';

import { createContext, useContext, useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

type Status = 'connecting' | 'connected' | 'disconnected';
const Ctx = createContext<{ status: Status }>({ status: 'disconnected' });
export const useRealtimeStatus = () => useContext(Ctx);

export function RealtimeProvider({ children }: { children: React.ReactNode }) {
  const qc      = useQueryClient();
  const wsRef   = useRef<WebSocket | null>(null);
  const retryRef = useRef<ReturnType<typeof setTimeout>>(null);
  const [status, setStatus] = useState<Status>('disconnected');

  useEffect(() => {
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8080/ws';

    function connect() {
      setStatus('connecting');
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;
      ws.onopen  = () => setStatus('connected');
      ws.onerror = () => ws.close();
      ws.onmessage = ({ data }) => {
        try {
          const msg = JSON.parse(data as string) as { type: string };
          if (msg.type === 'company.created' || msg.type === 'company.updated')
            void qc.invalidateQueries({ queryKey: ['companies'] });
          if (msg.type === 'partnership.matched') {
            void qc.invalidateQueries({ queryKey: ['partnerships'] });
            toast.success('Найдено новое партнёрство!', {
              description: 'Проверь раздел AI-подборка',
              action: {
                label:   'Открыть',
                onClick: () => { window.location.href = '/partnerships/recommendations'; },
              },
            });
          }
        } catch { /* skip */ }
      };
      ws.onclose = () => {
        setStatus('disconnected');
        retryRef.current = setTimeout(connect, 5_000);
      };
    }

    connect();
    return () => {
      clearTimeout(retryRef.current!);
      wsRef.current?.close();
    };
  }, [qc]);

  return <Ctx.Provider value={{ status }}>{children}</Ctx.Provider>;
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 20: SKELETON И ERROR КОМПОНЕНТЫ
═══════════════════════════════════════════════════════════

## components/companies/CompanyCardSkeleton.tsx:

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export function CompanyCardSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <Skeleton className="size-12 rounded-xl" />
          <div className="space-y-1.5 flex-1">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-3 w-24" />
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-4/5" />
        <div className="flex gap-1.5">
          {Array.from({ length: 4 }, (_, i) => (
            <Skeleton key={i} className="h-5 w-14 rounded-full" />
          ))}
        </div>
        <div className="flex gap-2 pt-1">
          <Skeleton className="h-8 flex-1 rounded-md" />
          <Skeleton className="h-8 flex-1 rounded-md" />
        </div>
      </CardContent>
    </Card>
  );
}


## app/(dashboard)/companies/loading.tsx:

import { CompanyCardSkeleton } from '@/components/companies/CompanyCardSkeleton';

export default function CompaniesLoading() {
  return (
    <div className="space-y-6">
      <div className="h-8 w-48 animate-pulse rounded bg-muted" />
      <div className="flex gap-3">
        <div className="h-9 w-64 animate-pulse rounded-md bg-muted" />
        <div className="h-9 w-32 animate-pulse rounded-md bg-muted" />
      </div>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }, (_, i) => <CompanyCardSkeleton key={i} />)}
      </div>
    </div>
  );
}


## app/(dashboard)/companies/error.tsx:

'use client';

import { useEffect } from 'react';
import { Button }    from '@/components/ui/button';
import { AlertCircle } from 'lucide-react';

export default function CompaniesError({
  error, reset,
}: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { console.error(error); }, [error]);
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <AlertCircle className="mb-4 size-10 text-destructive" />
      <h2 className="font-semibold">Не удалось загрузить компании</h2>
      <p className="mt-1 text-sm text-muted-foreground">{error.message}</p>
      <Button className="mt-4" onClick={reset}>Попробовать снова</Button>
    </div>
  );
}


## app/not-found.tsx:

import Link   from 'next/link';
import { Button } from '@/components/ui/button';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
      <p className="text-8xl font-bold text-muted-foreground/30">404</p>
      <h1 className="text-2xl font-bold">Страница не найдена</h1>
      <p className="text-muted-foreground">Запрошенная страница не существует или была перемещена</p>
      <Button asChild>
        <Link href="/companies">На главную</Link>
      </Button>
    </div>
  );
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 21: PLAYWRIGHT E2E ТЕСТЫ
═══════════════════════════════════════════════════════════

## playwright.config.ts:

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir:     './e2e',
  fullyParallel: true,
  forbidOnly:  !!process.env.CI,
  retries:     process.env.CI ? 2 : 0,
  reporter:    'html',
  use: {
    baseURL:   'http://localhost:3000',
    trace:     'on-first-retry',
    locale:    'ru-RU',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile',   use: { ...devices['Pixel 7'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url:     'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});


## e2e/auth.spec.ts:

import { test, expect } from '@playwright/test';

test.describe('Авторизация', () => {
  test('успешный вход', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Пароль').fill('password123');
    await page.getByRole('button', { name: 'Войти' }).click();
    await expect(page).toHaveURL('/companies');
  });

  test('ошибка при неверном пароле', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Пароль').fill('wrong');
    await page.getByRole('button', { name: 'Войти' }).click();
    await expect(page.getByRole('alert')).toBeVisible();
    await expect(page).toHaveURL('/login');
  });

  test('редирект незалогиненного пользователя на /login', async ({ page }) => {
    await page.goto('/companies');
    await expect(page).toHaveURL(/\/login/);
  });
});


## e2e/companies.spec.ts:

import { test, expect } from '@playwright/test';

// Переиспользуем сессию чтобы не логиниться перед каждым тестом
test.use({ storageState: 'e2e/.auth/user.json' });

test.describe('Компании', () => {
  test('список компаний загружается', async ({ page }) => {
    await page.goto('/companies');
    await expect(page.getByRole('heading', { name: 'Компании' })).toBeVisible();
    // Ждём хотя бы одну карточку
    await expect(page.locator('[data-testid="company-card"]').first()).toBeVisible();
  });

  test('поиск фильтрует компании', async ({ page }) => {
    await page.goto('/companies');
    await page.getByPlaceholder('Поиск компаний...').fill('Яндекс');
    await page.waitForTimeout(350);   // debounce 300ms
    const cards = page.locator('[data-testid="company-card"]');
    await expect(cards.first()).toContainText('Яндекс');
  });

  test('создание новой компании', async ({ page }) => {
    await page.goto('/companies/new');
    await page.getByLabel('Название').fill('Test SaaS Company');
    await page.getByLabel('Индустрия').selectOption('saas');
    await page.getByLabel('Размер').selectOption('11-50');
    await page.getByRole('button', { name: 'Создать компанию' }).click();
    await expect(page).toHaveURL(/\/companies\//);
    await expect(page.getByText('Test SaaS Company')).toBeVisible();
  });
});


## e2e/partnerships.spec.ts:

import { test, expect } from '@playwright/test';

test.use({ storageState: 'e2e/.auth/user.json' });

test.describe('Партнёрства', () => {
  test('AI-рекомендации загружаются', async ({ page }) => {
    await page.goto('/partnerships/recommendations');
    await expect(page.getByRole('heading', { name: /рекомендации/i })).toBeVisible();
    await expect(
      page.locator('[data-testid="partnership-card"]').first()
    ).toBeVisible({ timeout: 10_000 });  // AI может отвечать медленно
  });

  test('генерация письма через OutreachDialog', async ({ page }) => {
    await page.goto('/partnerships/recommendations');
    await page.locator('[data-testid="partnership-card"]').first()
      .getByRole('button', { name: 'Написать письмо' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.getByRole('button', { name: 'Сгенерировать' }).click();
    await expect(page.getByRole('textbox')).not.toBeEmpty({ timeout: 15_000 });
  });
});


## e2e/setup/auth.setup.ts — глобальная авторизация для тестов:

import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../.auth/user.json');

setup('авторизоваться и сохранить сессию', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.E2E_EMAIL ?? 'test@example.com');
  await page.getByLabel('Пароль').fill(process.env.E2E_PASSWORD ?? 'password123');
  await page.getByRole('button', { name: 'Войти' }).click();
  await expect(page).toHaveURL('/companies');
  await page.context().storageState({ path: authFile });
});


═══════════════════════════════════════════════════════════
ЧАСТЬ 22: STORYBOOK
═══════════════════════════════════════════════════════════

## .storybook/main.ts:

import type { StorybookConfig } from '@storybook/nextjs';

export default {
  stories:   ['../components/**/*.stories.tsx'],
  addons:    ['@storybook/addon-essentials', '@storybook/addon-a11y'],
  framework: { name: '@storybook/nextjs', options: {} },
  staticDirs: ['../public'],
} satisfies StorybookConfig;


## components/companies/CompanyCard.stories.tsx:

import type { Meta, StoryObj } from '@storybook/react';
import { CompanyCard } from './CompanyCard';

const meta: Meta<typeof CompanyCard> = {
  title:     'Companies/CompanyCard',
  component: CompanyCard,
  parameters: { layout: 'padded' },
};
export default meta;

type Story = StoryObj<typeof CompanyCard>;

const base = {
  id: '1', name: 'Яндекс', slug: 'yandex', industry: 'Технологии',
  sub_industries: [], tech_stack: { python: true, go: true, react: true, k8s: true },
  website: 'https://yandex.ru', logo_url: null,
  headquarters_city: 'Москва', headquarters_country: 'RU',
  employees_range: '500+' as const, funding_stage: 'ipo' as const,
  funding_total: null, is_verified: true, api_available: true,
  ai_summary: 'Крупнейшая российская технологическая компания',
  ai_tags: ['поиск', 'облако', 'AI'],
  description: null, created_at: '2024-01-01', updated_at: '2024-01-01',
};

export const Default: Story        = { args: { company: base } };
export const WithScore: Story      = { args: { company: { ...base, compatibility_score: 0.87 } } };
export const LowScore: Story       = { args: { company: { ...base, compatibility_score: 0.42 } } };
export const NotVerified: Story    = { args: { company: { ...base, is_verified: false } } };
export const NoLogo: Story         = { args: { company: { ...base, logo_url: null } } };


## components/partnerships/CompatibilityScore.stories.tsx:

import type { Meta, StoryObj } from '@storybook/react';
import { CompatibilityScore } from './CompatibilityScore';

const meta: Meta<typeof CompatibilityScore> = {
  title:     'Partnerships/CompatibilityScore',
  component: CompatibilityScore,
  parameters: { layout: 'centered' },
  argTypes:  { score: { control: { type: 'range', min: 0, max: 1, step: 0.01 } } },
};
export default meta;

type Story = StoryObj<typeof CompatibilityScore>;

export const Excellent: Story = { args: { score: 0.92 } };
export const Good: Story      = { args: { score: 0.71 } };
export const Low: Story       = { args: { score: 0.38 } };
export const Small: Story     = { args: { score: 0.85, size: 'sm' } };
export const NoLabel: Story   = { args: { score: 0.75, showLabel: false } };


═══════════════════════════════════════════════════════════
ЧАСТЬ 23: ИТОГОВЫЙ ЧЕКЛИСТ
═══════════════════════════════════════════════════════════

После реализации убедись что выполнено ВСЁ:

БЕЗОПАСНОСТЬ:
  [ ] proxy.ts защищает все /dashboard/* роуты
  [ ] Нет ни одного токена в localStorage / Zustand persist
  [ ] Security headers возвращаются для всех роутов (проверить curl -I)
  [ ] Auth.js session.error обрабатывается → редирект на /login
  [ ] Форма логина: rate limiting на уровне бэкенда (фронт не блокирует)

АРХИТЕКТУРА:
  [ ] 'use client' только там где реально нужно
  [ ] Server Components вызывают serverFetch() (не Axios, не orval хуки)
  [ ] Все мутации форм через Server Actions + useActionState()
  [ ] lib/api/generated/ не редактируется вручную
  [ ] npm run generate:api работает без ошибок

TAILWIND V4:
  [ ] Нет файла tailwind.config.ts
  [ ] Все токены в globals.css через @theme { }
  [ ] Dark mode работает через .dark класс и CSS-переменные
  [ ] postcss.config.mjs содержит @tailwindcss/postcss плагин

ПРОИЗВОДИТЕЛЬНОСТЬ:
  [ ] Все <img> заменены на next/image
  [ ] Все <a href="..."> заменены на next/link
  [ ] recharts импортируется через dynamic() с ssr: false
  [ ] loading.tsx есть рядом с каждым page.tsx
  [ ] 'use cache' используется на тяжёлых страницах (Next.js 16)

ДОСТУПНОСТЬ:
  [ ] Skip link в Header.tsx (<a href="#main-content">)
  [ ] <main id="main-content"> в dashboard layout
  [ ] Все иконки-кнопки имеют aria-label
  [ ] Ошибки форм имеют role="alert" и aria-describedby
  [ ] Playwright: нет warnings от @axe-core/playwright

ТЕСТЫ:
  [ ] npm run test:e2e — все тесты зелёные
  [ ] npm run storybook — все истории рендерятся без ошибок
  [ ] npm run type-check — 0 ошибок TypeScript

ЗАПУСК ПРОЕКТА:
  [ ] npm install
  [ ] npm run generate:api  (требует запущенный бэкенд)
  [ ] npm run dev           (http://localhost:3000)
  [ ] npm run build         (production build без ошибок)