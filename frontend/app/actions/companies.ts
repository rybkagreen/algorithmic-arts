'use server';

import { z } from 'zod';
import { revalidatePath } from 'next/cache';
import { auth } from '@/lib/auth';
import { serverFetch } from '@/lib/api/server';
import type { Company } from '@/lib/api/generated/schemas';

const createCompanySchema = z.object({
  name:              z.string().min(2).max(100),
  description:       z.string().max(1000).optional(),
  industry:          z.string(),
  website:           z.string().url().optional().or(z.literal('')),
  headquarters_city: z.string().optional(),
  employees_range:   z.enum(['1-10','11-50','51-200','201-500','500+']),
  funding_stage:     z.enum(['pre_seed','seed','series_a','series_b','bootstrapped','ipo']),
});

export type CreateCompanyState = {
  errors?: Record<string, string[]>;
  message?: string;
  company?: Company;
};

export async function createCompanyAction(
  _prevState: CreateCompanyState,
  formData: FormData,
): Promise<CreateCompanyState> {
  const session = await auth();
  if (!session) return { message: 'Unauthorized' };

  const raw = Object.fromEntries(formData.entries());
  const parsed = createCompanySchema.safeParse(raw);

  if (!parsed.success) {
    return { errors: parsed.error.flatten().fieldErrors };
  }

  const company = await serverFetch<Company>('/companies', {
    method: 'POST',
    body:   JSON.stringify(parsed.data),
  });

  revalidatePath('/companies');
  return { company };
}