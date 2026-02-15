'use client';

import { Progress } from '@/components/ui/progress';

interface Props {
  score: number;
}

export function CompatibilityScore({ score }: Props) {
  const color = score >= 0.8 ? 'bg-green-500' : score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500';
  
  return (
    <div className="space-y-2">
      <Progress value={score * 100} className="h-2" />
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>Низкая</span>
        <span className={`font-medium ${color} px-2 py-1 rounded`}>
          {Math.round(score * 100)}%
        </span>
        <span>Высокая</span>
      </div>
    </div>
  );
}