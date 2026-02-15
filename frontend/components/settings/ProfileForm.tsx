'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <Button type="submit" disabled={pending} className="w-full">
      {pending ? 'Сохранение...' : 'Сохранить изменения'}
    </Button>
  );
}

export function ProfileForm() {
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(formData: FormData) {
    try {
      // In a real implementation, this would call an API endpoint
      console.log('Profile data:', Object.fromEntries(formData.entries()));
      // Redirect would happen after successful update
    } catch (err: any) {
      setError(err.message || 'Ошибка сохранения профиля');
    }
  }

  return (
    <Card className="border-0 shadow-none">
      <CardHeader>
        <CardTitle>Профиль пользователя</CardTitle>
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
              <label htmlFor="firstName">Имя</label>
              <Input 
                id="firstName" 
                name="firstName" 
                placeholder="Иван"
                defaultValue="Иван"
                required 
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="lastName">Фамилия</label>
              <Input 
                id="lastName" 
                name="lastName" 
                placeholder="Иванов"
                defaultValue="Иванов"
                required 
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <label htmlFor="email">Email</label>
            <Input 
              id="email" 
              name="email" 
              type="email" 
              placeholder="example@company.ru"
              defaultValue="ivan@example.com"
              required 
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="companyName">Название компании</label>
            <Input
              id="companyName"
              name="companyName"
              placeholder="ООО Технологии Будущего"
              defaultValue="ООО Технологии Будущего"
              required
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="position">Должность</label>
            <Input 
              id="position" 
              name="position" 
              placeholder="CTO"
              defaultValue="CTO"
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="bio">Описание</label>
            <Textarea 
              id="bio" 
              name="bio" 
              placeholder="Краткое описание вашей роли и опыта"
              defaultValue="Руководитель отдела разработки в компании Технологии Будущего"
              rows={3}
            />
          </div>
          
          <SubmitButton />
        </form>
      </CardContent>
    </Card>
  );
}