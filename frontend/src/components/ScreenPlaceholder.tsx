import React from 'react';
import { Card, CardContent } from './ui/card';
import { Construction } from 'lucide-react';

interface PlaceholderProps {
  title: string;
  description?: string;
}

export const ScreenPlaceholder: React.FC<PlaceholderProps> = ({ title, description }) => (
  <div className="flex items-center justify-center min-h-[60vh] animate-fade-in">
    <Card className="max-w-md w-full border-dashed border-2">
      <CardContent className="py-16 text-center">
        <Construction className="w-12 h-12 text-amber-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-800 mb-2">{title}</h2>
        <p className="text-sm text-muted-foreground">
          {description ?? 'Esta tela será implementada no próximo prompt.'}
        </p>
      </CardContent>
    </Card>
  </div>
);
