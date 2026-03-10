import React, { useEffect, useState, useCallback } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { useApp } from '../contexts/AppContext';
import { Patient, Prescricao } from '../types';
import { apiGetPatientPrescriptions } from '../lib/api';
import {
  Search, MapPin, Clock, Utensils, AlertTriangle,
  RefreshCw, ArrowLeft, Heart,
} from 'lucide-react';

// ── Enriquece paciente com dieta ativa ────────────────────────────────────────
interface PatientWithDiet {
  patient: Patient;
  prescricao: Prescricao | null;
}

export const TouchDisplay: React.FC = () => {
  const { patients, refreshPatients, patientsLoading } = useApp();
  const [search, setSearch]             = useState('');
  const [selected, setSelected]         = useState<PatientWithDiet | null>(null);
  const [loadingDiet, setLoadingDiet]   = useState(false);
  const [refreshing, setRefreshing]     = useState(false);

  const filtered = patients.filter(p =>
    (p.nome?.toLowerCase().includes(search.toLowerCase())) ||
    (`${p.quarto}${p.leito}`.toLowerCase().includes(search.toLowerCase()))
  );

  const handleRefresh = async () => {
    setRefreshing(true);
    await refreshPatients();
    setRefreshing(false);
  };

  const selectPatient = async (patient: Patient) => {
    setLoadingDiet(true);
    setSelected({ patient, prescricao: null });
    try {
      const prescricoes = await apiGetPatientPrescriptions(patient.id);
      const active = prescricoes.find(p => p.status === 'ativa') ?? prescricoes[0] ?? null;
      setSelected({ patient, prescricao: active });
    } catch {
      setSelected({ patient, prescricao: null });
    } finally {
      setLoadingDiet(false);
    }
  };

  if (selected) {
    return (
      <DetailView
        data={selected}
        loading={loadingDiet}
        onBack={() => setSelected(null)}
      />
    );
  }

  return (
    <div className="min-h-[80vh] space-y-6 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Painel de Dietas</h1>
        <p className="text-gray-500 mt-1">Consulta rápida de informações nutricionais</p>
        <Button
          variant="outline" size="sm" className="mt-3"
          onClick={handleRefresh} disabled={refreshing || patientsLoading}
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Search bar — big, touch-friendly */}
      <Card className="shadow-md">
        <CardContent className="p-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground w-5 h-5" />
            <Input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Digite o nome ou quarto do paciente (ex: 101A)…"
              className="pl-12 h-14 text-lg text-center"
            />
          </div>
        </CardContent>
      </Card>

      {/* Patient grid */}
      {patientsLoading ? (
        <div className="text-center py-12 text-muted-foreground">Carregando…</div>
      ) : filtered.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <Search className="w-14 h-14 text-muted-foreground/30 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-800 mb-1">
              {search ? 'Paciente não encontrado' : 'Nenhum paciente cadastrado'}
            </h3>
            <p className="text-sm text-muted-foreground">
              {search ? 'Verifique o nome ou número do quarto.' : 'Os pacientes aparecerão aqui.'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.slice(0, 12).map(p => (
            <PatientCard key={p.id} patient={p} onClick={() => selectPatient(p)} />
          ))}
          {filtered.length > 12 && (
            <div className="col-span-full text-center text-sm text-muted-foreground py-3">
              Exibindo 12 de {filtered.length} pacientes. Refine a busca para ver outros.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ── Patient card (list view) ──────────────────────────────────────────────────
const PatientCard: React.FC<{ patient: Patient; onClick: () => void }> = ({ patient, onClick }) => (
  <Card
    className="cursor-pointer hover:shadow-lg hover:scale-[1.02] transition-all duration-200 border-2 hover:border-blue-300"
    onClick={onClick}
  >
    <CardContent className="p-5 text-center space-y-3">
      <div className="flex items-center justify-center gap-1.5 text-gray-700">
        <MapPin className="w-4 h-4 text-muted-foreground" />
        <span className="font-semibold">Quarto {patient.quarto}{patient.leito}</span>
        <span className="text-muted-foreground text-sm">· {patient.setor_nome ?? '—'}</span>
      </div>

      <h3 className="text-lg font-bold text-gray-900">{patient.nome}</h3>

      {patient.diagnostico && (
        <p className="text-sm text-muted-foreground line-clamp-1">{patient.diagnostico}</p>
      )}

      <div className="flex justify-center">
        <div className="bg-blue-50 rounded-lg px-4 py-2 flex items-center gap-2">
          <Utensils className="w-4 h-4 text-blue-600" />
          <span className="text-sm font-medium text-blue-800">Ver dieta</span>
        </div>
      </div>

      {patient.alergias?.length > 0 && (
        <div className="flex items-center justify-center gap-1 text-red-600 text-xs font-semibold">
          <AlertTriangle className="w-3.5 h-3.5" />
          {patient.alergias.length} alergia(s)
        </div>
      )}
    </CardContent>
  </Card>
);

// ── Detail view ───────────────────────────────────────────────────────────────
const DetailView: React.FC<{
  data: PatientWithDiet; loading: boolean; onBack: () => void;
}> = ({ data, loading, onBack }) => {
  const { patient, prescricao } = data;
  const diet = prescricao?.dieta_atual;

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex justify-center">
        <Button variant="outline" size="lg" onClick={onBack} className="px-8">
          <ArrowLeft className="w-4 h-4 mr-2" />Voltar à busca
        </Button>
      </div>

      <Card className="shadow-xl overflow-hidden">
        {/* Header colorido */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-8 text-center">
          <h2 className="text-3xl font-bold mb-2">{patient.nome}</h2>
          <div className="flex items-center justify-center gap-2 text-blue-100">
            <MapPin className="w-5 h-5" />
            <span className="text-xl">Quarto {patient.quarto}{patient.leito} · {patient.setor_nome ?? '—'}</span>
          </div>
        </div>

        <CardContent className="p-8">
          {loading ? (
            <div className="text-center py-10 text-muted-foreground">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-3" />
              Carregando dieta…
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Dieta */}
              <div className="space-y-4">
                <h3 className="text-xl font-bold flex items-center gap-2">
                  <Utensils className="w-5 h-5 text-blue-600" />Dieta Atual
                </h3>

                {diet ? (
                  <div className="bg-gray-50 rounded-xl p-5 space-y-3">
                    <Badge className={diet.tipo === 'enteral' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'} style={{ fontSize: 14, padding: '6px 14px' }}>
                      {diet.tipo?.toUpperCase()}
                    </Badge>
                    <p className="text-2xl font-bold text-gray-900">{diet.descricao}</p>
                    <div className="grid grid-cols-2 gap-3 text-center">
                      <div className="bg-white rounded-lg p-3">
                        <p className="text-xs text-muted-foreground">Consistência</p>
                        <p className="font-semibold">{diet.consistencia ?? '—'}</p>
                      </div>
                      <div className="bg-white rounded-lg p-3">
                        <p className="text-xs text-muted-foreground">Calorias</p>
                        <p className="font-semibold">{diet.calorias ? `${diet.calorias} kcal` : '—'}</p>
                      </div>
                    </div>

                    {diet.restricoes?.length > 0 && (
                      <div>
                        <p className="text-sm text-muted-foreground mb-1.5">Restrições da dieta</p>
                        <div className="flex flex-wrap gap-1.5">
                          {diet.restricoes.map((r, i) => <Badge key={i} variant="outline">{r}</Badge>)}
                        </div>
                      </div>
                    )}

                    {diet.suplementos?.length > 0 && (
                      <div>
                        <p className="text-sm text-muted-foreground mb-1.5">Suplementos</p>
                        <div className="flex flex-wrap gap-1.5">
                          {diet.suplementos.map((s, i) => <Badge key={i} variant="secondary">{s}</Badge>)}
                        </div>
                      </div>
                    )}

                    {diet.observacoes && (
                      <div className="bg-blue-50 rounded-lg p-3 text-sm text-blue-800">
                        <span className="font-medium">Obs:</span> {diet.observacoes}
                      </div>
                    )}

                    {prescricao?.data_inicio && (
                      <p className="text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        Prescrito em {new Date(prescricao.data_inicio).toLocaleString('pt-BR')}
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="bg-gray-50 rounded-xl p-8 text-center text-muted-foreground">
                    <Utensils className="w-10 h-10 mx-auto mb-2 opacity-30" />
                    Sem prescrição ativa
                  </div>
                )}
              </div>

              {/* Alergias + info */}
              <div className="space-y-4">
                {patient.alergias?.length > 0 && (
                  <div>
                    <h3 className="text-xl font-bold text-red-600 flex items-center gap-2 mb-3">
                      <AlertTriangle className="w-5 h-5" />ALERGIAS ALIMENTARES
                    </h3>
                    <div className="space-y-2">
                      {patient.alergias.map((a, i) => (
                        <div key={i} className="bg-red-50 border-2 border-red-300 rounded-xl p-4 text-center">
                          <p className="text-red-800 font-bold text-xl">⚠️ {a}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {patient.restricoes_alimentares?.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Restrições do paciente</h4>
                    <div className="flex flex-wrap gap-1.5">
                      {patient.restricoes_alimentares.map((r, i) => (
                        <Badge key={i} variant="outline" className="text-sm py-1 px-3">{r}</Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-gray-50 rounded-xl p-4 space-y-2 text-sm">
                  <h4 className="font-semibold mb-2">Informações do paciente</h4>
                  {patient.peso_atual && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Peso</span>
                      <span className="font-medium">{patient.peso_atual} kg</span>
                    </div>
                  )}
                  {patient.data_internacao && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Internado em</span>
                      <span className="font-medium">{new Date(patient.data_internacao).toLocaleDateString('pt-BR')}</span>
                    </div>
                  )}
                  {patient.diagnostico && (
                    <div className="flex justify-between gap-2">
                      <span className="text-muted-foreground flex-shrink-0">Diagnóstico</span>
                      <span className="font-medium text-right">{patient.diagnostico}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};