'use client';

import React from 'react';
import { createContext, useContext } from 'react';
import { useRealtimeUpdates } from '@/lib/hooks/useRealtimeUpdates';

const RealtimeContext = createContext<{
  status: 'connecting' | 'connected' | 'disconnected';
}>({ status: 'disconnected' });

export function RealtimeProvider({ children }: { children: React.ReactNode }) {
  const { status } = useRealtimeUpdates(true);
  
  return (
    <RealtimeContext.Provider value={{ status }}>
      {children}
    </RealtimeContext.Provider>
  );
}

export function useRealtime() {
  return useContext(RealtimeContext);
}