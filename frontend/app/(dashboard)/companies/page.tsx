import { CompanyCard } from '@/components/companies/CompanyCard';
import { CompanyCardSkeleton } from '@/components/companies/CompanyCardSkeleton';
import { CompanyFilters } from '@/components/companies/CompanyFilters';
import { CompanySearch } from '@/components/companies/CompanySearch';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Suspense } from 'react';

export default function CompaniesPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Компании</h1>
          <p className="text-muted-foreground">
            Управление базой компаний и поиск партнёрств
          </p>
        </div>
        <Button asChild>
          <a href="/dashboard/companies/new">Добавить компанию</a>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Поиск и фильтрация</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <CompanySearch />
            <CompanyFilters />
          </div>
        </CardContent>
      </Card>

      <Suspense fallback={
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <CompanyCardSkeleton key={i} />
          ))}
        </div>
      }>
        <CompaniesList />
      </Suspense>
    </div>
  );
}

function CompaniesList() {
  // In a real implementation, this would be an async Server Component that fetches data
  // For now, we'll simulate with static data since we don't have the API yet
  const companies = [
    {
      id: '1',
      name: 'Технологии Будущего',
      industry: 'IT и программное обеспечение',
      logo_url: '',
      is_verified: true,
      employees_range: '51-200',
      funding_stage: 'series_a',
      tech_stack: { react: true, nodejs: true, postgresql: true },
      description: 'Разработка enterprise решений для российского рынка',
    },
    {
      id: '2',
      name: 'Цифровая Экономика',
      industry: 'Финансы и банки',
      logo_url: '',
      is_verified: false,
      employees_range: '11-50',
      funding_stage: 'seed',
      tech_stack: { python: true, django: true, redis: true },
      description: 'Fintech платформа для малого бизнеса',
    },
    {
      id: '3',
      name: 'МедТех Инновации',
      industry: 'Здравоохранение',
      logo_url: '',
      is_verified: true,
      employees_range: '201-500',
      funding_stage: 'series_b',
      tech_stack: { java: true, spring: true, mongodb: true },
      description: 'Инновационные решения для медицинских учреждений',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {companies.map((company) => (
        <CompanyCard 
          key={company.id} 
          company={company}
          onFindPartners={(id) => console.log('Find partners for:', id)}
        />
      ))}
    </div>
  );
}