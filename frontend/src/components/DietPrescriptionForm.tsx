import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ArrowLeft, Save, AlertTriangle, Loader2, X } from 'lucide-react';
import { Patient, Prescricao } from '../types';
import { useApp } from '../contexts/AppContext';
import { apiCreatePrescription, apiUpdatePrescription } from '../lib/api';
import { toast } from 'sonner';

const DIET_DESCRIPTIONS = {
  oral: [
    'Dieta Geral', 'Dieta Hipossódica', 'Dieta Hipocalórica',
    'Dieta Diabética', 'Dieta Líquida', 'Dieta Pastosa', 'Dieta Mole',
  ],
  enteral: [
    'Dieta Enteral Padrão', 'Dieta Enteral Hipercalórica',
    'Dieta Enteral Hiperproteica', 'Dieta Enteral Normocalórica', 'Dieta Enteral com Fibras',
  ],
};

const CONSISTENCY_OPTIONS = {
  oral:    ['Normal', 'Pastosa', 'Líquida', 'Branda'],
  enteral: ['Líquida', 'Semi-líquida'],
};

const VIAS_INFUSAO = ['sng', 'nasogástrica', 'nasoentérica', 'gastrostomia', 'jejunostomia', 'cateter central'];
const TIPOS_EQUIPO = ['bomba', 'gravitacional', 'seringa'];
const COMMON_RESTRICTIONS = ['Sal', 'Açúcar', 'Lactose', 'Glúten', 'Conservantes', 'Corantes', 'Gordura Trans', 'Fritura'];
const COMMON_SUPPLEMENTS  = ['Vitamina D', 'Vitamina B12', 'Complexo B', 'Vitamina C', 'Ferro', 'Cálcio', 'Magnésio', 'Ômega 3'];

interface Props {
  patient: Patient;
  activePrescription?: Prescricao | null;
  onBack: () => void;
  onSuccess: () => void;
}

export const DietPrescriptionForm: React.FC<Props> = ({ patient, activePrescription, onBack, onSuccess }) => {
  const { currentUser, refreshPatients } = useApp();
  const existing = activePrescription?.dieta_atual;
  const tipoInicial = (existing?.tipo === 'enteral' ? 'enteral' : 'oral') as 'oral' | 'enteral';

  const [form, setForm] = useState({
    tipo:                     tipoInicial,
    descricao:                existing?.descricao ?? DIET_DESCRIPTIONS[tipoInicial][0],
    consistencia:             existing?.consistencia ?? CONSISTENCY_OPTIONS[tipoInicial][0],
    calorias:                 String(existing?.calorias ?? '2000'),
    via_infusao:              'sng',
    velocidade_ml_h:          '60',
    quantidade_gramas_porcao: '300',
    porcoes_diarias:          '5',
    tipo_equipo:              'bomba',
    restricoes:               existing?.restricoes  ?? [] as string[],
    suplementos:              existing?.suplementos ?? [] as string[],
    observacoes:              existing?.observacoes ?? '',
    motivo:                   '',
  });

  const [newRestr, setNewRestr] = useState('');
  const [newSupl,  setNewSupl]  = useState('');
  const [saving,   setSaving]   = useState(false);

  const handleTipoChange = (v: 'oral' | 'enteral') => {
    setForm(f => ({ ...f, tipo: v, descricao: DIET_DESCRIPTIONS[v][0], consistencia: CONSISTENCY_OPTIONS[v][0] }));
  };

  const addRestr = (v = newRestr) => { if (v && !form.restricoes.includes(v)) { setForm(f => ({ ...f, restricoes: [...f.restricoes, v] })); setNewRestr(''); } };
  const rmRestr  = (v: string) => setForm(f => ({ ...f, restricoes: f.restricoes.filter(r => r !== v) }));
  const addSupl  = (v = newSupl) => { if (v && !form.suplementos.includes(v)) { setForm(f => ({ ...f, suplementos: [...f.suplementos, v] })); setNewSupl(''); } };
  const rmSupl   = (v: string) => setForm(f => ({ ...f, suplementos: f.suplementos.filter(s => s !== v) }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.motivo.trim()) { toast.error('Informe o motivo da alteração da dieta.'); return; }
    setSaving(true);
    try {
      const dados_dieta: Record<string, any> = {
        descricao:           `${form.descricao} — ${form.motivo}`.trim(),
        usuario_responsavel: currentUser?.nome ?? 'nutricionista',
        restricoes:          form.restricoes,
        suplementos:         form.suplementos,
        observacoes:         form.observacoes,
      };

      if (form.tipo === 'oral') {
        dados_dieta.textura          = form.consistencia.toLowerCase();
        dados_dieta.numero_refeicoes = parseInt(form.porcoes_diarias) || 5;
        dados_dieta.tipo_refeicao    = 'desjejum';
      } else {
        dados_dieta.via_infusao                    = form.via_infusao;
        dados_dieta.velocidade_ml_h                = parseFloat(form.velocidade_ml_h) || 60;
        dados_dieta['quantidade_gramas_por_porção'] = parseFloat(form.quantidade_gramas_porcao) || 300;
        dados_dieta.porcoes_diarias                = parseInt(form.porcoes_diarias) || 5;
        dados_dieta.tipo_equipo                    = form.tipo_equipo;
      }

      const payload = { tipo_dieta: form.tipo, dados_dieta };

      if (activePrescription) {
        await apiUpdatePrescription(activePrescription.id, payload);
      } else {
        await apiCreatePrescription(patient.id, payload);
      }

      await refreshPatients();
      toast.success('Dieta prescrita com sucesso! Notificação enviada para a equipe.');
      onSuccess();
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? 'Erro ao salvar prescrição.';
      toast.error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setSaving(false);
    }
  };

  const selectCls = "bg-white border border-gray-300";
  const inputCls  = "bg-white border border-gray-300";

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

          <Card>
            <CardHeader><CardTitle>Informações da Dieta</CardTitle></CardHeader>
            <CardContent className="space-y-4">

              <div className="space-y-1">
                <Label>Tipo de Dieta</Label>
                <Select value={form.tipo} onValueChange={handleTipoChange}>
                  <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-white">
                    <SelectItem value="oral">Oral</SelectItem>
                    <SelectItem value="enteral">Enteral</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <Label>Descrição da Dieta</Label>
                <Select value={form.descricao} onValueChange={(v) => setForm(f => ({ ...f, descricao: v }))}>
                  <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-white">
                    {DIET_DESCRIPTIONS[form.tipo].map((d) => <SelectItem key={d} value={d}>{d}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>

              {form.tipo === 'oral' && (<>
                <div className="space-y-1">
                  <Label>Consistência</Label>
                  <Select value={form.consistencia} onValueChange={(v) => setForm(f => ({ ...f, consistencia: v }))}>
                    <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-white">
                      {CONSISTENCY_OPTIONS.oral.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Número de Refeições/dia</Label>
                  <Input type="number" value={form.porcoes_diarias} min="1" max="10" className={inputCls}
                    onChange={(e) => setForm(f => ({ ...f, porcoes_diarias: e.target.value }))} />
                </div>
                <div className="space-y-1">
                  <Label>Calorias (kcal/dia)</Label>
                  <Input type="number" value={form.calorias} min="800" max="4000" className={inputCls}
                    onChange={(e) => setForm(f => ({ ...f, calorias: e.target.value }))} />
                </div>
              </>)}

              {form.tipo === 'enteral' && (<>
                <div className="space-y-1">
                  <Label>Via de Infusão</Label>
                  <Select value={form.via_infusao} onValueChange={(v) => setForm(f => ({ ...f, via_infusao: v }))}>
                    <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-white">
                      {VIAS_INFUSAO.map((v) => <SelectItem key={v} value={v}>{v.toUpperCase()}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Velocidade (ml/h)</Label>
                  <Input type="number" value={form.velocidade_ml_h} min="10" max="200" className={inputCls}
                    onChange={(e) => setForm(f => ({ ...f, velocidade_ml_h: e.target.value }))} />
                </div>
                <div className="space-y-1">
                  <Label>Quantidade por Porção (g)</Label>
                  <Input type="number" value={form.quantidade_gramas_porcao} min="50" max="1000" className={inputCls}
                    onChange={(e) => setForm(f => ({ ...f, quantidade_gramas_porcao: e.target.value }))} />
                </div>
                <div className="space-y-1">
                  <Label>Porções/dia</Label>
                  <Input type="number" value={form.porcoes_diarias} min="1" max="10" className={inputCls}
                    onChange={(e) => setForm(f => ({ ...f, porcoes_diarias: e.target.value }))} />
                </div>
                <div className="space-y-1">
                  <Label>Tipo de Equipo</Label>
                  <Select value={form.tipo_equipo} onValueChange={(v) => setForm(f => ({ ...f, tipo_equipo: v }))}>
                    <SelectTrigger className={selectCls}><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-white">
                      {TIPOS_EQUIPO.map((t) => <SelectItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Calorias (kcal/dia)</Label>
                  <Input type="number" value={form.calorias} min="800" max="4000" className={inputCls}
                    onChange={(e) => setForm(f => ({ ...f, calorias: e.target.value }))} />
                </div>
              </>)}

              <div className="space-y-1">
                <Label>Motivo da Alteração *</Label>
                <Textarea value={form.motivo} onChange={(e) => setForm(f => ({ ...f, motivo: e.target.value }))}
                  placeholder="Descreva o motivo da alteração..." rows={3} className={inputCls} required />
              </div>
            </CardContent>
          </Card>

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
                      className={`h-7 text-xs ${form.restricoes.includes(r) ? 'bg-red-50 border-red-200 text-red-700' : 'bg-white'}`}
                      onClick={() => form.restricoes.includes(r) ? rmRestr(r) : addRestr(r)}>{r}</Button>
                  ))}
                </div>
                {form.restricoes.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {form.restricoes.map((r) => (
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
                  <Input value={newSupl} className={inputCls} onChange={(e) => setNewSupl(e.target.value)}
                    placeholder="Digite um suplemento..."
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addSupl(); } }} />
                  <Button type="button" size="sm" onClick={() => addSupl()}>+</Button>
                </div>
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {COMMON_SUPPLEMENTS.map((s) => (
                    <Button key={s} type="button" variant="outline" size="sm"
                      className={`h-7 text-xs ${form.suplementos.includes(s) ? 'bg-green-50 border-green-200 text-green-700' : 'bg-white'}`}
                      onClick={() => form.suplementos.includes(s) ? rmSupl(s) : addSupl(s)}>{s}</Button>
                  ))}
                </div>
                {form.suplementos.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {form.suplementos.map((s) => (
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
            <Textarea value={form.observacoes} onChange={(e) => setForm(f => ({ ...f, observacoes: e.target.value }))}
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