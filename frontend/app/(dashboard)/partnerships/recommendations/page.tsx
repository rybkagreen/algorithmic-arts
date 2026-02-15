import { CompatibilityScore } from '@/components/partnerships/CompatibilityScore';
import { OutreachDialog } from '@/components/partnerships/OutreachDialog';
import { Badge } from '@/components/ui/badge';

export default function RecommendationsPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Рекомендации</h1>
          <p className="text-muted-foreground">
            Автоматически найденные потенциальные партнёрства на основе AI-анализа
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(3)].map((_, i) => (
          <RecommendationCard key={i} />
        ))}
      </div>
    </div>
  );
}

function RecommendationCard() {
  const partnership = {
    id: 'rec-' + Math.random().toString(36).substr(2, 9),
    company_name: 'Технологии Будущего',
    partner_name: 'МедТех Инновации',
    status: 'pending',
    compatibility_score: 0.92,
    last_updated: '2026-02-14T10:30:00Z',
    description: 'Высокая совместимость по технологическому стеку и рыночной нише. Рекомендуется начать с пилотного проекта.',
  };

  return (
    <div className="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow duration-200">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-lg">{partnership.company_name}</h3>
            <p className="text-sm text-muted-foreground">↔ {partnership.partner_name}</p>
          </div>
          <Badge variant="default" className="bg-blue-500 text-white">
            Рекомендация
          </Badge>
        </div>
        
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Совместимость</span>
            <span className="text-sm font-bold text-primary">
              {Math.round(partnership.compatibility_score * 100)}%
            </span>
          </div>
          <CompatibilityScore score={partnership.compatibility_score} />
        </div>
        
        <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
          {partnership.description}
        </p>
        
        <div className="flex gap-3">
          <OutreachDialog partnershipId={partnership.id} />
          <button className="flex-1 px-4 py-2 border border-border rounded-md text-sm font-medium hover:bg-muted transition-colors">
            Подробнее
          </button>
        </div>
      </div>
    </div>
  );
}