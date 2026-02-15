'use client';

import { Button } from '@/components/ui/button';
import { Home, Users, TrendingUp, Settings, BarChart3 } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Sidebar() {
  const pathname = usePathname();
  
  const navItems = [
    { href: '/dashboard/companies', label: 'Компании', icon: Home },
    { href: '/dashboard/partnerships', label: 'Партнёрства', icon: Users },
    { href: '/dashboard/partnerships/recommendations', label: 'Рекомендации', icon: TrendingUp },
    { href: '/dashboard/analytics', label: 'Аналитика', icon: BarChart3 },
    { href: '/dashboard/settings', label: 'Настройки', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-card border-r border-border flex flex-col">
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-bold">ALGORITHMIC ARTS</h2>
      </div>
      
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Button
              key={item.href}
              asChild
              variant={isActive ? "secondary" : "ghost"}
              className="w-full justify-start"
            >
              <Link href={item.href}>
                <item.icon className="mr-2 h-4 w-4" />
                {item.label}
              </Link>
            </Button>
          );
        })}
      </nav>
    </aside>
  );
}