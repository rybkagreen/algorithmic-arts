import { StatsCard } from '@/components/analytics/StatsCard';
import { PartnershipChart } from '@/components/analytics/PartnershipChart';
import { IndustryPieChart } from '@/components/analytics/IndustryPieChart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Аналитика</h1>
        <p className="text-muted-foreground">
          Статистика по партнёрствам и рыночным трендам
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard title="Активные партнёрства" value="24" change="+12%" icon="📈" />
        <StatsCard title="Потенциальные партнёры" value="156" change="+8%" icon="🔍" />
        <StatsCard title="Средняя совместимость" value="78%" change="+5%" icon="🎯" />
        <StatsCard title="Новые компании" value="42" change="+23%" icon="🏢" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Динамика партнёрств</CardTitle>
        </CardHeader>
        <CardContent>
          <PartnershipChart />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Распределение по отраслям</CardTitle>
        </CardHeader>
        <CardContent>
          <IndustryPieChart />
        </CardContent>
      </Card>
    </div>
  );
}