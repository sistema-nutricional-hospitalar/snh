import axios from 'axios';
import { getToken, clearSession } from './auth';
import type {
  LoginRequest, LoginResponse,
  User, Patient, Prescricao, Notificacao,
} from '../types';

const client = axios.create({
  baseURL: '/api',
  timeout: 10_000,
});

// ─── Request interceptor: attach Bearer token ────────────────────────────────
client.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers['Authorization'] = `Bearer ${token}`;
  return config;
});

// ─── Response interceptor: redirect on 401 ───────────────────────────────────
client.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      clearSession();
      window.location.href = '/';
    }
    return Promise.reject(err);
  },
);

// ─── Mapper: backend prescription JSON → frontend Prescricao type ─────────────
// Backend stores: { id, patient_id, setor_id, dieta: { tipo, dados }, ativa, historico }
// Frontend uses:  { id, paciente_id, dieta_atual: { tipo, descricao, ... }, status, historico }
function mapPrescricao(raw: any): Prescricao {
  const dieta = raw.dieta ?? {};
  const dados = dieta.dados ?? {};
  return {
    id:               raw.id,
    paciente_id:      raw.patient_id ?? raw.paciente_id ?? '',
    nutricionista_id: raw.usuario_responsavel ?? '',
    dieta_atual: {
      tipo:        dieta.tipo ?? 'oral',
      descricao:   dados.descricao ?? dados.textura ?? dieta.tipo ?? '',
      calorias:    dados.calorias ?? null,
      consistencia: dados.textura ?? dados.consistencia ?? null,
      restricoes:  dados.restricoes ?? [],
      suplementos: dados.suplementos ?? [],
      observacoes: dados.observacoes ?? null,
    },
    status:      raw.ativa ? 'ativa' : 'encerrada',
    data_inicio: raw.criado_em ?? '',
    data_fim:    raw.encerrado_em ?? null,
    historico:   (raw.historico ?? []).map((h: any) => ({
      data:          h.data_hora ?? '',
      dieta_anterior: h.descricao ?? '',
      dieta_nova:    '',
      motivo:        h.descricao ?? '',
      alterado_por:  h.usuario ?? '',
    })),
    observacoes: dados.observacoes ?? null,
  };
}

// ─── Mapper: backend user JSON → frontend User type ───────────────────────────
// Backend: { id, nome, cpf, email, tipo, status, dados_extras }
// Frontend: { id, nome, email, tipo, ativo, crn, turno, setor }
function mapUser(raw: any): User {
  return {
    id:    raw.id,
    nome:  raw.nome,
    email: raw.email,
    tipo:  raw.tipo === 'administrador' ? 'admin' : raw.tipo,
    ativo: raw.ativo ?? raw.status === 'ativo',
    crn:   raw.dados_extras?.crn   ?? raw.crn   ?? null,
    turno: raw.dados_extras?.turno ?? raw.turno ?? null,
    setor: raw.dados_extras?.setor_trabalho ?? raw.setor ?? null,
  };
}

// ─── Mapper: backend patient JSON → frontend Patient type ─────────────────────
// Backend returns `data_nasc`, frontend type uses `data_nascimento`
function mapPatient(raw: any): Patient {
  return {
    ...raw,
    data_nascimento: raw.data_nascimento ?? raw.data_nasc ?? '',
  } as Patient;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────
export async function apiLogin(data: LoginRequest): Promise<LoginResponse> {
  const res = await client.post<LoginResponse>('/auth/login', {
    email: data.email,
    password: data.password,
  });
  return res.data;
}

export async function apiGetMe(): Promise<User> {
  const res = await client.get<any>('/users/me');
  return mapUser(res.data);
}

// ─── Patients ─────────────────────────────────────────────────────────────────
export async function apiGetPatients(params?: {
  setor_id?: string; busca?: string; ativo?: boolean;
}): Promise<Patient[]> {
  const res = await client.get<any[]>('/patients', { params });
  return res.data.map(mapPatient);
}

export async function apiGetPatient(id: string): Promise<Patient> {
  const res = await client.get<any>(`/patients/${id}`);
  return mapPatient(res.data);
}

export async function apiCreatePatient(data: Partial<Patient>): Promise<Patient> {
  const res = await client.post<any>('/patients', data);
  return mapPatient(res.data);
}

export async function apiUpdatePatient(id: string, data: Partial<Patient>): Promise<Patient> {
  const res = await client.put<any>(`/patients/${id}`, data);
  return mapPatient(res.data);
}

export async function apiDeletePatient(id: string): Promise<void> {
  await client.delete(`/patients/${id}`);
}

// ─── Prescriptions ─────────────────────────────────────────────────────────────
export async function apiGetPrescriptions(): Promise<any[]> {
  const res = await client.get<any[]>('/prescriptions');
  return res.data;
}

export async function apiGetPatientPrescriptions(patientId: string): Promise<Prescricao[]> {
  const res = await client.get<any[]>(`/patients/${patientId}/prescriptions`);
  return res.data.map(mapPrescricao);
}

export async function apiCreatePrescription(
  patientId: string,
  data: { tipo_dieta: string; dados_dieta: Record<string, any> },
): Promise<Prescricao> {
  const res = await client.post<any>(`/patients/${patientId}/prescriptions`, data);
  return mapPrescricao(res.data);
}

export async function apiUpdatePrescription(
  id: string,
  data: { tipo_dieta: string; dados_dieta: Record<string, any> },
): Promise<Prescricao> {
  const res = await client.put<any>(`/prescriptions/${id}`, data);
  return mapPrescricao(res.data);
}

export async function apiEncerrarPrescription(id: string): Promise<any> {
  const res = await client.post(`/prescriptions/${id}/encerrar`);
  return res.data;
}

export async function apiGetPrescriptionHistory(id: string) {
  const res = await client.get(`/prescriptions/${id}/history`);
  return res.data;
}

// ─── Notifications ────────────────────────────────────────────────────────────
export async function apiGetNotifications(): Promise<Notificacao[]> {
  const res = await client.get<Notificacao[]>('/notifications');
  return res.data;
}

export async function apiGetNotificationCount(): Promise<{ total: number; nao_lidas: number }> {
  const res = await client.get('/notifications/count');
  return res.data;
}

export async function apiMarkNotificationRead(id: string): Promise<void> {
  await client.patch(`/notifications/${id}/read`);
}

export async function apiMarkAllNotificationsRead(): Promise<void> {
  await client.patch('/notifications/read-all');
}

// ─── Reports ──────────────────────────────────────────────────────────────────
export async function apiGetDietReport(params?: {
  setor_nome?: string; data_inicio?: string; data_fim?: string;
}) {
  const res = await client.get('/reports/dietas', { params });
  return res.data;
}

export async function apiGetAlteracoesReport(params?: {
  data_inicio?: string; data_fim?: string; setor_nome?: string;
}) {
  const res = await client.get('/reports/alteracoes', { params });
  return res.data;
}

export async function apiGetEvolucaoReport(patientId: string) {
  const res = await client.get(`/reports/evolucao/${patientId}`);
  return res.data;
}

// ─── Users (admin) ────────────────────────────────────────────────────────────
export async function apiGetUsers(): Promise<User[]> {
  const res = await client.get<any[]>('/users');
  return res.data.map(mapUser);
}

export async function apiCreateUser(data: {
  nome: string; email: string; senha: string; tipo: string;
  setor?: string; crn?: string; turno?: string; ativo?: boolean;
}): Promise<User> {
  const res = await client.post<any>('/users', data);
  return mapUser(res.data);
}

// Bug 5 fix: envia { status: 'ativo' | 'bloqueado' } em vez de { ativo: boolean }
export async function apiToggleUserStatus(id: string, ativo: boolean): Promise<User> {
  const res = await client.patch<any>(`/users/${id}/status`, {
    status: ativo ? 'ativo' : 'bloqueado',
  });
  // O endpoint retorna { sucesso, user_id, novo_status } — busca o usuário atualizado
  const userRes = await client.get<any>(`/users/${id}`);
  return mapUser(userRes.data);
}

export default client;
