import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import React from 'react';
import './styles/globals.css';
import { QueryProvider } from '@/components/providers/QueryProvider';
import { RealtimeProvider } from '@/components/providers/RealtimeProvider';
import { ThemeProvider } from '@/components/providers/ThemeProvider';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });

export const metadata: Metadata = {
  title: {
    default: 'ALGORITHMIC ARTS',
    template: '%s | ALGORITHMIC ARTS',
  },
  description: 'AI-powered Partnership Intelligence Platform for Russian B2B SaaS',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru" className={inter.variable}>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <QueryProvider>
            <RealtimeProvider>
              {children}
            </RealtimeProvider>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}