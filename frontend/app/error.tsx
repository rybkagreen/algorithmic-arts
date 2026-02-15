'use client';

import { useEffect } from 'react';
import Link from 'next/link';

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="text-center max-w-md">
        <h1 className="text-6xl font-bold mb-4 text-red-500">Ошибка</h1>
        <h2 className="text-2xl font-semibold mb-2">Что-то пошло не так</h2>
        <p className="text-muted-foreground mb-6">
          Произошла ошибка при загрузке страницы. Пожалуйста, попробуйте обновить страницу или вернуться назад.
        </p>
        
        <div className="space-y-3">
          {error.message && (
            <div className="p-4 bg-red-50 text-red-700 rounded-lg text-sm">
              {error.message}
            </div>
          )}
          
          <div className="flex gap-3">
            <button
              onClick={reset}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              Повторить попытку
            </button>
            <Link 
              href="/" 
              className="px-6 py-3 border border-border hover:border-primary text-muted-foreground hover:text-primary rounded-lg font-medium transition-colors"
            >
              На главную
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}