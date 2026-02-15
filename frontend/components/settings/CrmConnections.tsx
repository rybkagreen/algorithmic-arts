'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, Plus, Settings } from 'lucide-react';

export function CrmConnections() {
  const [connections, setConnections] = useState([
    { id: '1', name: 'amoCRM', connected: true, lastSync: '2026-02-14T10:30:00Z' },
    { id: '2', name: 'Bitrix24', connected: true, lastSync: '2026-02-14T09:15:00Z' },
    { id: '3', name: 'Salesforce', connected: false, lastSync: null },
    { id: '4', name: 'HubSpot', connected: false, lastSync: null },
  ]);

  const handleConnect = (id: string) => {
    setConnections(connections.map(conn => 
      conn.id === id ? { ...conn, connected: true, lastSync: new Date().toISOString() } : conn
    ));
  };

  return (
    <Card className="border-0 shadow-none">
      <CardHeader>
        <CardTitle>CRM-интеграции</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {connections.map((connection) => (
            <div key={connection.id} className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-4">
                <div className="size-10 rounded-lg bg-muted flex items-center justify-center">
                  <span className="text-sm font-medium">{connection.name.charAt(0)}</span>
                </div>
                <div>
                  <h3 className="font-medium">{connection.name}</h3>
                  {connection.lastSync && (
                    <p className="text-sm text-muted-foreground">
                      Последняя синхронизация: {new Date(connection.lastSync).toLocaleDateString('ru-RU')}
                    </p>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                {connection.connected ? (
                  <Badge variant="default" className="bg-green-500 text-white">
                    <CheckCircle className="mr-1 h-4 w-4" />
                    Подключено
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-muted-foreground">
                    <XCircle className="mr-1 h-4 w-4" />
                    Не подключено
                  </Badge>
                )}
                
                <Button variant="ghost" size="icon">
                  <Settings className="h-4 w-4" />
                </Button>
                
                {!connection.connected && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleConnect(connection.id)}
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    Подключить
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-6 pt-6 border-t">
          <h3 className="font-medium mb-3">Добавить новую CRM</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {['Pipedrive', 'Megaplan', 'Zapier'].map((crm) => (
              <Button key={crm} variant="outline" className="justify-start">
                <Plus className="mr-2 h-4 w-4" />
                {crm}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}