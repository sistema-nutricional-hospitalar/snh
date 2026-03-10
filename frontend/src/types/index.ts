// ─── Auth ───────────────────────────────────────────────────────────────────
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// ─── User ────────────────────────────────────────────────────────────────────
export type UserRole = 'admin' | 'nutricionista' | 'copeiro';

export interface User {
  id: string;
  nome: string;
  email: string;
  tipo: UserRole;
  setor?: string | null;
  crn?: string | null;
  turno?: string | null;
  ativo: boolean;
}

// ─── Setor ───────────────────────────────────────────────────────────────────
export interface Setor {
  id: string;
  nome: string;
  andar: string;
  responsavel: string;
}

// ─── Patient ─────────────────────────────────────────────────────────────────
export interface Patient {
  id: string;
  nome: string;
  data_nascimento: string;
  sexo: 'M' | 'F';
  quarto: string;
  leito: string;
  setor_id: string;
  setor_nome?: string;
  data_internacao: string;
  diagnostico: string;
  alergias: string[];
  peso_atual?: number | null;
  altura?: number | null;
  restricoes_alimentares: string[];
  observacoes?: string | null;
  ativo: boolean;
}

// ─── Prescription ─────────────────────────────────────────────────────────────
export interface Prescricao {
  id: string;
  paciente_id: string;
  paciente_nome?: string;
  nutricionista_id: string;
  nutricionista_nome?: string;
  dieta_atual: DietaInfo;
  status: 'ativa' | 'encerrada' | 'suspensa';
  data_inicio: string;
  data_fim?: string | null;
  historico: HistoricoItem[];
  observacoes?: string | null;
}

export interface DietaInfo {
  tipo: string;
  descricao: string;
  calorias?: number | null;
  restricoes: string[];
  suplementos: string[];
  consistencia?: string | null;
  observacoes?: string | null;
}

export interface HistoricoItem {
  data: string;
  dieta_anterior: string;
  dieta_nova: string;
  motivo: string;
  alterado_por: string;
}

// ─── Notification ────────────────────────────────────────────────────────────
export interface Notificacao {
  id: string;
  titulo: string;
  mensagem: string;
  tipo: 'alteracao_dieta' | 'novo_paciente' | 'urgente' | 'sistema';
  prioridade: 'baixa' | 'media' | 'alta' | 'urgente';
  setor_id?: string | null;
  lida: boolean;
  criada_em: string;
}

// ─── UI helpers ───────────────────────────────────────────────────────────────
export type PriorityLevel = 'baixa' | 'media' | 'alta' | 'urgente';

// Figma mock types (kept for compatibility)
export interface Diet {
  id: string;
  type: 'oral' | 'enteral' | 'parenteral' | 'mista';
  description: string;
  consistency: string;
  restrictions: string[];
  supplements: string[];
  calories: number;
  prescribedBy: string;
  prescribedAt: string;
  observations: string;
}
