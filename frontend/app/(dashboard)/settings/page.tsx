'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ProfileForm } from '@/components/settings/ProfileForm';
import { CrmConnections } from '@/components/settings/CrmConnections';

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Настройки</h1>
        <p className="text-muted-foreground">
          Управление профилем и интеграциями CRM
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Настройки</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="profile" className="w-full">
            <TabsList>
              <TabsTrigger value="profile">Профиль</TabsTrigger>
              <TabsTrigger value="crm">CRM-интеграции</TabsTrigger>
            </TabsList>
            
            <TabsContent value="profile">
              <ProfileForm />
            </TabsContent>
            
            <TabsContent value="crm">
              <CrmConnections />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}