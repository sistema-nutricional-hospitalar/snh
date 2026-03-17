import React, { useState } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { useApp } from '../contexts/AppContext';
import { Notificacao } from '../types';
import {
  Bell, CheckCircle, AlertTriangle, Clock, MapPin, X, RefreshCw,
} from 'lucide-react';

const TYPE_EMOJI: Record<string, string> = {
  alteracao_dieta: '🍽️',
  novo_paciente:   '👤',
  urgente:         '🚨',
  sistema:         '⚙️',
};

const PRIORITY_BG: Record<string, string> = {
  urgente: 'bg-red-50 border-red-200',
  alta:    'bg-orange-50 border-orange-200',
  media:   'bg-yellow-50 border-yellow-200',
  baixa:   'bg-green-50 border-green-200',
};

const PRIORITY_ICON: Record<string, React.ReactNode> = {
  urgente: <AlertTriangle className="w-4 h-4 text-red-500" />,
  alta:    <AlertTriangle className="w-4 h-4 text-orange-500" />,
  media:   <Bell className="w-4 h-4 text-yellow-500" />,
  baixa:   <Bell className="w-4 h-4 text-green-500" />,
};

export const NotificationCenter: React.FC = () => {
  const { notifications, markRead, markAllRead, unreadCount } = useApp();
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [marking, setMarking] = useState(false);
  const [setorFilter, setSetorFilter] = useState<string | null>(null);

  const setoresUnicos = Array.from(
    new Set((notifications || []).map(n => n.setor_nome).filter(Boolean))
  ).sort() as string[];

  const filtered = notifications.filter((n) => {
    const matchFilter = filter === 'all' || !n.lida;
    const matchSetor = !setorFilter || n.setor_nome === setorFilter;
    return matchFilter && matchSetor;
  });

  const handleMarkAll = async () => {
    setMarking(true);
    try { await markAllRead(); } finally { setMarking(false); }
  };

  const stats = [
    { label: 'Urgentes',          value: notifications.filter(n => n.prioridade === 'urgente').length,       color: 'text-red-600' },
    { label: 'Alta prioridade',   value: notifications.filter(n => n.prioridade === 'alta').length,          color: 'text-orange-600' },
    { label: 'Alterações dieta',  value: notifications.filter(n => n.tipo === 'alteracao_dieta').length,     color: 'text-blue-600' },
    { label: 'Novos pacientes',   value: notifications.filter(n => n.tipo === 'novo_paciente').length,       color: 'text-green-600' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1>Central de Notificações</h1>
          <p className="text-sm text-muted-foreground">Acompanhe todas as notificações em tempo real</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-base px-3 py-1">
            {unreadCount} não lidas
          </Badge>
          {unreadCount > 0 && (
            <Button size="sm" onClick={handleMarkAll} disabled={marking}>
              {marking
                ? <><RefreshCw className="w-4 h-4 mr-2 animate-spin" />Marcando...</>
                : <><CheckCircle className="w-4 h-4 mr-2" />Marcar todas como lidas</>}
            </Button>
          )}
        </div>
      </div>

      {/* Filtro por setor */}
      {setoresUnicos.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-medium text-muted-foreground">Filtrar por setor:</span>
          <Button
            size="sm"
            variant={setorFilter === null ? 'default' : 'outline'}
            onClick={() => setSetorFilter(null)}
          >
            Todos os setores
          </Button>
          {setoresUnicos.map(setor => (
            <Button
              key={setor}
              size="sm"
              variant={setorFilter === setor ? 'default' : 'outline'}
              onClick={() => setSetorFilter(setor)}
            >
              {setor}
            </Button>
          ))}
        </div>
      )}

      {/* Tabs */}
      <Tabs value={filter} onValueChange={(v) => setFilter(v as 'all' | 'unread')}>
        <TabsList>
          <TabsTrigger value="all">Todas ({notifications.length})</TabsTrigger>
          <TabsTrigger value="unread">Não lidas ({unreadCount})</TabsTrigger>
        </TabsList>

        <TabsContent value={filter} className="mt-5">
          {filtered.length === 0 ? (
            <Card>
              <CardContent className="py-16 text-center">
                <Bell className="w-12 h-12 text-muted-foreground/30 mx-auto mb-4" />
                <h3 className="font-semibold text-gray-900 mb-1">
                  {filter === 'unread' ? 'Nenhuma notificação não lida' : 'Nenhuma notificação'}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {filter === 'unread'
                    ? 'Todas as notificações foram lidas.'
                    : 'As notificações aparecerão aqui conforme chegarem.'}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {filtered.map((n) => (
                <NotifCard key={n.id} notif={n} onMarkRead={() => markRead(n.id)} />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {stats.map((s) => (
          <Card key={s.label}>
            <CardContent className="p-4 text-center">
              <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
              <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// ── Notification card ───────────────────────────────────────────────────────
const NotifCard: React.FC<{ notif: Notificacao; onMarkRead: () => void }> = ({ notif, onMarkRead }) => {
  const [marking, setMarking] = useState(false);

  const handleMark = async () => {
    if (notif.lida) return;
    setMarking(true);
    try { await onMarkRead(); } finally { setMarking(false); }
  };

  return (
    <Card className={`transition-all ${!notif.lida ? `${PRIORITY_BG[notif.prioridade] ?? ''} shadow-sm` : 'bg-white opacity-80'}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="text-2xl flex-shrink-0 mt-0.5">
            {TYPE_EMOJI[notif.tipo] ?? '📢'}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <div className="flex items-center gap-2 flex-wrap">
                {PRIORITY_ICON[notif.prioridade]}
                <span className={`font-semibold text-sm ${!notif.lida ? 'text-gray-900' : 'text-gray-500'}`}>
                  {notif.titulo}
                </span>
                {!notif.lida && <span className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0" />}
              </div>
              <div className="flex items-center gap-1.5 flex-shrink-0">
                <Badge variant="outline" className="text-xs">
                  {notif.prioridade.toUpperCase()}
                </Badge>
                {!notif.lida && (
                  <Button
                    variant="ghost" size="sm"
                    className="h-6 w-6 p-0"
                    disabled={marking}
                    onClick={handleMark}
                  >
                    {marking ? <RefreshCw className="w-3 h-3 animate-spin" /> : <X className="w-3 h-3" />}
                  </Button>
                )}
              </div>
            </div>

            {(notif.paciente_nome || notif.setor_nome) && (
              <div className="flex items-center gap-2 mb-2 flex-wrap">
                {notif.paciente_nome && (
                  <Badge variant="secondary" className="text-xs font-normal">
                    <span className="mr-1">👤</span> {notif.paciente_nome}
                  </Badge>
                )}
                {notif.setor_nome && (
                  <Badge variant="outline" className="text-xs font-normal bg-blue-50 border-blue-200">
                    <span className="mr-1">🏥</span> {notif.setor_nome}
                  </Badge>
                )}
              </div>
            )}

            <p className={`text-sm mb-2.5 ${!notif.lida ? 'text-gray-800' : 'text-gray-500'}`}>
              {notif.mensagem}
            </p>

            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(notif.criada_em).toLocaleString('pt-BR')}
                </div>
              </div>
              {notif.lida && (
                <div className="flex items-center gap-1 text-green-600">
                  <CheckCircle className="w-3 h-3" />Lida
                </div>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
