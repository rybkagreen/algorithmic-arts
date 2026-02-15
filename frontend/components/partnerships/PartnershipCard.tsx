'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TrendingUp, Clock } from 'lucide-react';
import { formatScore } from '@/lib/utils/formatters';

interface Props {
  partnership: {
    id: string;
    company_name: string;
    partner_name: string;
    status: 'active' | 'pending' | 'rejected' | 'completed';
    compatibility_score: number;
    last_updated: string;
    description: string;
  };
}

export function PartnershipCard({ partnership }: Props) {
  const statusColors = {
    active: 'bg-green-500',
    pending: 'bg-yellow-500',
    rejected: 'bg-red-500',
    completed: 'bg-blue-500',
  };

  return (
    <Card className="flex flex-col hover:shadow-lg transition-shadow duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="font-semibold truncate">{partnership.company_name}</h3>
            <p className="text-sm text-muted-foreground truncate">
              ↔ {partnership.partner_name}
            </p>
          </div>
          
          <Badge className={statusColors[partnership.status]}>
            {partnership.status === 'active' && 'Активно'}
            {partnership.status === 'pending' && 'На рассмотрении'}
            {partnership.status === 'rejected' && 'Отклонено'}
            {partnership.status === 'completed' && 'Завершено'}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Совместимость</span>
          <span className="text-sm font-bold text-primary">
            {formatScore(partnership.compatibility_score)}
          </span>
        </div>
        
        <div className="flex items-center text-xs text-muted-foreground">
          <Clock className="mr-1 h-3 w-3" />
          Обновлено: {new Date(partnership.last_updated).toLocaleDateString('ru-RU')}
        </div>
        
        <p className="text-sm text-muted-foreground line-clamp-2">
          {partnership.description}
        </p>
        
        <div className="flex gap-2 pt-2">
          <Button 
            variant="outline" 
            size="sm"
            asChild
            className="flex-1"
          >
            <a href={`/dashboard/partnerships/${partnership.id}`}>
              Подробнее
            </a>
          </Button>
          
          <Button 
            variant="outline" 
            size="sm"
            className="flex-1"
            disabled={partnership.status === 'active'}
          >
            <TrendingUp className="mr-2 h-4 w-4" />
            Статус
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}