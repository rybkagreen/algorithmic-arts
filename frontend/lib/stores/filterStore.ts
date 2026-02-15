/* eslint-disable @typescript-eslint/no-unused-vars */
import { create } from 'zustand';

interface CompanyFilters {
  search?:          string;
  industry?:        string;
  employees_range?: string;
  funding_stage?:   string;
  tech_stack?:      string[];
  page:             number;
  size:             number;
}

interface FilterState {
  companyFilters:       CompanyFilters;
  setCompanyFilter:    <K extends keyof CompanyFilters>(key: K, value: CompanyFilters[K]) => void;
  resetCompanyFilters: () => void;
}

const defaults: CompanyFilters = { page: 1, size: 12 };

export const useFilterStore = create<FilterState>((set) => ({
  companyFilters: defaults,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setCompanyFilter: (key, value) =>
    set(s => ({ companyFilters: { ...s.companyFilters, [key]: value, page: 1 } })),
  resetCompanyFilters: () => set({ companyFilters: defaults }),
}));