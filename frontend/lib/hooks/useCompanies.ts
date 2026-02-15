/*
  Используем сгенерированные orval-функции, обёрнутые в TanStack Query.
  Orval генерирует useGetCompanies(), useCreateCompany() и т.д.
  Здесь — только дополнительная логика поверх них.
*/

import { keepPreviousData } from '@tanstack/react-query';
import { useGetCompanies, useGetCompanyById } from '@/lib/api/generated/companies';
import { useFilterStore } from '@/lib/stores/filterStore';

export function useCompanies() {
  const filters = useFilterStore(s => s.companyFilters);
  return useGetCompanies(filters, {
    query: {
      placeholderData: keepPreviousData,
      staleTime:       30_000,
    },
  });
}

export function useCompany(id: string) {
  return useGetCompanyById(id, {
    query: {
      enabled:   !!id,
      staleTime: 60_000,
    },
  });
}