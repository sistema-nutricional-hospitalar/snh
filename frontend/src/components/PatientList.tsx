import React, { useState, useMemo, useCallback } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Skeleton } from './ui/skeleton';
import { useApp } from '../contexts/AppContext';
import { Patient } from '../types';
import {
  Search, Edit, AlertTriangle, Clock,
  MapPin, RefreshCw, UserX,
} from 'lucide-react';

interface PatientListProps {
  onSelectPatient?: (patient: Patient) => void;
}

function priorityColor(p: string) {
  const m: Record<string, string> = {
    urgente: 'bg-red-100 text-red-800 border-red-200',
    alta:    'bg-orange-100 text-orange-800 border-orange-200',
    media:   'bg-yellow-100 text-yellow-800 border-yellow-200',
    baixa:   'bg-green-100 text-green-800 border-green-200',
  };
  return m[p] ?? 'bg-gray-100 text-gray-800';
}

export const PatientList: React.FC<PatientListProps> = ({ onSelectPatient }) => {
  const { patients, patientsLoading, refreshPatients } = useApp();
  const [search, setSearch]         = useState('');
  const [sector, setSector]         = useState('all');

  // Setores derivados dinamicamente dos pacientes carregados
  const sectors = useMemo(() => {
    const names = patients.map(p => p.setor_nome).filter(Boolean) as string[];
    return [...new Set(names)].sort();
  }, [patients]);

  const filtered = useMemo(() => {
    return patients.filter((p) => {
      const q = search.toLowerCase();
      const matchSearch =
        (p.nome?.toLowerCase().includes(q)) ||
        (String(p.quarto ?? '').toLowerCase().includes(q)) ||
        (p.id?.includes(q));
      const matchSector = sector === 'all' || p.setor_nome === sector;
      return matchSearch && matchSector;
    });
  }, [patients, search, sector]);

  const handleRefresh = useCallback(() => {
    refreshPatients(sector !== 'all' ? { setor_id: sector } : undefined);
  }, [refreshPatients, sector]);

  if (patientsLoading && patients.length === 0) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <Skeleton className="h-4 w-48 mb-3" />
              <Skeleton className="h-3 w-32 mb-2" />
              <Skeleton className="h-3 w-24" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1>Pacientes</h1>
          <p className="text-muted-foreground text-sm">
            Gerenciamento de pacientes por setor clínico
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-base px-3 py-1">
            {filtered.length} pacientes
          </Badge>
          <Button variant="outline" size="sm" onClick={handleRefresh} disabled={patientsLoading}>
            <RefreshCw className={`w-4 h-4 ${patientsLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Buscar por nome, quarto ou ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 h-9"
              />
            </div>
            <div className="w-full md:w-52">
              <Select value={sector} onValueChange={setSector}>
                <SelectTrigger className="h-9">
                  <SelectValue placeholder="Todos os setores" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os setores</SelectItem>
                  {sectors.map((s) => (
                    <SelectItem key={s} value={s}>{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Patient grid */}
      {filtered.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filtered.map((patient) => (
            <PatientCard
              key={patient.id}
              patient={patient}
              onSelect={onSelectPatient}
            />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-16 text-center">
            <UserX className="w-12 h-12 text-muted-foreground/40 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-900 mb-1">
              {search || sector !== 'all' ? 'Nenhum paciente encontrado' : 'Nenhum paciente cadastrado'}
            </h3>
            <p className="text-sm text-muted-foreground">
              {search || sector !== 'all'
                ? 'Tente ajustar os filtros.'
                : 'Cadastre o primeiro paciente usando o menu lateral.'}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// ─── Patient Card ─────────────────────────────────────────────────────────────
const PatientCard: React.FC<{ patient: Patient; onSelect?: (p: Patient) => void }> = ({
  patient, onSelect,
}) => {
  const admDate = patient.data_internacao
    ? new Date(patient.data_internacao).toLocaleDateString('pt-BR')
    : '—';

  return (
    <Card className="hover:shadow-md transition-all duration-200 border hover:border-blue-200 group">
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0 pr-3">
            <h3 className="font-semibold text-base truncate">{patient.nome}</h3>
            <div className="flex items-center text-sm text-muted-foreground mt-0.5">
              <MapPin className="w-3.5 h-3.5 mr-1 flex-shrink-0" />
              <span className="truncate">
                Quarto {patient.quarto}{patient.leito} · {patient.setor_nome ?? '—'}
              </span>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
            {patient.restricoes_alimentares?.length > 0 && (
              <Badge className="bg-red-100 text-red-800 border-red-200 text-xs">
                RESTRIÇÃO
              </Badge>
            )}
          </div>
        </div>

        {/* Diagnosis */}
        {patient.diagnostico && (
          <div className="mb-3">
            <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Diagnóstico</p>
            <p className="text-sm truncate">{patient.diagnostico}</p>
          </div>
        )}

        {/* Allergies */}
        {patient.alergias?.length > 0 && (
          <div className="mb-3">
            <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Alergias</p>
            <div className="flex flex-wrap gap-1">
              {patient.alergias.slice(0, 3).map((a, i) => (
                <Badge key={i} variant="destructive" className="text-xs py-0">
                  {a}
                </Badge>
              ))}
              {patient.alergias.length > 3 && (
                <Badge variant="outline" className="text-xs py-0">
                  +{patient.alergias.length - 3}
                </Badge>
              )}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between pt-2.5 border-t mt-3">
          <div className="flex items-center text-xs text-muted-foreground">
            <Clock className="w-3 h-3 mr-1" />
            Internado em {admDate}
          </div>
          {onSelect && (
            <Button
              size="sm"
              variant="outline"
              className="h-7 text-xs group-hover:border-blue-300 group-hover:text-blue-700"
              onClick={() => onSelect(patient)}
            >
              <Edit className="w-3 h-3 mr-1" />
              Ver detalhes
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};