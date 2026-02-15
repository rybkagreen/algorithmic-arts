'use client';

import { useFilterStore } from '@/lib/stores/filterStore';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';

export function CompanyFilters() {
  const filters = useFilterStore(s => s.companyFilters);
  const setFilter = useFilterStore(s => s.setCompanyFilter);
  const resetFilters = useFilterStore(s => s.resetCompanyFilters);

  return (
    <div className="flex flex-wrap items-center gap-4 mb-6">
      <div className="flex-1 min-w-[200px]">
        <Input
          placeholder="Поиск по названию..."
          value={filters.search || ''}
          onChange={(e) => setFilter('search', e.target.value)}
          className="h-10"
        />
      </div>
      
      <div className="min-w-[150px]">
        <Select 
          value={filters.industry || ''} 
          onValueChange={(value) => setFilter('industry', value || undefined)}
        >
          <SelectTrigger className="h-10">
            <SelectValue placeholder="Отрасль" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">Все отрасли</SelectItem>
            <SelectItem value="it">IT и программное обеспечение</SelectItem>
            <SelectItem value="finance">Финансы и банки</SelectItem>
            <SelectItem value="healthcare">Здравоохранение</SelectItem>
            <SelectItem value="education">Образование</SelectItem>
            <SelectItem value="manufacturing">Производство</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div className="min-w-[150px]">
        <Select 
          value={filters.employees_range || ''} 
          onValueChange={(value) => setFilter('employees_range', value || undefined)}
        >
          <SelectTrigger className="h-10">
            <SelectValue placeholder="Размер компании" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">Все размеры</SelectItem>
            <SelectItem value="1-10">1-10 сотрудников</SelectItem>
            <SelectItem value="11-50">11-50 сотрудников</SelectItem>
            <SelectItem value="51-200">51-200 сотрудников</SelectItem>
            <SelectItem value="201-500">201-500 сотрудников</SelectItem>
            <SelectItem value="500+">500+ сотрудников</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <Button variant="outline" size="sm" onClick={resetFilters}>
        <X className="mr-2 h-4 w-4" />
        Сбросить
      </Button>
    </div>
  );
}