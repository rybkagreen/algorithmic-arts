'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';

interface Props {
  partnershipId: string;
}

export function OutreachDialog({ partnershipId }: Props) {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);

  function handleSend() {
    setIsSending(true);
    // In a real implementation, this would call an API endpoint
    console.log('Sending outreach message:', { partnershipId, message });
    setTimeout(() => {
      setIsSending(false);
      alert('Сообщение отправлено!');
    }, 1000);
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="flex-1">
          Отправить предложение
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Отправить предложение о партнёрстве</DialogTitle>
          <DialogDescription>
            Напишите краткое сообщение для потенциального партнёра
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <Card>
            <CardContent className="p-4">
              <h3 className="font-medium mb-2">Потенциальный партнёр</h3>
              <p className="text-sm text-muted-foreground">МедТех Инновации</p>
            </CardContent>
          </Card>
          
          <Textarea
            placeholder="Приветствуем вас! Мы заметили вашу компанию и считаем, что у нас есть отличные возможности для сотрудничества в области..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={5}
          />
          
          <div className="flex justify-end space-x-3">
            <Button variant="outline" onClick={() => setMessage('')}>
              Сбросить
            </Button>
            <Button 
              onClick={handleSend}
              disabled={isSending || !message.trim()}
            >
              {isSending ? 'Отправка...' : 'Отправить'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}