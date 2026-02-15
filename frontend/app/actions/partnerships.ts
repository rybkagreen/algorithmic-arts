'use server';

import { revalidatePath } from 'next/cache';
import { auth } from '@/lib/auth';
import { serverFetch } from '@/lib/api/server';

export async function updatePartnershipStatusAction(
  partnershipId: string,
  status: string,
): Promise<{ success: boolean }> {
  const session = await auth();
  if (!session) throw new Error('Unauthorized');

  await serverFetch(`/partnerships/${partnershipId}`, {
    method: 'PATCH',
    body:   JSON.stringify({ status }),
  });

  revalidatePath('/partnerships');
  revalidatePath(`/partnerships/${partnershipId}`);
  return { success: true };
}