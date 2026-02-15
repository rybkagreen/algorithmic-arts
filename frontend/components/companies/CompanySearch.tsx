'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { useFilterStore } from '@/lib/stores/filterStore';

export function CompanySearch() {
  const [searchTerm, setSearchTerm] = useState('');
  const setFilter = useFilterStore(s => s.setCompanyFilter);

  // Debounce search term
  useEffect(() => {
    const handler = setTimeout(() => {
      setFilter('search', searchTerm || undefined);
    }, 300);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm, setFilter]);

  return (
    <div className="relative">
      <Input
        placeholder="Поиск компаний..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="pl-10"
      />
      <svg 
        className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </div>
  );
}