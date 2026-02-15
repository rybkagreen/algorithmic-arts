'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useFormStatus } from 'react-dom';
import { createCompanyAction } from '@/app/actions/companies';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <Button type="submit" disabled={pending} className="w-full">
      {pending ? 'Создание...' : 'Создать компанию'}
    </Button>
  );
}

export default function CreateCompanyPage() {
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(formData: FormData) {
    try {
      const result = await createCompanyAction({}, formData);
      if (result.message) {
        setError(result.message);
      }
      // In a real implementation, we would redirect on success
      console.log('Company created:', result.company);
    } catch (err: any) {
      setError(err.message || 'Ошибка создания компании');
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <CardTitle>Добавить новую компанию</CardTitle>
        </CardHeader>
        <CardContent>
          <form action={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                {error}
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label htmlFor="name">Название компании</label>
                <Input
                  id="name"
                  name="name"
                  placeholder="ООО Технологии Будущего"
                  required
                />
              </div>
              
              <div className="space-y-2">
                <label htmlFor="industry">Отрасль</label>
                <Select name="industry" required>
                  <SelectTrigger>
                    <SelectValue placeholder="Выберите отрасль" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="it">IT и программное обеспечение</SelectItem>
                    <SelectItem value="finance">Финансы и банки</SelectItem>
                    <SelectItem value="healthcare">Здравоохранение</SelectItem>
                    <SelectItem value="education">Образование</SelectItem>
                    <SelectItem value="manufacturing">Производство</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="space-y-2">
              <label htmlFor="description">Описание</label>
              <Textarea 
                id="description" 
                name="description" 
                placeholder="Краткое описание компании и её деятельности"
                rows={3}
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label htmlFor="website">Веб-сайт</label>
                <Input 
                  id="website" 
                  name="website" 
                  type="url" 
                  placeholder="https://example.com"
                />
              </div>
              
              <div className="space-y-2">
                <label htmlFor="headquarters_city">Город headquarters</label>
                <Input 
                  id="headquarters_city" 
                  name="headquarters_city" 
                  placeholder="Москва"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label htmlFor="employees_range">Размер компании</label>
                <Select name="employees_range" required>
                  <SelectTrigger>
                    <SelectValue placeholder="Выберите размер" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1-10">1-10 сотрудников</SelectItem>
                    <SelectItem value="11-50">11-50 сотрудников</SelectItem>
                    <SelectItem value="51-200">51-200 сотрудников</SelectItem>
                    <SelectItem value="201-500">201-500 сотрудников</SelectItem>
                    <SelectItem value="500+">500+ сотрудников</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <label htmlFor="funding_stage">Стадия финансирования</label>
                <Select name="funding_stage" required>
                  <SelectTrigger>
                    <SelectValue placeholder="Выберите стадию" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pre_seed">Pre-seed</SelectItem>
                    <SelectItem value="seed">Seed</SelectItem>
                    <SelectItem value="series_a">Series A</SelectItem>
                    <SelectItem value="series_b">Series B</SelectItem>
                    <SelectItem value="bootstrapped">Bootstrapped</SelectItem>
                    <SelectItem value="ipo">IPO</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <SubmitButton />
          </form>
        </CardContent>
      </Card>
    </div>
  );
}