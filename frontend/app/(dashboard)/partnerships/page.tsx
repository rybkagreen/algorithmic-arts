import { PartnershipCard } from '@/components/partnerships/PartnershipCard';
import { PartnershipCardSkeleton } from '@/components/partnerships/PartnershipCardSkeleton';
import { Suspense } from 'react';

export default function PartnershipsPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Партнёрства</h1>
          <p className="text-muted-foreground">
            Управление текущими партнёрствами и отслеживание статусов
          </p>
        </div>
      </div>

      <Suspense fallback={
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <PartnershipCardSkeleton key={i} />
          ))}
        </div>
      }>
        <PartnershipsList />
      </Suspense>
    </div>
  );
}

function PartnershipsList() {
  // Simulated data since API not available yet
  const partnerships = [
    {
      id: '1',
      company_name: 'Технологии Будущего',
      partner_name: 'Цифровая Экономика',
      status: 'active',
      compatibility_score: 0.85,
      last_updated: '2026-02-14T10:30:00Z',
      description: 'Сотрудничество в области enterprise решений для финансового сектора',
    },
    {
      id: '2',
      company_name: 'МедТех Инновации',
      partner_name: 'Технологии Будущего',
      status: 'pending',
      compatibility_score: 0.72,
      last_updated: '2026-02-14T09:15:00Z',
      description: 'Предложение по интеграции медицинских решений с enterprise платформой',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {partnerships.map((partnership) => (
        <PartnershipCard key={partnership.id} partnership={partnership} />
      ))}
    </div>
  );
}