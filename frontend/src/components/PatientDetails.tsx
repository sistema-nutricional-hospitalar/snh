import React, { useEffect, useState } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Skeleton } from './ui/skeleton';
import {
  ArrowLeft, Edit, Calendar, User, Heart, AlertTriangle,
  Clock, Utensils, RefreshCw, Trash2,
} from 'lucide-react';
import { Patient, Prescricao } from '../types';
import { DietPrescriptionForm } from './DietPrescriptionForm';
import { DietHistory } from './DietHistory';
import { apiGetPatientPrescriptions, apiDeletePatient } from '../lib/api';
import { useApp } from '../contexts/AppContext';

interface Props {
  patient: Patient;
  onBack: () => void;
  onDelete?: () => Promise<void>;
}

function calcAge(dob: string) {
  const birth = new Date(dob);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
  return age;
}

function bmiInfo(weight?: number | null, height?: number | null) {
  if (!weight || !height) return null;
  const h = height / 100;
  const bmi = weight / (h * h);
  let cat = 'Peso normal';
  let color = 'text-green-600';
  if (bmi < 18.5) { cat = 'Abaixo do peso'; color = 'text-blue-600'; }
  else if (bmi >= 25 && bmi < 30) { cat = 'Sobrepeso'; color = 'text-yellow-600'; }
  else if (bmi >= 30) { cat = 'Obesidade'; color = 'text-red-600'; }
  return { value: bmi.toFixed(1), cat, color };
}

export const PatientDetails: React.FC<Props> = ({ patient, onBack, onDelete }) => {
  const { currentUser } = useApp();
  const [showPrescForm, setShowPrescForm] = useState(false);
  const [prescricoes, setPrescricoes]     = useState<Prescricao[]>([]);
  const [loadingPresc, setLoadingPresc]   = useState(true);

  const canPrescribe = ['nutricionista', 'admin'].includes(currentUser?.tipo ?? '');
  const canDelete    = ['nutricionista', 'admin'].includes(currentUser?.tipo ?? '');

  const [showConfirmDelete, setShowConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await apiDeletePatient(patient.id);
      await onDelete?.();  // aguarda refresh antes de navegar
    } catch {
      setDeleting(false);
      setShowConfirmDelete(false);
    }
  };

  const loadPrescricoes = () => {
    setLoadingPresc(true);
    apiGetPatientPrescriptions(patient.id)
      .then(setPrescricoes)
      .catch(() => {})
      .finally(() => setLoadingPresc(false));
  };

  useEffect(() => { loadPrescricoes(); }, [patient.id]);

  const activePrescricao = prescricoes.find((p) => p.status === 'ativa') ?? null;
  const diet = activePrescricao?.dieta_atual;
  const bmi  = bmiInfo(patient.peso_atual, patient.altura);

  if (showPrescForm) {
    return (
      <DietPrescriptionForm
        patient={patient}
        activePrescription={activePrescricao}
        onBack={() => setShowPrescForm(false)}
        onSuccess={() => { setShowPrescForm(false); loadPrescricoes(); }}
      />
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={onBack}>
            <ArrowLeft className="w-4 h-4 mr-1" />Voltar
          </Button>
          <div>
            <h1>{patient.nome}</h1>
            <p className="text-sm text-muted-foreground">
              Quarto {patient.quarto}{patient.leito} · {patient.setor_nome ?? '—'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {patient.restricoes_alimentares?.length > 0 && (
            <Badge className="bg-red-100 text-red-800 border-red-200">RESTRIÇÃO ALIMENTAR</Badge>
          )}
          {canPrescribe && (
            <Button onClick={() => setShowPrescForm(true)} className="bg-blue-600 hover:bg-blue-700">
              <Edit className="w-4 h-4 mr-2" />
              {activePrescricao ? 'Alterar Dieta' : 'Prescrever Dieta'}
            </Button>
          )}
          {canDelete && (
            <Button
              variant="outline"
              size="sm"
              className="border-red-200 text-red-600 hover:bg-red-50"
              onClick={() => setShowConfirmDelete(true)}
            >
              <Trash2 className="w-4 h-4 mr-1" />Excluir
            </Button>
          )}

          {/* Modal de confirmação */}
          {showConfirmDelete && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
              <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-sm mx-4 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="bg-red-100 rounded-full p-2">
                    <Trash2 className="w-5 h-5 text-red-600" />
                  </div>
                  <h2 className="text-base font-semibold">Excluir paciente?</h2>
                </div>
                <p className="text-sm text-muted-foreground">
                  Tem certeza que deseja excluir <strong>{patient.nome}</strong>? Esta ação é irreversível.
                </p>
                <div className="flex justify-end gap-2 pt-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowConfirmDelete(false)}
                    disabled={deleting}
                  >
                    Cancelar
                  </Button>
                  <Button
                    size="sm"
                    className="bg-red-600 hover:bg-red-700 text-white"
                    onClick={handleDelete}
                    disabled={deleting}
                  >
                    {deleting ? <><RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />Excluindo...</> : 'Confirmar exclusão'}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ── Painel esquerdo: dados do paciente ───────────────────────────── */}
        <Card className="lg:col-span-1 h-fit">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <User className="w-4 h-4" />Informações Pessoais
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <InfoRow label="Idade" value={patient.data_nascimento ? `${calcAge(patient.data_nascimento)} anos` : '—'} />
            <InfoRow label="Nascimento" value={patient.data_nascimento ? new Date(patient.data_nascimento).toLocaleDateString('pt-BR') : '—'} />
            <InfoRow label="Sexo" value={patient.sexo === 'M' ? 'Masculino' : patient.sexo === 'F' ? 'Feminino' : '—'} />
            <InfoRow
              label="Internado em"
              value={patient.data_internacao ? new Date(patient.data_internacao).toLocaleDateString('pt-BR') : '—'}
              icon={<Calendar className="w-3.5 h-3.5 text-muted-foreground" />}
            />

            {(patient.peso_atual || patient.altura) && (
              <InfoRow
                label="Peso / Altura"
                value={`${patient.peso_atual ?? '?'} kg / ${patient.altura ?? '?'} cm`}
              />
            )}

            {bmi && (
              <div>
                <p className="text-muted-foreground mb-0.5">IMC</p>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{bmi.value}</span>
                  <span className={`text-xs ${bmi.color}`}>({bmi.cat})</span>
                </div>
              </div>
            )}

            {patient.diagnostico && (
              <InfoRow label="Diagnóstico" value={patient.diagnostico} />
            )}

            {patient.alergias?.length > 0 && (
              <div>
                <p className="text-muted-foreground mb-1.5">Alergias</p>
                <div className="space-y-1">
                  {patient.alergias.map((a, i) => (
                    <Badge key={i} variant="destructive" className="flex w-fit items-center gap-1">
                      <AlertTriangle className="w-3 h-3" />{a}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {patient.restricoes_alimentares?.length > 0 && (
              <div>
                <p className="text-muted-foreground mb-1.5">Restrições</p>
                <div className="space-y-1">
                  {patient.restricoes_alimentares.map((r, i) => (
                    <Badge key={i} variant="outline" className="flex w-fit">{r}</Badge>
                  ))}
                </div>
              </div>
            )}

            {patient.observacoes && (
              <div>
                <p className="text-muted-foreground mb-1">Observações</p>
                <p className="bg-gray-50 rounded p-2 text-xs leading-relaxed">{patient.observacoes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* ── Painel direito: dieta + histórico ───────────────────────────── */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="current-diet">
            <TabsList>
              <TabsTrigger value="current-diet">Dieta Atual</TabsTrigger>
              <TabsTrigger value="history">Histórico</TabsTrigger>
            </TabsList>

            {/* Dieta Atual */}
            <TabsContent value="current-diet" className="mt-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Utensils className="w-4 h-4" />Dieta Atual
                  </CardTitle>
                  <Button variant="ghost" size="sm" onClick={loadPrescricoes} disabled={loadingPresc}>
                    <RefreshCw className={`w-4 h-4 ${loadingPresc ? 'animate-spin' : ''}`} />
                  </Button>
                </CardHeader>
                <CardContent>
                  {loadingPresc ? (
                    <div className="space-y-3">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-4 w-48" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                  ) : diet ? (
                    <div className="space-y-4 text-sm">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-muted-foreground mb-1">Tipo</p>
                          <Badge className={diet.tipo === 'enteral' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}>
                            {diet.tipo?.toUpperCase() ?? '—'}
                          </Badge>
                        </div>
                        <div>
                          <p className="text-muted-foreground mb-1">Consistência</p>
                          <p className="font-medium">{diet.consistencia ?? '—'}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground mb-1">Calorias</p>
                          <p className="font-medium">{diet.calorias ? `${diet.calorias} kcal/dia` : '—'}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground mb-1">Prescrito por</p>
                          <p className="font-medium">{activePrescricao?.nutricionista_nome ?? '—'}</p>
                        </div>
                      </div>

                      <div>
                        <p className="text-muted-foreground mb-1">Descrição</p>
                        <p className="font-semibold text-base">{diet.descricao}</p>
                      </div>

                      {/* Detalhes técnicos — Enteral */}
                      {diet.tipo === 'enteral' && (diet.via_infusao || diet.velocidade_ml_h != null) && (
                        <div>
                          <p className="text-muted-foreground mb-1.5">Parâmetros Enterais</p>
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            {diet.via_infusao && (
                              <div className="bg-blue-50 rounded-lg p-2.5">
                                <p className="text-xs text-muted-foreground">Via de Infusão</p>
                                <p className="font-medium capitalize">{diet.via_infusao}</p>
                              </div>
                            )}
                            {diet.velocidade_ml_h != null && (
                              <div className="bg-blue-50 rounded-lg p-2.5">
                                <p className="text-xs text-muted-foreground">Velocidade</p>
                                <p className="font-medium">{diet.velocidade_ml_h} ml/h</p>
                              </div>
                            )}
                            {diet.quantidade_gramas_por_porcao != null && (
                              <div className="bg-blue-50 rounded-lg p-2.5">
                                <p className="text-xs text-muted-foreground">Qtd. por Porção</p>
                                <p className="font-medium">{diet.quantidade_gramas_por_porcao} g</p>
                              </div>
                            )}
                            {diet.porcoes_diarias != null && (
                              <div className="bg-blue-50 rounded-lg p-2.5">
                                <p className="text-xs text-muted-foreground">Porções/dia · Equipo</p>
                                <p className="font-medium">{diet.porcoes_diarias}x · {diet.tipo_equipo ?? '—'}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {diet.restricoes?.length > 0 && (
                        <div>
                          <p className="text-muted-foreground mb-1.5">Restrições da Dieta</p>
                          <div className="flex flex-wrap gap-1.5">
                            {diet.restricoes.map((r, i) => <Badge key={i} variant="outline">{r}</Badge>)}
                          </div>
                        </div>
                      )}

                      {diet.suplementos?.length > 0 && (
                        <div>
                          <p className="text-muted-foreground mb-1.5">Suplementos</p>
                          <div className="flex flex-wrap gap-1.5">
                            {diet.suplementos.map((s, i) => <Badge key={i} variant="secondary">{s}</Badge>)}
                          </div>
                        </div>
                      )}

                      {diet.observacoes && (
                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-muted-foreground text-xs mb-1">Observações</p>
                          <p>{diet.observacoes}</p>
                        </div>
                      )}

                      {activePrescricao?.data_inicio && (
                        <div className="flex items-center text-xs text-muted-foreground pt-3 border-t">
                          <Clock className="w-3.5 h-3.5 mr-1" />
                          Prescrito em {new Date(activePrescricao.data_inicio).toLocaleString('pt-BR')}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="py-10 text-center">
                      <Utensils className="w-10 h-10 text-muted-foreground/30 mx-auto mb-3" />
                      <p className="text-sm text-muted-foreground">Nenhuma prescrição ativa.</p>
                      {canPrescribe && (
                        <Button className="mt-3" size="sm" onClick={() => setShowPrescForm(true)}>
                          Prescrever Dieta
                        </Button>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Histórico */}
            <TabsContent value="history" className="mt-4">
              <DietHistory patientId={patient.id} />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

const InfoRow: React.FC<{ label: string; value: string; icon?: React.ReactNode }> = ({ label, value, icon }) => (
  <div>
    <p className="text-muted-foreground mb-0.5">{label}</p>
    <div className="flex items-center gap-1.5 font-medium">
      {icon}{value}
    </div>
  </div>
);