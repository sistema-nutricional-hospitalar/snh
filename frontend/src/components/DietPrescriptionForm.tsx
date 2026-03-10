import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ArrowLeft, Save, AlertTriangle, Loader2, X, Plus, Trash2 } from 'lucide-react';
import { Patient, Prescricao } from '../types';
import { useApp } from '../contexts/AppContext';
import { apiCreatePrescription, apiUpdatePrescription } from '../lib/api';
import { toast } from 'sonner';

type TipoDieta = 'oral' | 'enteral' | 'parenteral' | 'mista';

const DIET_DESCRIPTIONS: Record<string, string[]> = {
  oral: [
    'Dieta Geral', 'Dieta Hipossódica', 'Dieta Hipocalórica',
    'Dieta Diabética', 'Dieta Líquida', 'Dieta Pastosa', 'Dieta Mole',
  ],
  enteral: [
    'Dieta Enteral Padrão', 'Dieta Enteral Hipercalórica',
    'Dieta Enteral Hiperproteica', 'Dieta Enteral Normocalórica', 'Dieta Enteral com Fibras',
  ],
  parenteral: [
    'Nutrição Parenteral Total (NPT)', 'Nutrição Parenteral Periférica (NPP)',
    'Nutrição Parenteral Central', 'Nutrição Parenteral Suplementar',
  ],
  mista: [
    'Transição Enteral → Oral', 'Reforço Nutricional (Oral + Parenteral)',
    'Desmame Enteral', 'Nutrição Combinada Personalizada',
  ],
};

const CONSISTENCY_OPTIONS = ['Normal', 'Pastosa', 'Líquida', 'Branda'];
const VIAS_INFUSAO        = ['nasogástrica', 'nasoentérica', 'gastrostomia', 'jejunostomia', 'cateter central'];
const TIPOS_EQUIPO        = ['bomba', 'gravitacional'];  // 'seringa' removido: backend só aceita bomba/gravitacional
const TIPOS_ACESSO        = ['periférico', 'central', 'cateter central', 'picc'];
const COMPOSICOES_PADRAO  = [
  'Glicose 50% + Aminoácidos 10% + Lipídios 20%',
  'Glicose 25% + Aminoácidos 8.5%',
  'Aminoácidos 10% + Glicose 50%',
  'Solução 3 em 1 (glicose + AA + lipídios)',
];
const TIPOS_MISTA_COMPONENTE: TipoDieta[] = ['oral', 'enteral', 'parenteral'];

const COMMON_RESTRICTIONS = ['Sal', 'Açúcar', 'Lactose', 'Glúten', 'Conservantes', 'Corantes', 'Gordura Trans', 'Fritura'];
const COMMON_SUPPLEMENTS  = ['Vitamina D', 'Vitamina B12', 'Complexo B', 'Vitamina C', 'Ferro', 'Cálcio', 'Magnésio', 'Ômega 3'];

interface ComponenteMisto {
  tipo: 'oral' | 'enteral' | 'parenteral';
  percentual: string;
  // oral
  textura: string;
  numero_refeicoes: string;
  // enteral
  via_infusao: string;
  velocidade_ml_h: string;
  quantidade_gramas_porcao: string;
  porcoes_diarias: string;
  tipo_equipo: string;
  // parenteral
  tipo_acesso: string;
  volume_ml_dia: string;
  composicao: string;
  velocidade_par_ml_h: string;
}

const defaultComponente = (): ComponenteMisto => ({
  tipo: 'oral',
  percentual: '50',
  textura: 'normal',
  numero_refeicoes: '5',
  via_infusao: 'nasogástrica',
  velocidade_ml_h: '60',
  quantidade_gramas_porcao: '300',
  porcoes_diarias: '5',
  tipo_equipo: 'bomba',
  tipo_acesso: 'central',
  volume_ml_dia: '2000',
  composicao: COMPOSICOES_PADRAO[0],
  velocidade_par_ml_h: '83',
});

interface Props {
  patient: Patient;
  activePrescription?: Prescricao | null;
  onBack: () => void;
  onSuccess: () => void;
}

export const DietPrescriptionForm: React.FC<Props> = ({ patient, activePrescription, onBack, onSuccess }) => {
  const { currentUser, refreshPatients } = useApp();
  const existing   = activePrescription?.dieta_atual;
  const tipoInicial = (['oral', 'enteral', 'parenteral', 'mista'].includes(existing?.tipo ?? '')
    ? existing!.tipo : 'oral') as TipoDieta;

  const [tipo,       setTipo]      = useState<TipoDieta>(tipoInicial);
  const [descricao,  setDescricao] = useState(existing?.descricao ?? DIET_DESCRIPTIONS[tipoInicial][0]);
  const [calorias,   setCalorias]  = useState(String(existing?.calorias ?? '2000'));
  const [motivo,     setMotivo]    = useState('');
  const [observacoes, setObservacoes] = useState(existing?.observacoes ?? '');
  const [restricoes, setRestricoes] = useState<string[]>(existing?.restricoes ?? []);
  const [suplementos, setSupl]     = useState<string[]>(existing?.suplementos ?? []);
  const [newRestr,   setNewRestr]  = useState('');
  const [newSupl,    setNewSuplV]  = useState('');
  const [saving,     setSaving]    = useState(false);

  // Oral
  const [consistencia,    setConsistencia]   = useState(existing?.consistencia ?? 'Normal');
  const [numRefeicoes,    setNumRefeicoes]   = useState('5');

  // Enteral — pré-preenchido da prescrição existente quando disponível
  const [viaInfusao,      setViaInfusao]     = useState(existing?.via_infusao ?? 'nasogástrica');
  const [velocidade,      setVelocidade]     = useState(String(existing?.velocidade_ml_h ?? '60'));
  const [qtdGramas,       setQtdGramas]      = useState(String(existing?.quantidade_gramas_por_porcao ?? '300'));
  const [porcoesDiarias,  setPorcoesDiarias] = useState(String(existing?.porcoes_diarias ?? '5'));
  const [tipoEquipo,      setTipoEquipo]     = useState(existing?.tipo_equipo ?? 'bomba');

  // Parenteral — pré-preenchido da prescrição existente quando disponível
  const [tipoAcesso,      setTipoAcesso]     = useState(existing?.tipo_acesso ?? 'central');
  const [volumeMlDia,     setVolumeMlDia]    = useState(String(existing?.volume_ml_dia ?? '2000'));
  const [composicao,      setComposicao]     = useState(existing?.composicao ?? COMPOSICOES_PADRAO[0]);
  const [velocidadePar,   setVelocidadePar]  = useState(String(existing?.velocidade_ml_h ?? '83'));

  // Mista — lista de componentes
  const [componentes, setComponentes] = useState<ComponenteMisto[]>([
    { ...defaultComponente(), tipo: 'oral',    percentual: '70' },
    { ...defaultComponente(), tipo: 'enteral', percentual: '30' },
  ]);

  const handleTipoChange = (v: TipoDieta) => {
    setTipo(v);
    setDescricao(DIET_DESCRIPTIONS[v][0]);
  };

  // ── Componentes da Mista ──────────────────────────────────────────
  const addComponente = () => {
    if (componentes.length >= 4) { toast.warning('Máximo de 4 componentes na dieta mista.'); return; }
    setComponentes(c => [...c, defaultComponente()]);
  };
  const removeComponente = (i: number) => setComponentes(c => c.filter((_, idx) => idx !== i));
  const updateComponente = (i: number, patch: Partial<ComponenteMisto>) =>
    setComponentes(c => c.map((comp, idx) => idx === i ? { ...comp, ...patch } : comp));

  // ── Restrições / Suplementos ──────────────────────────────────────
  const addRestr = (v = newRestr) => { if (v && !restricoes.includes(v)) { setRestricoes(r => [...r, v]); setNewRestr(''); } };
  const rmRestr  = (v: string) => setRestricoes(r => r.filter(x => x !== v));
  const addSuplF = (v = newSupl) => { if (v && !suplementos.includes(v)) { setSupl(s => [...s, v]); setNewSuplV(''); } };
  const rmSupl   = (v: string) => setSupl(s => s.filter(x => x !== v));

  // ── Submit ────────────────────────────────────────────────────────
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (activePrescription && !motivo.trim()) { toast.error('Informe o motivo da alteração da dieta.'); return; }

    if (tipo === 'mista') {
      const total = componentes.reduce((s, c) => s + (parseFloat(c.percentual) || 0), 0);
      if (total < 95 || total > 105) {
        toast.error(`A soma dos percentuais deve ser 100% (atual: ${total.toFixed(0)}%).`);
        return;
      }
      if (componentes.length < 2) { toast.error('Dieta mista requer pelo menos 2 componentes.'); return; }
    }

    setSaving(true);
    try {
      let dados_dieta: Record<string, any> = {
        descricao:           `${descricao} — ${motivo}`.trim(),
        usuario_responsavel: currentUser?.nome ?? 'nutricionista',
        restricoes,
        suplementos,
        observacoes,
      };

      if (tipo === 'oral') {
        dados_dieta.textura          = consistencia.toLowerCase();
        dados_dieta.numero_refeicoes = parseInt(numRefeicoes) || 5;
        dados_dieta.tipo_refeicao    = 'desjejum';
      } else if (tipo === 'enteral') {
        dados_dieta.via_infusao                     = viaInfusao;
        dados_dieta.velocidade_ml_h                 = parseFloat(velocidade) || 60;
        dados_dieta['quantidade_gramas_por_porção']  = parseFloat(qtdGramas) || 300;
        dados_dieta.porcoes_diarias                 = parseInt(porcoesDiarias) || 5;
        dados_dieta.tipo_equipo                     = tipoEquipo;
      } else if (tipo === 'parenteral') {
        dados_dieta.tipo_acesso    = tipoAcesso;
        dados_dieta.volume_ml_dia  = parseFloat(volumeMlDia) || 2000;
        dados_dieta.composicao     = composicao;
        dados_dieta.velocidade_ml_h = parseFloat(velocidadePar) || 83;
      } else if (tipo === 'mista') {
        dados_dieta.componentes_raw = componentes.map(c => {
          const base: Record<string, any> = { tipo: c.tipo, percentual: parseFloat(c.percentual) || 50 };
          if (c.tipo === 'oral') {
            base.textura          = c.textura;
            base.numero_refeicoes = parseInt(c.numero_refeicoes) || 5;
            base.tipo_refeicao    = 'desjejum';
          } else if (c.tipo === 'enteral') {
            base.via_infusao                    = c.via_infusao;
            base.velocidade_ml_h                = parseFloat(c.velocidade_ml_h) || 60;
            base['quantidade_gramas_por_porção'] = parseFloat(c.quantidade_gramas_porcao) || 300;
            base.porcoes_diarias                = parseInt(c.porcoes_diarias) || 5;
            base.tipo_equipo                    = c.tipo_equipo;
          } else if (c.tipo === 'parenteral') {
            base.tipo_acesso     = c.tipo_acesso;
            base.volume_ml_dia   = parseFloat(c.volume_ml_dia) || 2000;
            base.composicao      = c.composicao;
            base.velocidade_ml_h = parseFloat(c.velocidade_par_ml_h) || 83;
          }
          return base;
        });
      }

      const payload = { tipo_dieta: tipo, dados_dieta };
      if (activePrescription) {
        await apiUpdatePrescription(activePrescription.id, payload);
      } else {
        await apiCreatePrescription(patient.id, payload);
      }

      toast.success('Dieta prescrita com sucesso! Notificação enviada para a equipe.');
      onSuccess();
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? 'Erro ao salvar prescrição.';
      toast.error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setSaving(false);
    }
  };

  const selectCls = 'bg-white border border-gray-300';
  const inputCls  = 'bg-white border border-gray-300';

  // Soma de percentuais para feedback em tempo real (mista)
  const totalPerc = componentes.reduce((s, c) => s + (parseFloat(c.percentual) || 0), 0);
  const percOk    = totalPerc >= 95 && totalPerc <= 105;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={onBack}>
          <ArrowLeft className="w-4 h-4 mr-2" />Voltar
        </Button>
        <div>
          <h1>Prescrição de Dieta</h1>
          <p className="text-sm text-muted-foreground">{patient.nome} · Quarto {patient.quarto}{patient.leito}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* ── Informações da dieta ─────────────────────────────── */}
          <Card>
            <CardHeader><CardTitle>Informações da Dieta</CardTitle></CardHeader>
            <CardContent className="space-y-4">

              <div className="space-y-1">
                <Label>Tipo de Dieta</Label>
                <Select value={tipo} onValueChange={(v) => handleTipoChange(v as TipoDieta)}>
                  <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-white">
                    <SelectItem value="oral">Oral</SelectItem>
                    <SelectItem value="enteral">Enteral</SelectItem>
                    <SelectItem value="parenteral">Parenteral</SelectItem>
                    <SelectItem value="mista">Mista</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <Label>Descrição</Label>
                <Select value={descricao} onValueChange={setDescricao}>
                  <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-white">
                    {DIET_DESCRIPTIONS[tipo].map((d) => <SelectItem key={d} value={d}>{d}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>

              {/* ── ORAL ─────────────────────────────────────── */}
              {tipo === 'oral' && (<>
                <div className="space-y-1">
                  <Label>Consistência</Label>
                  <Select value={consistencia} onValueChange={setConsistencia}>
                    <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-white">
                      {CONSISTENCY_OPTIONS.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Número de Refeições/dia</Label>
                  <Input type="number" value={numRefeicoes} min="1" max="10" className={inputCls}
                    onChange={(e) => setNumRefeicoes(e.target.value)} />
                </div>
                <div className="space-y-1">
                  <Label>Calorias (kcal/dia)</Label>
                  <Input type="number" value={calorias} min="800" max="4000" className={inputCls}
                    onChange={(e) => setCalorias(e.target.value)} />
                </div>
              </>)}

              {/* ── ENTERAL ──────────────────────────────────── */}
              {tipo === 'enteral' && (<>
                <div className="space-y-1">
                  <Label>Via de Infusão</Label>
                  <Select value={viaInfusao} onValueChange={setViaInfusao}>
                    <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-white">
                      {VIAS_INFUSAO.map((v) => <SelectItem key={v} value={v}>{v.charAt(0).toUpperCase() + v.slice(1)}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Velocidade (ml/h)</Label>
                  <Input type="number" value={velocidade} min="10" max="200" className={inputCls}
                    onChange={(e) => setVelocidade(e.target.value)} />
                </div>
                <div className="space-y-1">
                  <Label>Quantidade por Porção (g)</Label>
                  <Input type="number" value={qtdGramas} min="50" max="1000" className={inputCls}
                    onChange={(e) => setQtdGramas(e.target.value)} />
                </div>
                <div className="space-y-1">
                  <Label>Porções/dia</Label>
                  <Input type="number" value={porcoesDiarias} min="1" max="10" className={inputCls}
                    onChange={(e) => setPorcoesDiarias(e.target.value)} />
                </div>
                <div className="space-y-1">
                  <Label>Tipo de Equipo</Label>
                  <Select value={tipoEquipo} onValueChange={setTipoEquipo}>
                    <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-white">
                      {TIPOS_EQUIPO.map((t) => <SelectItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Calorias (kcal/dia)</Label>
                  <Input type="number" value={calorias} min="800" max="4000" className={inputCls}
                    onChange={(e) => setCalorias(e.target.value)} />
                </div>
              </>)}

              {/* ── PARENTERAL ───────────────────────────────── */}
              {tipo === 'parenteral' && (<>
                <div className="space-y-1">
                  <Label>Tipo de Acesso Venoso</Label>
                  <Select value={tipoAcesso} onValueChange={setTipoAcesso}>
                    <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-white">
                      {TIPOS_ACESSO.map((t) => <SelectItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Volume Total/dia (ml)</Label>
                  <Input type="number" value={volumeMlDia} min="100" max="5000" className={inputCls}
                    onChange={(e) => setVolumeMlDia(e.target.value)} />
                </div>
                <div className="space-y-1">
                  <Label>Composição</Label>
                  <Select value={composicao} onValueChange={setComposicao}>
                    <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-white">
                      {COMPOSICOES_PADRAO.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Velocidade de Infusão (ml/h)</Label>
                  <Input type="number" value={velocidadePar} min="10" max="300" className={inputCls}
                    onChange={(e) => setVelocidadePar(e.target.value)} />
                  <p className="text-xs text-gray-500 mt-1">
                    Volume infundido em 24h: {(parseFloat(velocidadePar) * 24).toFixed(0)} ml
                    {Math.abs((parseFloat(velocidadePar) * 24) - parseFloat(volumeMlDia)) / parseFloat(volumeMlDia) > 0.2
                      ? <span className="text-red-500 ml-1">⚠ Diferença &gt;20% em relação ao volume/dia</span>
                      : <span className="text-green-600 ml-1">✓ Dentro da tolerância</span>}
                  </p>
                </div>
              </>)}

              {/* ── MISTA ────────────────────────────────────── */}
              {tipo === 'mista' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label>Componentes</Label>
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${percOk ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      Total: {totalPerc.toFixed(0)}%{percOk ? ' ✓' : ' (deve ser 100%)'}
                    </span>
                  </div>

                  {componentes.map((comp, i) => (
                    <div key={i} className="border rounded-lg p-3 space-y-2 bg-gray-50">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-gray-600">Componente {i + 1}</span>
                        {componentes.length > 2 && (
                          <button type="button" onClick={() => removeComponente(i)} className="text-red-400 hover:text-red-600">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-1">
                          <Label className="text-xs">Tipo</Label>
                          <Select value={comp.tipo} onValueChange={(v) => updateComponente(i, { tipo: v as 'oral' | 'enteral' | 'parenteral' })}>
                            <SelectTrigger className="bg-white border border-gray-300 h-8 text-sm"><SelectValue /></SelectTrigger>
                            <SelectContent className="bg-white">
                              {TIPOS_MISTA_COMPONENTE.map(t => <SelectItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</SelectItem>)}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs">Percentual (%)</Label>
                          <Input type="number" value={comp.percentual} min="1" max="99" className="bg-white border border-gray-300 h-8 text-sm"
                            onChange={(e) => updateComponente(i, { percentual: e.target.value })} />
                        </div>
                      </div>

                      {comp.tipo === 'oral' && (
                        <div className="grid grid-cols-2 gap-2">
                          <div className="space-y-1">
                            <Label className="text-xs">Consistência</Label>
                            <Select value={comp.textura} onValueChange={(v) => updateComponente(i, { textura: v })}>
                              <SelectTrigger className="bg-white border border-gray-300 h-8 text-sm"><SelectValue /></SelectTrigger>
                              <SelectContent className="bg-white">
                                {CONSISTENCY_OPTIONS.map(c => <SelectItem key={c} value={c.toLowerCase()}>{c}</SelectItem>)}
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-1">
                            <Label className="text-xs">Refeições/dia</Label>
                            <Input type="number" value={comp.numero_refeicoes} min="1" max="10" className="bg-white border border-gray-300 h-8 text-sm"
                              onChange={(e) => updateComponente(i, { numero_refeicoes: e.target.value })} />
                          </div>
                        </div>
                      )}

                      {comp.tipo === 'enteral' && (
                        <div className="grid grid-cols-2 gap-2">
                          <div className="space-y-1">
                            <Label className="text-xs">Via de Infusão</Label>
                            <Select value={comp.via_infusao} onValueChange={(v) => updateComponente(i, { via_infusao: v })}>
                              <SelectTrigger className="bg-white border border-gray-300 h-8 text-sm"><SelectValue /></SelectTrigger>
                              <SelectContent className="bg-white">
                                {VIAS_INFUSAO.map(v => <SelectItem key={v} value={v}>{v}</SelectItem>)}
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-1">
                            <Label className="text-xs">Velocidade (ml/h)</Label>
                            <Input type="number" value={comp.velocidade_ml_h} min="10" max="200" className="bg-white border border-gray-300 h-8 text-sm"
                              onChange={(e) => updateComponente(i, { velocidade_ml_h: e.target.value })} />
                          </div>
                        </div>
                      )}

                      {comp.tipo === 'parenteral' && (
                        <div className="grid grid-cols-2 gap-2">
                          <div className="space-y-1">
                            <Label className="text-xs">Tipo de Acesso</Label>
                            <Select value={comp.tipo_acesso} onValueChange={(v) => updateComponente(i, { tipo_acesso: v })}>
                              <SelectTrigger className="bg-white border border-gray-300 h-8 text-sm"><SelectValue /></SelectTrigger>
                              <SelectContent className="bg-white">
                                {TIPOS_ACESSO.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-1">
                            <Label className="text-xs">Volume/dia (ml)</Label>
                            <Input type="number" value={comp.volume_ml_dia} min="100" max="5000" className="bg-white border border-gray-300 h-8 text-sm"
                              onChange={(e) => updateComponente(i, { volume_ml_dia: e.target.value })} />
                          </div>
                          <div className="col-span-2 space-y-1">
                            <Label className="text-xs">Velocidade (ml/h)</Label>
                            <Input type="number" value={comp.velocidade_par_ml_h} min="10" max="300" className="bg-white border border-gray-300 h-8 text-sm"
                              onChange={(e) => updateComponente(i, { velocidade_par_ml_h: e.target.value })} />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}

                  {componentes.length < 4 && (
                    <Button type="button" variant="outline" size="sm" className="w-full" onClick={addComponente}>
                      <Plus className="w-4 h-4 mr-1" />Adicionar Componente
                    </Button>
                  )}
                </div>
              )}

              <div className="space-y-1">
                <Label>{activePrescription ? 'Motivo da Alteração *' : 'Observações / Motivo'}</Label>
                <Textarea value={motivo} onChange={(e) => setMotivo(e.target.value)}
                  placeholder={activePrescription ? "Descreva o motivo da alteração..." : "Observações iniciais (opcional)..."}
                  rows={3} className={inputCls} required={!!activePrescription} />
              </div>
            </CardContent>
          </Card>

          {/* ── Restrições e Suplementos ─────────────────────────── */}
          <Card>
            <CardHeader><CardTitle>Restrições e Suplementos</CardTitle></CardHeader>
            <CardContent className="space-y-5">
              <div>
                <Label>Restrições Alimentares</Label>
                <div className="flex gap-2 mt-2">
                  <Input value={newRestr} className={inputCls} onChange={(e) => setNewRestr(e.target.value)}
                    placeholder="Digite uma restrição..."
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addRestr(); } }} />
                  <Button type="button" size="sm" onClick={() => addRestr()}>+</Button>
                </div>
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {COMMON_RESTRICTIONS.map((r) => (
                    <Button key={r} type="button" variant="outline" size="sm"
                      className={`h-7 text-xs ${restricoes.includes(r) ? 'bg-red-50 border-red-200 text-red-700' : 'bg-white'}`}
                      onClick={() => restricoes.includes(r) ? rmRestr(r) : addRestr(r)}>{r}</Button>
                  ))}
                </div>
                {restricoes.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {restricoes.map((r) => (
                      <span key={r} className="flex items-center gap-1 bg-red-50 text-red-800 text-xs px-2 py-1 rounded-full border border-red-200">
                        <AlertTriangle className="w-3 h-3" />{r}
                        <button type="button" onClick={() => rmRestr(r)} className="ml-0.5 text-red-600 hover:text-red-900"><X className="w-3 h-3" /></button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <Label>Suplementos</Label>
                <div className="flex gap-2 mt-2">
                  <Input value={newSupl} className={inputCls} onChange={(e) => setNewSuplV(e.target.value)}
                    placeholder="Digite um suplemento..."
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addSuplF(); } }} />
                  <Button type="button" size="sm" onClick={() => addSuplF()}>+</Button>
                </div>
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {COMMON_SUPPLEMENTS.map((s) => (
                    <Button key={s} type="button" variant="outline" size="sm"
                      className={`h-7 text-xs ${suplementos.includes(s) ? 'bg-green-50 border-green-200 text-green-700' : 'bg-white'}`}
                      onClick={() => suplementos.includes(s) ? rmSupl(s) : addSuplF(s)}>{s}</Button>
                  ))}
                </div>
                {suplementos.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {suplementos.map((s) => (
                      <span key={s} className="flex items-center gap-1 bg-green-50 text-green-800 text-xs px-2 py-1 rounded-full border border-green-200">
                        {s}
                        <button type="button" onClick={() => rmSupl(s)} className="ml-0.5"><X className="w-3 h-3" /></button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Observações Adicionais</CardTitle></CardHeader>
          <CardContent>
            <Textarea value={observacoes} onChange={(e) => setObservacoes(e.target.value)}
              placeholder="Instruções especiais, horários, preparo..." rows={3} className={inputCls} />
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={onBack}>Cancelar</Button>
          <Button type="submit" disabled={saving} className="bg-blue-600 hover:bg-blue-700">
            {saving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Salvando...</> : <><Save className="w-4 h-4 mr-2" />Prescrever Dieta</>}
          </Button>
        </div>
      </form>
    </div>
  );
};