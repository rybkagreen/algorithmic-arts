'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';

const ResponsivePieChart = dynamic(() => import('recharts').then(mod => mod.PieChart), {
  ssr: false,
});

const Pie = dynamic(() => import('recharts').then(mod => mod.Pie), {
  ssr: false,
});

const Cell = dynamic(() => import('recharts').then(mod => mod.Cell), {
  ssr: false,
});

const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), {
  ssr: false,
});

const Legend = dynamic(() => import('recharts').then(mod => mod.Legend), {
  ssr: false,
});

export function IndustryPieChart() {
  const [data, setData] = useState<any[]>([]);
  
  useEffect(() => {
    // Simulated industry distribution data
    const industries = [
      { name: 'IT и программное обеспечение', value: 42 },
      { name: 'Финансы и банки', value: 28 },
      { name: 'Здравоохранение', value: 15 },
      { name: 'Образование', value: 10 },
      { name: 'Производство', value: 5 },
    ];
    
    setData(industries);
  }, []);

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="h-80">
      <ResponsivePieChart
        width={400}
        height={400}
        data={data}
        margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
      >
        <Pie
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={80}
          fill="#8884d8"
          data={data}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </ResponsivePieChart>
    </div>
  );
}