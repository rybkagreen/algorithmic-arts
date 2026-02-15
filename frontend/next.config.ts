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
  headers() {
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

  rewrites() {
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