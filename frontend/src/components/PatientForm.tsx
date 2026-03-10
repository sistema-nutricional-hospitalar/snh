import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ArrowLeft, Save, Plus, X, Loader2 } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { apiCreatePatient, apiCreatePrescription } from '../lib/api';
import { toast } from 'sonner';

const SECTORS = ['UTI', 'Cardiologia', 'Neurologia', 'Pediatria', 'Oncologia', 'Ortopedia', 'Cirurgia Geral', 'Emergência'];
const DIET_TYPES = ['Dieta Geral', 'Dieta Hipossódica', 'Dieta Hipocalórica', 'Dieta Diabética', 'Dieta Líquida', 'Dieta Pastosa', 'Dieta Enteral Padrão', 'Dieta Enteral Hipercalórica'];
const VIAS_INFUSAO = ['nasogástrica', 'nasoentérica', 'gastrostomia', 'jejunostomia', 'cateter central'];
const TIPOS_EQUIPO = ['bomba', 'gravitacional'];
const TIPOS_ACESSO = ['periférico', 'central', 'cateter central', 'picc'];
const COMPOSICOES_PADRAO = [
  'Glicose 50% + Aminoácidos 10% + Lipídios 20%',
  'Glicose 25% + Aminoácidos 8.5%',
  'Aminoácidos 10% + Glicose 50%',
  'Solução 3 em 1 (glicose + AA + lipídios)',
];
const CONSISTENCY: Record<string, { label: string; value: string }[]> = {
  // Backend aceita: normal, pastosa, liquida, mole
  oral: [
    { label: 'Normal', value: 'normal' },
    { label: 'Pastosa', value: 'pastosa' },
    { label: 'Líquida', value: 'liquida' },
    { label: 'Mole', value: 'mole' },
  ],
  // Consistência não é usada em enteral/parenteral/mista, mas mantemos para UI
  enteral: [
    { label: 'Líquida', value: 'liquida' },
    { label: 'Semi-líquida', value: 'semi-liquida' },
  ],
  parenteral: [{ label: 'IV', value: 'iv' }],
  mista: [{ label: 'Combinada', value: 'combinada' }],
};

interface Props { onSuccess: () => void; }

export const PatientForm: React.FC<Props> = ({ onSuccess }) => {
  const { refreshPatients } = useApp();
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    nome: '',
    quarto: '',
    leito: 'A',
    setor_id: '',
    data_nascimento: '',
    sexo: 'M' as 'M' | 'F',
    peso_atual: '',
    altura: '',
    diagnostico: '',
    observacoes: '',
    alergias: [] as string[],
    restricoes_alimentares: [] as string[],
    // dieta inicial
    dietTipo: 'oral' as 'oral' | 'enteral' | 'parenteral' | 'mista',
    dietDescricao: 'Dieta Geral',
    dietConsistencia: 'normal',
    dietCalorias: '2000',
        dietObs: '',
    // enteral
    enteralViaInfusao: 'nasogástrica',
    enteralVelocidade: '60',
    enteralQtdGramas: '300',
    enteralPorcoes: '5',
    enteralTipoEquipo: 'bomba',
    // parenteral
    parenteralTipoAcesso: 'central',
    parenteralVolume: '2000',
    parenteralComposicao: COMPOSICOES_PADRAO[0],
    parenteralVelocidade: '83',
    // mista (oral + enteral)
    mistaPercOral: '70',
    mistaPercEnteral: '30',
    mistaTextura: 'normal',
    mistaNumeroRefeicoes: '5',
    mistaViaInfusao: 'nasogástrica',
    mistaVelocidade: '60',
    mistaQtdGramas: '300',
    mistaPorcoes: '5',
    mistaTipoEquipo: 'bomba',
  });

  const [newAlergia, setNewAlergia]     = useState('');
  const [newRestricao, setNewRestricao] = useState('');

  const set = (k: keyof typeof form, v: string) =>
    setForm(f => ({ ...f, [k]: v }));

  const addTag = (field: 'alergias' | 'restricoes_alimentares', val: string, clear: () => void) => {
    const v = val.trim();
    if (v && !(form[field] as string[]).includes(v)) {
      setForm(f => ({ ...f, [field]: [...(f[field] as string[]), v] }));
      clear();
    }
  };
  const rmTag = (field: 'alergias' | 'restricoes_alimentares', val: string) =>
    setForm(f => ({ ...f, [field]: (f[field] as string[]).filter(x => x !== val) }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.nome.trim() || !form.quarto.trim() || !form.setor_id) {
      toast.error('Preencha nome, quarto e setor.');
      return;
    }
    if (form.quarto.trim() && isNaN(parseInt(form.quarto.trim(), 10))) {
      toast.error('Quarto deve ser um número inteiro.');
      return;
    }
    if (form.quarto.trim() && parseInt(form.quarto.trim(), 10) <= 0) {
      toast.error('Quarto deve ser um número inteiro positivo.');
      return;
    }
    if (form.peso_atual && parseFloat(form.peso_atual) <= 0) {
      toast.error('Peso deve ser maior que zero.');
      return;
    }
    if (form.altura && parseFloat(form.altura) <= 0) {
      toast.error('Altura deve ser maior que zero.');
      return;
    }
    if (form.leito && !['A','B','C','D'].includes(form.leito)) {
      toast.error('Leito inválido.');
      return;
    }
    if (form.dietTipo === 'mista') {
      const total = (parseFloat(form.mistaPercOral) || 0) + (parseFloat(form.mistaPercEnteral) || 0);
      if (total < 95 || total > 105) {
        toast.error(`A soma dos percentuais deve ser 100% (atual: ${total.toFixed(0)}%).`);
        return;
      }
    }

    if (form.data_nascimento) {
      const nascimento = new Date(form.data_nascimento);
      const hoje       = new Date();
      hoje.setHours(0, 0, 0, 0);
      const anoMinimo  = new Date('1900-01-01');

      if (nascimento >= hoje) {
        toast.error('Data de nascimento não pode ser hoje ou no futuro.');
        return;
      }
      if (nascimento < anoMinimo) {
        toast.error('Data de nascimento inválida (anterior a 1900).');
        return;
      }
    }
    setSaving(true);
    try {
      const patient = await apiCreatePatient({
        nome: form.nome.trim(),
        quarto: parseInt(form.quarto.trim(), 10) || undefined,
        leito: form.leito,
        setor_id: form.setor_id,
        data_nascimento: form.data_nascimento || undefined,
        sexo: form.sexo,
        peso_atual: form.peso_atual ? parseFloat(form.peso_atual) : undefined,
        altura: form.altura ? parseFloat(form.altura) : undefined,
        diagnostico: form.diagnostico || '',
        observacoes: form.observacoes || '',
        alergias: form.alergias,
        restricoes_alimentares: form.restricoes_alimentares,
        ativo: true,
        data_internacao: new Date().toISOString().split('T')[0],
      });

      // Criar prescrição inicial com a dieta preenchida no formulário
      try {
        let dados_dieta: Record<string, any> = {
          descricao: form.dietDescricao,
          usuario_responsavel: 'sistema',
          observacoes: form.dietObs || '',
          restricoes: [],
          suplementos: [],
        };

                if (form.dietTipo === 'oral') {
          dados_dieta.textura          = form.dietConsistencia;
          dados_dieta.numero_refeicoes = 5;
          dados_dieta.tipo_refeicao    = 'desjejum';
        } else if (form.dietTipo === 'enteral') {
          dados_dieta.via_infusao                     = form.enteralViaInfusao;
          dados_dieta.velocidade_ml_h                 = parseFloat(form.enteralVelocidade) || 60;
          dados_dieta['quantidade_gramas_por_porção']  = parseFloat(form.enteralQtdGramas) || 300;
          dados_dieta.porcoes_diarias                 = parseInt(form.enteralPorcoes, 10) || 5;
          dados_dieta.tipo_equipo                     = form.enteralTipoEquipo;
        } else if (form.dietTipo === 'parenteral') {
          dados_dieta.tipo_acesso     = form.parenteralTipoAcesso;
          dados_dieta.volume_ml_dia   = parseFloat(form.parenteralVolume) || 2000;
          dados_dieta.composicao      = form.parenteralComposicao;
          dados_dieta.velocidade_ml_h = parseFloat(form.parenteralVelocidade) || 83;
        } else if (form.dietTipo === 'mista') {
          const percOral = parseFloat(form.mistaPercOral) || 0;
          const percEnteral = parseFloat(form.mistaPercEnteral) || 0;
          dados_dieta.componentes_raw = [
            {
              tipo: 'oral',
              percentual: percOral,
              textura: form.mistaTextura,
              numero_refeicoes: parseInt(form.mistaNumeroRefeicoes, 10) || 5,
              tipo_refeicao: 'desjejum',
            },
            {
              tipo: 'enteral',
              percentual: percEnteral,
              via_infusao: form.mistaViaInfusao,
              velocidade_ml_h: parseFloat(form.mistaVelocidade) || 60,
              'quantidade_gramas_por_porção': parseFloat(form.mistaQtdGramas) || 300,
              porcoes_diarias: parseInt(form.mistaPorcoes, 10) || 5,
              tipo_equipo: form.mistaTipoEquipo,
            },
          ];
        }

        await apiCreatePrescription(patient.id, {
          tipo_dieta: form.dietTipo,
          dados_dieta,
        });
      } catch {
        // Paciente criado com sucesso mesmo se a prescrição inicial falhar
        toast.warning('Paciente cadastrado, mas a dieta inicial não pôde ser criada. Adicione manualmente.');
      }

      await refreshPatients();
      toast.success('Paciente cadastrado com sucesso!');
      onSuccess();
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? 'Erro ao cadastrar paciente.';
      toast.error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={onSuccess}>
          <ArrowLeft className="w-4 h-4 mr-1" />Voltar
        </Button>
        <div>
          <h1>Cadastro de Paciente</h1>
          <p className="text-sm text-muted-foreground">Registre um novo paciente no sistema</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* ── Informações pessoais ── */}
          <Card>
            <CardHeader><CardTitle>Informações Pessoais</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <Field label="Nome Completo *">
                <Input value={form.nome} onChange={e => set('nome', e.target.value)}
                  placeholder="Nome completo do paciente" required />
              </Field>

              <div className="grid grid-cols-3 gap-2">
                <Field label="Quarto *">
                  <Input value={form.quarto} onChange={e => set('quarto', e.target.value)}
                    placeholder="101" required />
                </Field>
                <Field label="Leito">
                  <Select value={form.leito} onValueChange={v => set('leito', v)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {['A','B','C','D'].map(l => <SelectItem key={l} value={l}>{l}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </Field>
                <Field label="Sexo">
                  <Select value={form.sexo} onValueChange={v => set('sexo', v)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="M">Masculino</SelectItem>
                      <SelectItem value="F">Feminino</SelectItem>
                    </SelectContent>
                  </Select>
                </Field>
              </div>

              <Field label="Setor *">
                <Select value={form.setor_id} onValueChange={v => set('setor_id', v)}>
                  <SelectTrigger><SelectValue placeholder="Selecione o setor" /></SelectTrigger>
                  <SelectContent>
                    {SECTORS.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                  </SelectContent>
                </Select>
              </Field>

              <Field label="Data de Nascimento">
                <Input type="date" value={form.data_nascimento}
                  max={new Date(Date.now() - 86400000).toISOString().split('T')[0]}
                  min="1900-01-01"
                  onChange={e => set('data_nascimento', e.target.value)} />
              </Field>

              <div className="grid grid-cols-2 gap-3">
                <Field label="Peso (kg)">
                  <Input type="number" value={form.peso_atual}
                    onChange={e => set('peso_atual', e.target.value)}
                    placeholder="70" min="1" max="300" step="0.1" />
                </Field>
                <Field label="Altura (cm)">
                  <Input type="number" value={form.altura}
                    onChange={e => set('altura', e.target.value)}
                    placeholder="170" min="50" max="250" />
                </Field>
              </div>

              <Field label="Diagnóstico">
                <Input value={form.diagnostico} onChange={e => set('diagnostico', e.target.value)}
                  placeholder="Ex: Diabetes Tipo 2, AVC..." />
              </Field>
            </CardContent>
          </Card>

          {/* ── Condições e restrições ── */}
          <Card>
            <CardHeader><CardTitle>Condições Médicas</CardTitle></CardHeader>
            <CardContent className="space-y-5">
              <div>
                <Label>Alergias Alimentares</Label>
                <div className="flex gap-2 mt-2">
                  <Input value={newAlergia} onChange={e => setNewAlergia(e.target.value)}
                    placeholder="Ex: Camarão, Amendoim"
                    onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTag('alergias', newAlergia, () => setNewAlergia('')); }}} />
                  <Button type="button" size="sm" onClick={() => addTag('alergias', newAlergia, () => setNewAlergia(''))}>
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
                {form.alergias.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {form.alergias.map((a, i) => (
                      <Badge key={i} variant="destructive" className="flex items-center gap-1">
                        {a}
                        <button type="button" onClick={() => rmTag('alergias', a)}>
                          <X className="w-3 h-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <Label>Restrições Alimentares</Label>
                <div className="flex gap-2 mt-2">
                  <Input value={newRestricao} onChange={e => setNewRestricao(e.target.value)}
                    placeholder="Ex: Lactose, Glúten"
                    onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTag('restricoes_alimentares', newRestricao, () => setNewRestricao('')); }}} />
                  <Button type="button" size="sm" onClick={() => addTag('restricoes_alimentares', newRestricao, () => setNewRestricao(''))}>
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
                {form.restricoes_alimentares.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {form.restricoes_alimentares.map((r, i) => (
                      <Badge key={i} variant="outline" className="flex items-center gap-1">
                        {r}
                        <button type="button" onClick={() => rmTag('restricoes_alimentares', r)}>
                          <X className="w-3 h-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              <Field label="Observações Gerais">
                <Textarea value={form.observacoes} onChange={e => set('observacoes', e.target.value)}
                  placeholder="Informações adicionais relevantes..." rows={4} />
              </Field>
            </CardContent>
          </Card>
        </div>

        {/* ── Dieta inicial ── */}
        <Card>
          <CardHeader><CardTitle>Dieta Inicial</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Field label="Tipo">
                <Select value={form.dietTipo} onValueChange={v => setForm(f => ({ ...f, dietTipo: v as 'oral' | 'enteral' | 'parenteral' | 'mista', dietConsistencia: CONSISTENCY[v][0].value }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="oral">Oral</SelectItem>
                    <SelectItem value="enteral">Enteral</SelectItem>
                    <SelectItem value="parenteral">Parenteral</SelectItem>
                    <SelectItem value="mista">Mista</SelectItem>
                  </SelectContent>
                </Select>
              </Field>
              <Field label="Descrição">
                <Select value={form.dietDescricao} onValueChange={v => set('dietDescricao', v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {DIET_TYPES.map(d => <SelectItem key={d} value={d}>{d}</SelectItem>)}
                  </SelectContent>
                </Select>
              </Field>
              {form.dietTipo === 'oral' && (
                <Field label="Consistência">
                  <Select value={form.dietConsistencia} onValueChange={v => set('dietConsistencia', v)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {CONSISTENCY.oral.map(c => (
                        <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </Field>
              )}
              <Field label="Calorias (kcal/dia)">
                <Input type="number" value={form.dietCalorias}
                  onChange={e => set('dietCalorias', e.target.value)} min="800" max="4000" />
              </Field>
            </div>

            {form.dietTipo === 'enteral' && (
              <div className="mt-4 grid grid-cols-1 md:grid-cols-5 gap-4">
                <Field label="Via de Infusão">
                  <Select value={form.enteralViaInfusao} onValueChange={v => set('enteralViaInfusao', v)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {VIAS_INFUSAO.map(v => <SelectItem key={v} value={v}>{v}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </Field>
                <Field label="Velocidade (ml/h)">
                  <Input type="number" value={form.enteralVelocidade}
                    onChange={e => set('enteralVelocidade', e.target.value)} min="1" />
                </Field>
                <Field label="Qtd. por Porção (g)">
                  <Input type="number" value={form.enteralQtdGramas}
                    onChange={e => set('enteralQtdGramas', e.target.value)} min="1" />
                </Field>
                <Field label="Porções/dia">
                  <Input type="number" value={form.enteralPorcoes}
                    onChange={e => set('enteralPorcoes', e.target.value)} min="1" />
                </Field>
                <Field label="Tipo de Equipo">
                  <Select value={form.enteralTipoEquipo} onValueChange={v => set('enteralTipoEquipo', v)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {TIPOS_EQUIPO.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </Field>
              </div>
            )}

            {form.dietTipo === 'parenteral' && (
              <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
                <Field label="Tipo de Acesso">
                  <Select value={form.parenteralTipoAcesso} onValueChange={v => set('parenteralTipoAcesso', v)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {TIPOS_ACESSO.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </Field>
                <Field label="Volume (ml/dia)">
                  <Input type="number" value={form.parenteralVolume}
                    onChange={e => set('parenteralVolume', e.target.value)} min="1" />
                </Field>
                <Field label="Composição">
                  <Select value={form.parenteralComposicao} onValueChange={v => set('parenteralComposicao', v)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {COMPOSICOES_PADRAO.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </Field>
                <Field label="Velocidade (ml/h)">
                  <Input type="number" value={form.parenteralVelocidade}
                    onChange={e => set('parenteralVelocidade', e.target.value)} min="1" />
                </Field>
              </div>
            )}

            {form.dietTipo === 'mista' && (
              <div className="mt-4 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Field label="Percentual Oral (%)">
                    <Input type="number" value={form.mistaPercOral}
                      onChange={e => set('mistaPercOral', e.target.value)} min="0" max="100" />
                  </Field>
                  <Field label="Percentual Enteral (%)">
                    <Input type="number" value={form.mistaPercEnteral}
                      onChange={e => set('mistaPercEnteral', e.target.value)} min="0" max="100" />
                  </Field>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Field label="Consistência (Oral)">
                    <Select value={form.mistaTextura} onValueChange={v => set('mistaTextura', v)}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {CONSISTENCY.oral.map(c => (
                          <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </Field>
                  <Field label="Refeições/dia (Oral)">
                    <Input type="number" value={form.mistaNumeroRefeicoes}
                      onChange={e => set('mistaNumeroRefeicoes', e.target.value)} min="1" />
                  </Field>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <Field label="Via de Infusão (Enteral)">
                    <Select value={form.mistaViaInfusao} onValueChange={v => set('mistaViaInfusao', v)}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {VIAS_INFUSAO.map(v => <SelectItem key={v} value={v}>{v}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </Field>
                  <Field label="Velocidade (ml/h)">
                    <Input type="number" value={form.mistaVelocidade}
                      onChange={e => set('mistaVelocidade', e.target.value)} min="1" />
                  </Field>
                  <Field label="Qtd. por Porção (g)">
                    <Input type="number" value={form.mistaQtdGramas}
                      onChange={e => set('mistaQtdGramas', e.target.value)} min="1" />
                  </Field>
                  <Field label="Porções/dia">
                    <Input type="number" value={form.mistaPorcoes}
                      onChange={e => set('mistaPorcoes', e.target.value)} min="1" />
                  </Field>
                  <Field label="Tipo de Equipo">
                    <Select value={form.mistaTipoEquipo} onValueChange={v => set('mistaTipoEquipo', v)}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {TIPOS_EQUIPO.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </Field>
                </div>
              </div>
            )}
            <div className="mt-4">
              <Field label="Observações da Dieta">
                <Textarea value={form.dietObs} onChange={e => set('dietObs', e.target.value)}
                  placeholder="Instruções especiais sobre a dieta..." rows={2} />
              </Field>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={onSuccess}>Cancelar</Button>
          <Button type="submit" disabled={saving} className="bg-blue-600 hover:bg-blue-700">
            {saving
              ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Salvando...</>
              : <><Save className="w-4 h-4 mr-2" />Cadastrar Paciente</>}
          </Button>
        </div>
      </form>
    </div>
  );
};

const Field: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div className="space-y-1.5">
    <Label>{label}</Label>
    {children}
  </div>
);








