import React, { useEffect, useState, useCallback } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { User } from '../types';
import { apiGetUsers, apiCreateUser, apiToggleUserStatus } from '../lib/api';
import { toast } from 'sonner';
import {
  UserPlus, RefreshCw, Shield, CheckCircle, XCircle,
  Loader2, Search, Settings,
} from 'lucide-react';

const ROLE_LABEL: Record<string, string> = {
  admin: 'Administrador',
  nutricionista: 'Nutricionista',
  copeiro: 'Copeiro',
  medico: 'Médico',
  enfermeiro: 'Enfermeiro',
};

const ROLE_COLOR: Record<string, string> = {
  admin:         'bg-blue-100 text-blue-800',
  nutricionista: 'bg-emerald-100 text-emerald-800',
  copeiro:       'bg-amber-100 text-amber-800',
  medico:        'bg-indigo-100 text-indigo-800',
  enfermeiro:    'bg-teal-100 text-teal-800',
};

export const AdminUsers: React.FC = () => {
  const [users,      setUsers]      = useState<User[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [search,     setSearch]     = useState('');
  const [showForm,   setShowForm]   = useState(false);
  const [toggling,   setToggling]   = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setUsers(await apiGetUsers());
    } catch {
      toast.error('Erro ao carregar usuários.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const toggle = async (user: User) => {
    setToggling(user.id);
    try {
      const updated = await apiToggleUserStatus(user.id, !user.ativo);
      setUsers(prev => prev.map(u => u.id === user.id ? updated : u));
      toast.success(`Usuário ${updated.ativo ? 'ativado' : 'bloqueado'} com sucesso.`);
    } catch {
      toast.error('Erro ao alterar status do usuário.');
    } finally {
      setToggling(null);
    }
  };

  const filtered = users.filter(u =>
    u.nome?.toLowerCase().includes(search.toLowerCase()) ||
    u.email?.toLowerCase().includes(search.toLowerCase())
  );

  const stats = {
    total:  users.length,
    ativos: users.filter(u => u.ativo).length,
    bloqueados: users.filter(u => !u.ativo).length,
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1>Gerenciamento de Usuários</h1>
          <p className="text-sm text-muted-foreground">Criar, ativar e bloquear usuários do sistema</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={load} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700" onClick={() => setShowForm(true)}>
            <UserPlus className="w-4 h-4 mr-2" />Novo Usuário
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Total"     value={stats.total}      color="text-blue-600"  bg="bg-blue-50"  icon={<Settings className="w-5 h-5" />} />
        <StatCard label="Ativos"    value={stats.ativos}     color="text-green-600" bg="bg-green-50" icon={<CheckCircle className="w-5 h-5" />} />
        <StatCard label="Bloqueados" value={stats.bloqueados} color="text-red-600"  bg="bg-red-50"   icon={<XCircle className="w-5 h-5" />} />
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
        <Input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Buscar por nome ou email…"
          className="pl-9 h-9"
        />
      </div>

      {/* User list */}
      {loading ? (
        <div className="space-y-3">
          {[1,2,3].map(i => <div key={i} className="h-20 bg-gray-100 rounded-xl animate-pulse" />)}
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(u => (
            <Card key={u.id} className={`border ${!u.ativo ? 'opacity-60' : ''}`}>
              <CardContent className="p-4 flex items-center justify-between gap-4 flex-wrap">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-semibold text-sm">
                      {u.nome?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="min-w-0">
                    <p className="font-medium truncate">{u.nome}</p>
                    <p className="text-sm text-muted-foreground truncate">{u.email}</p>
                    {(u.crn || u.turno || u.setor || u.crm || u.coren || u.especialidade) && (
                      <p className="text-xs text-muted-foreground">
                        {u.crn ?? ''}{u.crm ? ` · CRM: ${u.crm}` : ''}{u.coren ? ` · COREN: ${u.coren}` : ''}{u.especialidade ? ` · ${u.especialidade}` : ''}{u.turno ? ` · Turno: ${u.turno}` : ''}{u.setor ? ` · ${u.setor}` : ''}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  <Badge className={ROLE_COLOR[u.tipo] ?? 'bg-gray-100 text-gray-800'}>
                    <Shield className="w-3 h-3 mr-1" />
                    {ROLE_LABEL[u.tipo] ?? u.tipo}
                  </Badge>
                  <Badge variant={u.ativo ? 'default' : 'destructive'} className={u.ativo ? 'bg-green-100 text-green-800' : ''}>
                    {u.ativo ? 'Ativo' : 'Bloqueado'}
                  </Badge>
                  <Button
                    size="sm" variant="outline"
                    className={`h-8 text-xs ${u.ativo ? 'hover:border-red-300 hover:text-red-700' : 'hover:border-green-300 hover:text-green-700'}`}
                    disabled={toggling === u.id}
                    onClick={() => toggle(u)}
                  >
                    {toggling === u.id
                      ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      : u.ativo ? <><XCircle className="w-3.5 h-3.5 mr-1" />Bloquear</> : <><CheckCircle className="w-3.5 h-3.5 mr-1" />Ativar</>}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}

          {filtered.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center text-muted-foreground text-sm">
                Nenhum usuário encontrado.
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Create user dialog */}
      <CreateUserDialog
        open={showForm}
        onClose={() => setShowForm(false)}
        onCreated={() => { setShowForm(false); load(); }}
      />
    </div>
  );
};

// ── Create user dialog ────────────────────────────────────────────────────────
const CreateUserDialog: React.FC<{ open: boolean; onClose: () => void; onCreated: () => void }> = ({
  open, onClose, onCreated,
}) => {
  const [form, setForm] = useState({
    nome: '', email: '', senha: '', tipo: 'copeiro',
    setor: '', crn: '', turno: '', crm: '', coren: '', especialidade: '',
  });
  const [saving, setSaving] = useState(false);

  const set = (k: keyof typeof form, v: string) => setForm(f => ({ ...f, [k]: v }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiCreateUser({
        nome:  form.nome,
        email: form.email,
        senha: form.senha,
        tipo:  form.tipo === "admin" ? "administrador" : form.tipo as any,
        setor: form.setor || undefined,
        crn:   form.crn   || undefined,
        crm:   form.crm   || undefined,
        coren: form.coren || undefined,
        especialidade: form.especialidade || undefined,
        turno: form.turno || undefined,
        ativo: true,
      });
      toast.success('Usuário criado com sucesso!');
      setForm({ nome: '', email: '', senha: '', tipo: 'copeiro', setor: '', crn: '', turno: '', crm: '', coren: '', especialidade: '' });
      onCreated();
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? 'Erro ao criar usuário.';
      toast.error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <UserPlus className="w-5 h-5" />Novo Usuário
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={submit} className="space-y-4 mt-2">
          <Field label="Nome Completo *">
            <Input value={form.nome} onChange={e => set('nome', e.target.value)} placeholder="Nome completo" required />
          </Field>
          <Field label="Email *">
            <Input type="email" value={form.email} onChange={e => set('email', e.target.value)} placeholder="email@hospital.com" required />
          </Field>
          <Field label="Senha *">
            <Input type="password" value={form.senha} onChange={e => set('senha', e.target.value)} placeholder="••••••••" required minLength={6} />
          </Field>
          <Field label="Perfil *">
            <Select value={form.tipo} onValueChange={v => set('tipo', v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="administrador">Administrador</SelectItem>
                <SelectItem value="nutricionista">Nutricionista</SelectItem>
                <SelectItem value="medico">Médico</SelectItem>
                <SelectItem value="enfermeiro">Enfermeiro</SelectItem>
                <SelectItem value="copeiro">Copeiro</SelectItem>
              </SelectContent>
            </Select>
          </Field>
          {(form.tipo === 'nutricionista') && (
            <Field label="CRN">
              <Input value={form.crn} onChange={e => set('crn', e.target.value)} placeholder="CRN-8/12345" />
            </Field>
          )}
          {form.tipo === 'medico' && (
            <>
              <Field label="CRM">
                <Input value={form.crm} onChange={e => set('crm', e.target.value)} placeholder="CRM-SP 000000" />
              </Field>
              <Field label="Especialidade">
                <Input value={form.especialidade} onChange={e => set('especialidade', e.target.value)} placeholder="Clínico geral" />
              </Field>
            </>
          )}
          {form.tipo === 'enfermeiro' && (
            <>
              <Field label="COREN">
                <Input value={form.coren} onChange={e => set('coren', e.target.value)} placeholder="COREN-SP 000000" />
              </Field>
              <Field label="Setor">
                <Input value={form.setor} onChange={e => set('setor', e.target.value)} placeholder="UTI, Clínica..." />
              </Field>
            </>
          )}
          {form.tipo === 'copeiro' && (
            <Field label="Turno">
              <Select value={form.turno} onValueChange={v => set('turno', v)}>
                <SelectTrigger><SelectValue placeholder="Selecionar turno" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="manha">Manhã</SelectItem>
                  <SelectItem value="tarde">Tarde</SelectItem>
                  <SelectItem value="noite">Noite</SelectItem>
                </SelectContent>
              </Select>
            </Field>
          )}
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={onClose}>Cancelar</Button>
            <Button type="submit" disabled={saving} className="bg-blue-600 hover:bg-blue-700">
              {saving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Criando…</> : 'Criar Usuário'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

const StatCard: React.FC<{ label: string; value: number; color: string; bg: string; icon: React.ReactNode }> = ({
  label, value, color, bg, icon,
}) => (
  <div className={`${bg} rounded-xl p-4 flex items-center gap-3`}>
    <div className={`${color}`}>{icon}</div>
    <div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  </div>
);

const Field: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div className="space-y-1.5">
    <Label>{label}</Label>
    {children}
  </div>
);
