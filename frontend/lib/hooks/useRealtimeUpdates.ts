'use client';

import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8080/ws';

type WSStatus = 'connecting' | 'connected' | 'disconnected';

export function useRealtimeUpdates(enabled = true) {
  const qc     = useQueryClient();
  const wsRef  = useRef<WebSocket | null>(null);
  const retryRef = useRef<ReturnType<typeof setTimeout>>(null);
  const [status, setStatus] = useState<WSStatus>('disconnected');

  useEffect(() => {
    if (!enabled) return;

    function connect() {
      setStatus('connecting');
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen  = () => setStatus('connected');
      ws.onerror = () => ws.close();

      ws.onmessage = ({ data }) => {
        try {
          const msg = JSON.parse(data as string) as { type: string };
          switch (msg.type) {
            case 'company.created':
            case 'company.updated':
              void qc.invalidateQueries({ queryKey: ['companies'] });
              break;
            case 'partnership.matched':
              void qc.invalidateQueries({ queryKey: ['partnerships'] });
              toast.success('Найдено новое партнёрство!', {
                description: 'Проверь раздел Рекомендации',
                action: { label: 'Открыть', onClick: () => window.location.href = '/partnerships/recommendations' },
              });
              break;
            case 'ai.analysis.completed':
              void qc.invalidateQueries({ queryKey: ['partnerships', 'recommendations'] });
              break;
          }
        } catch { /* игнорируем некорректные сообщения */ }
      };

      ws.onclose = () => {
        setStatus('disconnected');
        retryRef.current = setTimeout(connect, 5_000);
      };
    }

    connect();
    return () => {
      clearTimeout(retryRef.current!);
      wsRef.current?.close();
    };
  }, [enabled, qc]);

  return { status };
}