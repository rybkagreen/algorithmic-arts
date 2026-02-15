'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';


const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis), {
  ssr: false,
});

const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis), {
  ssr: false,
});

const CartesianGrid = dynamic(() => import('recharts').then(mod => mod.CartesianGrid), {
  ssr: false,
});

const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), {
  ssr: false,
});

const Legend = dynamic(() => import('recharts').then(mod => mod.Legend), {
  ssr: false,
});

const AreaChart = dynamic(() => import('recharts').then(mod => mod.AreaChart), {
  ssr: false,
});

const Area = dynamic(() => import('recharts').then(mod => mod.Area), {
  ssr: false,
});

export function PartnershipChart() {
  const [data, setData] = useState<any[]>([]);
  
  useEffect(() => {
    // Simulated data for the chart
    const months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];
    const activeData = Array.from({ length: 12 }, (_, i) => ({
      month: months[i],
      active: Math.floor(10 + Math.random() * 30),
      potential: Math.floor(20 + Math.random() * 50),
    }));
    
    setData(activeData);
  }, []);

  return (
    <div className="h-80">
      <AreaChart
        width={500}
        height={300}
        data={data}
        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Area type="monotone" dataKey="active" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} name="Активные партнёрства" />
        <Area type="monotone" dataKey="potential" stroke="#10b981" fill="#10b981" fillOpacity={0.3} name="Потенциальные партнёры" />
      </AreaChart>
    </div>
  );
}