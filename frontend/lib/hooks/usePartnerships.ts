import {
  useGetPartnerships,
  useGetRecommendations,
  useUpdatePartnership,
} from '@/lib/api/generated/partnerships';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

export function usePartnerships(params = {}) {
  return useGetPartnerships(params, {
    query: { staleTime: 30_000 },
  });
}

export function useRecommendations() {
  return useGetRecommendations({ limit: 20 }, {
    query: {
      staleTime: 120_000,    // 2 мин — AI дорогой
      gcTime:    300_000,
    },
  });
}

export function useUpdatePartnershipStatus() {
  const qc = useQueryClient();
  return useUpdatePartnership({
    mutation: {
      onSuccess: () => {
        void qc.invalidateQueries({ queryKey: ['partnerships'] });
        toast.success('Статус партнёрства обновлён');
      },
      onError: () => toast.error('Не удалось обновить статус'),
    },
  });
}