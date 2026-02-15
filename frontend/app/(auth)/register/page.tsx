'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <Button type="submit" disabled={pending} className="w-full">
      {pending ? 'Регистрация...' : 'Зарегистрироваться'}
    </Button>
  );
}

export default function RegisterPage() {
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(formData: FormData) {
    try {
      // In a real implementation, this would call an API endpoint
      // For now, we'll simulate registration
      console.log('Registration data:', Object.fromEntries(formData.entries()));
      // Redirect would happen after successful registration
    } catch (err: any) {
      setError(err.message || 'Ошибка регистрации');
    }
  }

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader className="pb-4">
        <CardTitle className="text-2xl font-bold">Регистрация</CardTitle>
      </CardHeader>
      <CardContent>
        <form action={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="firstName">Имя</Label>
              <Input 
                id="firstName" 
                name="firstName" 
                placeholder="Иван"
                required 
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="lastName">Фамилия</Label>
              <Input 
                id="lastName" 
                name="lastName" 
                placeholder="Иванов"
                required 
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input 
              id="email" 
              name="email" 
              type="email" 
              placeholder="example@company.ru"
              required 
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password">Пароль</Label>
            <Input 
              id="password" 
              name="password" 
              type="password" 
              placeholder="••••••••" 
              required 
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="companyName">Название компании</Label>
            <Input
              id="companyName"
              name="companyName"
              placeholder="ООО Технологии Будущего"
              required
            />
          </div>
          
          <SubmitButton />
          
          <div className="text-center text-sm text-muted-foreground">
            Уже есть аккаунт?{' '}
            <a href="/login" className="text-primary hover:underline">
              Войти
            </a>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}