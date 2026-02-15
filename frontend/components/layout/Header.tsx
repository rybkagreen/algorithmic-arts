'use client';

import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/layout/ThemeToggle';
import { signOut } from '@/lib/auth';
import { User } from 'lucide-react';

export function Header() {
  return (
    <header className="border-b border-border bg-card">
      <div className="flex items-center justify-between h-16 px-4 md:px-6">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold">ALGORITHMIC ARTS</h1>
        </div>
        
        <div className="flex items-center space-x-4">
          <ThemeToggle />
          <Button variant="ghost" size="icon" onClick={() => signOut()}>
            <User className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}