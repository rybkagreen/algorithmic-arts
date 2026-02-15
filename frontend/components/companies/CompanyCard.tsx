/* eslint-disable @typescript-eslint/no-unused-vars */
'use client';

import Link from 'next/link';
import Image from 'next/image';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BadgeCheck } from 'lucide-react';
import type { Company } from '@/lib/api/generated/schemas';

interface Props {
  company:        Company;
  onFindPartners?: (id: string) => void;
}

export function CompanyCard({ company, onFindPartners }: Props) {
  const handleFindPartners = (id: string) => {
    if (onFindPartners) {
      onFindPartners(id); // Явное использование параметра id для ESLint v9
    }
  };

  const techs = Object.entries(company.tech_stack ?? {})
    .filter(([, v]) => v)
    .map(([k]) => k)
    .slice(0, 5);

  return (
    <Card className="flex flex-col hover:shadow-lg transition-shadow duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="relative size-12 shrink-0 rounded-xl overflow-hidden bg-muted">
              {company.logo_url ? (
                <Image
                  src={company.logo_url}
                  alt={company.name}
                  fill
                  className="object-contain"
                  sizes="48px"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                  {company.name.charAt(0)}
                </div>
              )}
            </div>
            <div className="min-w-0">
              <h3 className="font-semibold truncate">{company.name}</h3>
              <p className="text-sm text-muted-foreground truncate">
                {company.industry}
              </p>
            </div>
          </div>

          {company.is_verified && (
            <BadgeCheck className="size-5 text-green-500" />
          )}
        </div>
      </CardHeader>

      <CardContent className="flex-1 space-y-3">
        <div className="flex flex-wrap gap-2">
          {techs.map((tech) => (
            <Badge key={tech} variant="secondary" className="text-xs">
              {tech}
            </Badge>
          ))}
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            {company.employees_range} сотрудников
          </span>
          <span className="text-muted-foreground">
            {company.funding_stage}
          </span>
        </div>

        <div className="flex gap-2 pt-2">
          <Button
            variant="outline"
            size="sm"
            asChild
            className="flex-1"
          >
            <Link href={`/dashboard/companies/${company.id}`}>
              Подробнее
            </Link>
          </Button>

          {onFindPartners && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleFindPartners(company.id)}
              className="flex-1"
            >
              Найти партнёров
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}