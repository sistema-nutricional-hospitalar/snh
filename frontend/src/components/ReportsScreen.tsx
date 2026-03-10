import React, { useState, useEffect, useCallback } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { useApp } from '../contexts/AppContext';
import { apiGetDietReport, apiGetAlteracoesReport } from '../lib/api';
import {
  FileText, Download, BarChart3, TrendingUp, PieChart,
  Clock, RefreshCw, AlertCircle,
} from 'lucide-react';

const PERIOD_OPTIONS = [
  { value: 'today', label: 'Hoje' },
  { value: 'week',  label: 'Esta Semana' },
  { value: 'month', label: 'Este Mês' },
  { value: 'custom', label: 'Período Personalizado' },
];

function exportJSON(data: any, title: string) {
  const content = `HOSPITAL SNH — ${title}\nGerado em: ${new Date().toLocaleString('pt-BR')}\n\n${JSON.stringify(data, null, 2)}`;
  const blob = new Blob([content], { type: 'text/plain' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url;
  a.download = `${title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.txt`;
  document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);
}

export const ReportsScreen: React.FC = () => {
  const { patients } = useApp();

  const [period,     setPeriod]     = useState('month');
  const [sector,     setSector]     = useState('all');
  const [startDate,  setStartDate]  = useState('');
  const [endDate,    setEndDate]    = useState('');

  const [dietData,   setDietData]   = useState<any>(null);
  const [altData,    setAltData]    = useState<any>(null);
  const [loading,    setLoading]    = useState(false);
  const [error,      setError]      = useState('');

  // Local stats from patients
  const localStats = {
    total:     patients.length,
    alergias: patients.reduce((s, p) => s + (p.alergias?.length ?? 0), 0),
    restricoes: patients.reduce((s, p) => s + (p.restricoes_alimentares?.length ?? 0), 0),
    setores: [...new Set(patients.map(p => p.setor_nome).filter(Boolean))].length,
  };

  const fetchReports = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params: any = {};
      if (sector !== 'all') params.setor_id = sector;
      if (period === 'custom' && startDate) params.data_inicio = startDate;
      if (period === 'custom' && endDate)   params.data_fim    = endDate;

      const [diet, alt] = await Promise.allSettled([
        apiGetDietReport(params),
        apiGetAlteracoesReport(),
      ]);

      if (diet.status === 'fulfilled') setDietData(diet.value);
      if (alt.status  === 'fulfilled') setAltData(alt.value);

      if (diet.status === 'rejected' && alt.status === 'rejected') {
        setError('Endpoints de relatório retornaram erro. Os dados locais abaixo são derivados dos pacientes carregados.');
      }
    } catch {
      setError('Erro ao carregar relatórios.');
    } finally {
      setLoading(false);
    }
  }, [period, sector, startDate, endDate]);

  useEffect(() => { fetchReports(); }, [fetchReports]);

  const periodLabel = PERIOD_OPTIONS.find(p => p.value === period)?.label ?? '';

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1>Relatórios e Análises</h1>
          <p className="text-sm text-muted-foreground">Geração e exportação de relatórios do sistema</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchReports} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {error && (
        <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardHeader><CardTitle className="text-base">Filtros</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <Label>Período</Label>
              <Select value={period} onValueChange={setPeriod}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {PERIOD_OPTIONS.map(o => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>

            {period === 'custom' && (
              <>
                <div className="space-y-1.5">
                  <Label>Data Inicial</Label>
                  <Input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label>Data Final</Label>
                  <Input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
                </div>
              </>
            )}

            <div className="space-y-1.5">
              <Label>Setor</Label>
              <Select value={sector} onValueChange={setSector}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os Setores</SelectItem>
                  {[...new Set(patients.map(p => p.setor_nome).filter(Boolean))].sort().map(s => (
                    // Correção: Garante que 'value' nunca seja undefined usando ?? ""
                    <SelectItem key={s ?? "none"} value={s ?? ""}>{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Report tabs */}
      <Tabs defaultValue="production">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="production">Produção</TabsTrigger>
          <TabsTrigger value="changes">Alterações</TabsTrigger>
          <TabsTrigger value="nutritional">Evolução Nutricional</TabsTrigger>
        </TabsList>

        {/* ── Produção ── */}
        <TabsContent value="production" className="mt-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="flex items-center gap-2 text-base">
                  <BarChart3 className="w-4 h-4" />Relatório de Produção
                </CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">{periodLabel}</p>
              </div>
              <Button size="sm" variant="outline"
                onClick={() => exportJSON(dietData ?? localStats, 'Relatorio_Producao')}>
                <Download className="w-4 h-4 mr-2" />Exportar
              </Button>
            </CardHeader>
            <CardContent>
              {loading ? <LoadingRows /> : (
                <>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <StatBox label="Total de Pacientes" value={localStats.total} color="text-blue-600" />
                    <StatBox label="Setores Ativos"     value={localStats.setores} color="text-green-600" />
                    <StatBox label="Total de Alergias"  value={localStats.alergias} color="text-red-600" />
                    <StatBox label="Restrições"         value={localStats.restricoes} color="text-orange-600" />
                  </div>

                  {dietData && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {dietData.por_tipo_dieta && (
                        <SectionTable title="Distribuição por Tipo de Dieta" rows={dietData.por_tipo_dieta} />
                      )}
                      {dietData.por_setor && (
                        <SectionTable title="Distribuição por Setor" rows={dietData.por_setor} />
                      )}
                    </div>
                  )}

                  {!dietData && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div>
                        <p className="text-sm font-medium mb-3">Pacientes por setor</p>
                        <div className="space-y-1.5">
                          {[...new Set(patients.map(p => p.setor_nome).filter(Boolean))].map(s => (
                            <div key={s} className="flex justify-between items-center text-sm">
                              <span>{s}</span>
                              <Badge variant="secondary">{patients.filter(p => p.setor_nome === s).length}</Badge>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Alterações ── */}
        <TabsContent value="changes" className="mt-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="flex items-center gap-2 text-base">
                  <TrendingUp className="w-4 h-4" />Relatório de Alterações
                </CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">{periodLabel}</p>
              </div>
              <Button size="sm" variant="outline"
                onClick={() => exportJSON(altData ?? {}, 'Relatorio_Alteracoes')}>
                <Download className="w-4 h-4 mr-2" />Exportar
              </Button>
            </CardHeader>
            <CardContent>
              {loading ? <LoadingRows /> : altData ? (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <StatBox label="Total de Alterações" value={altData.total ?? altData.length ?? '—'} color="text-blue-600" />
                    <StatBox label="Urgentes" value={altData.urgentes ?? '—'} color="text-red-600" />
                    <StatBox label="Notificadas" value={altData.notificadas ?? '—'} color="text-green-600" />
                  </div>
                  {altData.alteracoes && (
                    <div className="space-y-3">
                      {altData.alteracoes.slice(0, 10).map((a: any, i: number) => (
                        <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg text-sm">
                          <div className="flex-1">
                            <p className="font-medium">{a.paciente_nome}</p>
                            <p className="text-muted-foreground text-xs">{a.dieta_anterior} → {a.dieta_nova}</p>
                            {a.motivo && <p className="text-xs mt-1 text-gray-600">{a.motivo}</p>}
                          </div>
                          <span className="text-xs text-muted-foreground whitespace-nowrap">
                            {a.data ? new Date(a.data).toLocaleDateString('pt-BR') : '—'}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <div className="py-12 text-center text-muted-foreground text-sm">
                  <FileText className="w-10 h-10 mx-auto mb-3 opacity-30" />
                  Dados de alterações não disponíveis no momento.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Evolução Nutricional ── */}
        <TabsContent value="nutritional" className="mt-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="flex items-center gap-2 text-base">
                  <PieChart className="w-4 h-4" />Evolução Nutricional
                </CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">{periodLabel}</p>
              </div>
              <Button size="sm" variant="outline"
                onClick={() => exportJSON(localStats, 'Relatorio_Nutricional')}>
                <Download className="w-4 h-4 mr-2" />Exportar
              </Button>
            </CardHeader>
            <CardContent>
              {loading ? <LoadingRows /> : (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <StatBox label="Total Pacientes"     value={localStats.total}    color="text-blue-600" />
                    <StatBox label="Com Alergias"        value={patients.filter(p => (p.alergias?.length ?? 0) > 0).length} color="text-red-600" />
                    <StatBox label="Com Restrições"      value={patients.filter(p => (p.restricoes_alimentares?.length ?? 0) > 0).length} color="text-orange-600" />
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-red-50 rounded-xl p-5">
                      <h4 className="font-semibold text-red-800 mb-3">Indicadores de Segurança</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-sm text-red-700">Total de alergias registradas</span>
                          <span className="font-bold text-red-900">{localStats.alergias}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-red-700">Total de restrições alimentares</span>
                          <span className="font-bold text-red-900">{localStats.restricoes}</span>
                        </div>
                      </div>
                    </div>
                    <div className="bg-blue-50 rounded-xl p-5">
                      <h4 className="font-semibold text-blue-800 mb-3">Cobertura de Setores</h4>
                      <div className="space-y-1.5">
                        {[...new Set(patients.map(p => p.setor_nome).filter(Boolean))].map(s => (
                          <div key={s} className="flex justify-between text-sm">
                            <span className="text-blue-700">{s}</span>
                            <span className="font-semibold text-blue-900">
                              {patients.filter(p => p.setor_nome === s).length} paciente(s)
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <Card>
        <CardContent className="py-3 px-5">
          <div className="flex items-center justify-center text-xs text-muted-foreground gap-2">
            <Clock className="w-3.5 h-3.5" />
            Gerado em {new Date().toLocaleString('pt-BR')} · Período: {periodLabel} · Setor: {sector === 'all' ? 'Todos' : sector}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ── Helpers ───────────────────────────────────────────────────────────────────
const StatBox: React.FC<{ label: string; value: any; color: string }> = ({ label, value, color }) => (
  <div className="text-center bg-gray-50 rounded-xl p-4">
    <div className={`text-3xl font-bold ${color}`}>{value}</div>
    <p className="text-xs text-muted-foreground mt-1">{label}</p>
  </div>
);

const SectionTable: React.FC<{ title: string; rows: Record<string, number> }> = ({ title, rows }) => (
  <div>
    <p className="text-sm font-medium mb-2">{title}</p>
    <div className="space-y-1.5">
      {Object.entries(rows).map(([k, v]) => (
        <div key={k} className="flex justify-between items-center text-sm">
          <span>{k}</span>
          <Badge variant="secondary">{v}</Badge>
        </div>
      ))}
    </div>
  </div>
);

const LoadingRows = () => (
  <div className="space-y-3 py-4">
    {[1,2,3].map(i => <div key={i} className="h-8 bg-gray-100 rounded animate-pulse" />)}
  </div>
);