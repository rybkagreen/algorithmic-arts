import React from 'react';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="max-w-4xl w-full text-center">
        <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">
          ALGORITHMIC ARTS
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          AI-powered Partnership Intelligence Platform for Russian B2B SaaS companies
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link 
            href="/login" 
            className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            Войти в систему
          </Link>
          <Link 
            href="/register" 
            className="px-8 py-3 border border-muted-foreground hover:border-primary text-muted-foreground hover:text-primary rounded-lg font-medium transition-colors"
          >
            Зарегистрироваться
          </Link>
        </div>
      </div>
    </div>
  );
}