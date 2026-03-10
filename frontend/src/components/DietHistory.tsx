import React, { useEffect, useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Skeleton } from './ui/skeleton';
import { Clock, User, FileText, ArrowRight } from 'lucide-react';
import { apiGetPatientPrescriptions } from '../lib/api';
import { Prescricao } from '../types';

interface DietHistoryProps {
  patientId: string;
}

const priorityColor: Record<string, string> = {
  urgente: 'bg-red-100 text-red-800',
  alta:    'bg-orange-100 text-orange-800',
  media:   'bg-yellow-100 text-yellow-800',
  baixa:   'bg-green-100 text-green-800',
};

export const DietHistory: React.FC<DietHistoryProps> = ({ patientId }) => {
  const [prescricoes, setPrescricoes] = useState<Prescricao[]>([]);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState('');

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    apiGetPatientPrescriptions(patientId)
      .then((data) => { if (!cancelled) setPrescricoes(data); })
      .catch(() => { if (!cancelled) setError('Erro ao carregar histórico.'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [patientId]);

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2].map((i) => (
          <Card key={i}><CardContent className="p-5"><Skeleton className="h-24 w-full" /></CardContent></Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-sm text-muted-foreground">{error}</CardContent>
      </Card>
    );
  }

  // Flatten all history items across all prescriptions
  const allHistorico = prescricoes.flatMap((p) =>
    (p.historico ?? []).map((h) => ({ ...h, prescricaoId: p.id }))
  ).sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime());

  if (allHistorico.length === 0) {
    return (
      <Card>
        <CardContent className="py-14 text-center">
          <FileText className="w-10 h-10 text-muted-foreground/40 mx-auto mb-3" />
          <h3 className="font-semibold text-gray-800 mb-1">Nenhuma alteração registrada</h3>
          <p className="text-sm text-muted-foreground">
            O histórico de alterações de dieta aparecerá aqui.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {allHistorico.map((h, idx) => (
        <Card key={idx} className="border-l-4 border-l-blue-400">
          <CardContent className="p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-mono text-muted-foreground bg-gray-100 px-2 py-0.5 rounded">
                  #{allHistorico.length - idx}
                </span>
                <Badge variant="outline" className="text-xs">Notificado</Badge>
              </div>
              <div className="flex items-center text-xs text-muted-foreground">
                <Clock className="w-3 h-3 mr-1" />
                {new Date(h.data).toLocaleString('pt-BR')}
              </div>
            </div>

            <div className="flex items-center gap-3 mb-3">
              <div className="flex-1 bg-gray-50 rounded p-2.5">
                <p className="text-xs text-muted-foreground mb-0.5">Dieta anterior</p>
                <p className="text-sm font-medium text-gray-700">{h.dieta_anterior}</p>
              </div>
              <ArrowRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />
              <div className="flex-1 bg-blue-50 rounded p-2.5">
                <p className="text-xs text-muted-foreground mb-0.5">Nova dieta</p>
                <p className="text-sm font-medium text-blue-700">{h.dieta_nova}</p>
              </div>
            </div>

            {h.motivo && (
              <div className="bg-gray-50 rounded p-2.5 mb-3 text-sm text-gray-700">
                <span className="text-xs text-muted-foreground block mb-0.5">Motivo</span>
                {h.motivo}
              </div>
            )}

            <div className="flex items-center text-xs text-muted-foreground">
              <User className="w-3 h-3 mr-1" />
              Alterado por: <span className="ml-1 font-medium">{h.alterado_por}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
