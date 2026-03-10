import React, { useState } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { useApp } from '../contexts/AppContext';
import { PatientList } from './PatientList';
import { PatientDetails } from './PatientDetails';
import { NotificationCenter } from './NotificationCenter';
import { PatientForm } from './PatientForm';
import { TouchDisplay } from './TouchDisplay';
import { ReportsScreen } from './ReportsScreen';
import { AdminUsers } from './AdminUsers';
import { Patient } from '../types';
import {
  LayoutDashboard, Users, UserPlus, Bell, FileText,
  Monitor, Settings, LogOut, Menu, X, Heart,
  ChevronRight,
} from 'lucide-react';

// ─── Screen types ─────────────────────────────────────────────────────────────
type Screen =
  | 'dashboard'
  | 'patients'
  | 'patient-detail'
  | 'add-patient'
  | 'notifications'
  | 'reports'
  | 'touch-display'
  | 'admin-users'
  | 'diet-prescription'
  | 'diet-history';

interface NavItem {
  id: Screen;
  label: string;
  icon: React.ElementType;
  roles: string[];
  badge?: number;
}

// ─── Role-based dashboard home cards ─────────────────────────────────────────
const DashboardHome: React.FC<{ onNavigate: (s: Screen) => void }> = ({ onNavigate }) => {
  // refreshPatients extraído do contexto para uso em ações de atualização
  const { currentUser, patients, unreadCount } = useApp();
  const role = currentUser?.tipo;

  const stats = [
    {
      label: 'Pacientes',
      value: patients.length,
      sub: 'cadastrados',
      icon: Users,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      show: ['admin', 'nutricionista', 'medico', 'enfermeiro'],
    },
    {
      label: 'Notificações',
      value: unreadCount,
      sub: 'não lidas',
      icon: Bell,
      color: 'text-amber-600',
      bg: 'bg-amber-50',
      show: ['admin', 'nutricionista', 'copeiro', 'medico', 'enfermeiro'],
    },
  ].filter((s) => s.show.includes(role ?? ''));

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1>Bem-vindo, {currentUser?.nome?.split(' ')[0]}</h1>
        <p className="text-muted-foreground text-sm mt-1">
          {new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="bg-white rounded-xl border p-5 flex items-center gap-4">
              <div className={`w-12 h-12 rounded-xl ${stat.bg} flex items-center justify-center flex-shrink-0`}>
                <Icon className={`w-5 h-5 ${stat.color}`} />
              </div>
              <div>
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
                <div className="text-xs text-muted-foreground">{stat.sub}</div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-white rounded-xl border p-5">
        <h3 className="font-semibold mb-4">Ações rápidas</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {role === 'nutricionista' && (
            <>
              <QuickAction icon={Users}    label="Ver pacientes"        onClick={() => onNavigate('patients')} />
              <QuickAction icon={UserPlus} label="Cadastrar paciente"    onClick={() => onNavigate('add-patient')} />
              <QuickAction icon={Bell}     label="Notificações"          onClick={() => onNavigate('notifications')} badge={unreadCount} />
              <QuickAction icon={FileText} label="Relatórios"            onClick={() => onNavigate('reports')} />
            </>
          )}
          {role === 'copeiro' && (
            <>
              <QuickAction icon={Monitor}  label="Painel de dietas"      onClick={() => onNavigate('touch-display')} />
              <QuickAction icon={Bell}     label="Notificações"          onClick={() => onNavigate('notifications')} badge={unreadCount} />
            </>
          )}
          {role === 'medico' && (
            <>
              <QuickAction icon={Users}    label="Ver pacientes"         onClick={() => onNavigate('patients')} />
              <QuickAction icon={Monitor}  label="Painel de dietas"      onClick={() => onNavigate('touch-display')} />
              <QuickAction icon={Bell}     label="Notificações"          onClick={() => onNavigate('notifications')} badge={unreadCount} />
            </>
          )}
          {role === 'enfermeiro' && (
            <>
              <QuickAction icon={Users}    label="Ver pacientes"         onClick={() => onNavigate('patients')} />
              <QuickAction icon={Monitor}  label="Painel de dietas"      onClick={() => onNavigate('touch-display')} />
              <QuickAction icon={Bell}     label="Notificações"          onClick={() => onNavigate('notifications')} badge={unreadCount} />
            </>
          )}
          {role === 'admin' && (
            <>
              <QuickAction icon={Users}    label="Pacientes"             onClick={() => onNavigate('patients')} />
              <QuickAction icon={Settings} label="Gerenciar usuários"    onClick={() => onNavigate('admin-users')} />
              <QuickAction icon={FileText} label="Relatórios"            onClick={() => onNavigate('reports')} />
              <QuickAction icon={Bell}     label="Notificações"          onClick={() => onNavigate('notifications')} badge={unreadCount} />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

const QuickAction: React.FC<{
  icon: React.ElementType; label: string; onClick: () => void; badge?: number;
}> = ({ icon: Icon, label, onClick, badge }) => (
  <Button
    variant="outline"
    className="justify-between h-auto py-3 px-4 font-normal"
    onClick={onClick}
  >
    <div className="flex items-center gap-2">
      <Icon className="w-4 h-4 text-muted-foreground" />
      <span>{label}</span>
    </div>
    <div className="flex items-center gap-2">
      {badge !== undefined && badge > 0 && (
        <Badge variant="destructive" className="text-xs">{badge}</Badge>
      )}
      <ChevronRight className="w-4 h-4 text-muted-foreground" />
    </div>
  </Button>
);

// ─── Main Dashboard ───────────────────────────────────────────────────────────
export const Dashboard: React.FC = () => {
  // Adicionado refreshPatients aqui para resolver o erro de referência
  const { currentUser, logout, unreadCount, refreshPatients } = useApp();
  const [activeScreen, setActiveScreen] = useState<Screen>('dashboard');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const role = currentUser?.tipo ?? '';

  // Adicionado o casting 'as Screen' para garantir compatibilidade de tipos
  const navItems: NavItem[] = [
    {
      id: 'dashboard' as Screen, label: 'Dashboard', icon: LayoutDashboard,
      roles: ['admin', 'nutricionista', 'copeiro'],
    },
    {
      id: 'patients' as Screen, label: 'Pacientes', icon: Users,
      roles: ['admin', 'nutricionista', 'medico', 'enfermeiro'],
    },
    {
      id: 'add-patient' as Screen, label: 'Novo Paciente', icon: UserPlus,
      roles: ['nutricionista', 'admin'],
    },
    {
      id: 'touch-display' as Screen, label: 'Painel de Dietas', icon: Monitor,
      roles: ['copeiro', 'nutricionista', 'medico', 'enfermeiro'],
    },
    {
      id: 'notifications' as Screen, label: 'Notificações', icon: Bell,
      roles: ['admin', 'nutricionista', 'copeiro', 'medico', 'enfermeiro'],
      badge: unreadCount,
    },
    {
      id: 'reports' as Screen, label: 'Relatórios', icon: FileText,
      roles: ['admin', 'nutricionista'],
    },
    {
      id: 'admin-users' as Screen, label: 'Usuários', icon: Settings,
      roles: ['admin'],
    },
  ].filter((item) => item.roles.includes(role));

  const navigate = (s: Screen) => {
    setActiveScreen(s);
    setSidebarOpen(false);
    if (s !== 'patient-detail') setSelectedPatient(null);
  };

  // Hash-based navigation (e.g. #/touch-display?patient_id=...)
  React.useEffect(() => {
    const applyHash = () => {
      const hash = window.location.hash.replace(/^#\/?/, '');
      if (!hash) return;
      const [path] = hash.split('?', 1);
      if (path === 'touch-display') navigate('touch-display');
      if (path === 'notifications') navigate('notifications');
      if (path === 'patients') navigate('patients');
    };
    const handleNavigate = (e: Event) => {
      const detail = (e as CustomEvent).detail ?? {};
      if (detail.screen) navigate(detail.screen as Screen);
    };
    applyHash();
    window.addEventListener('hashchange', applyHash);
    window.addEventListener('snh:navigate', handleNavigate as EventListener);
    return () => window.removeEventListener('hashchange', applyHash);
  }, []);

  const handleSelectPatient = (p: Patient) => {
    setSelectedPatient(p);
    setActiveScreen('patient-detail');
    setSidebarOpen(false);
  };

  const renderContent = () => {
    switch (activeScreen) {
      case 'dashboard':
        return <DashboardHome onNavigate={navigate} />;
      case 'patients':
        return <PatientList onSelectPatient={handleSelectPatient} />;
      case 'patient-detail':
        return selectedPatient ? (
          <PatientDetails
            patient={selectedPatient}
            onBack={() => navigate('patients')}
            onDelete={async () => { 
              if (refreshPatients) await refreshPatients(); 
              navigate('patients'); 
            }}
          />
        ) : null;
      case 'add-patient':
        return <PatientForm onSuccess={() => navigate('patients')} />;
      case 'touch-display':
        return <TouchDisplay />;
      case 'notifications':
        return <NotificationCenter />;
      case 'reports':
        return <ReportsScreen />;
      case 'admin-users':
        return <AdminUsers />;
      default:
        return null;
    }
  };

  const roleLabel: Record<string, string> = {
    nutricionista: 'Nutricionista',
    copeiro: 'Copeiro',
    admin: 'Administrador',
    medico: 'Médico',
    enfermeiro: 'Enfermeiro',
  };

  const roleBadgeColor: Record<string, string> = {
    nutricionista: 'bg-emerald-100 text-emerald-800',
    copeiro:       'bg-amber-100 text-amber-800',
    admin:         'bg-blue-100 text-blue-800',
    medico:        'bg-indigo-100 text-indigo-800',
    enfermeiro:    'bg-teal-100 text-teal-800',
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 w-64 bg-white border-r flex flex-col
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:inset-0
        `}
      >
        <div className="flex items-center justify-between h-16 px-5 border-b">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Heart className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-sm text-gray-900">SNH</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="px-5 py-3 border-b">
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${roleBadgeColor[role] ?? 'bg-gray-100 text-gray-700'}`}>
            {roleLabel[role] ?? role}
          </span>
        </div>

        <nav className="flex-1 py-4 px-3 overflow-y-auto">
          <div className="space-y-0.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeScreen === item.id ||
                (item.id === 'patients' && activeScreen === 'patient-detail');
              return (
                <Button
                  key={item.id}
                  variant={isActive ? 'secondary' : 'ghost'}
                  className={`w-full justify-start h-9 text-sm font-normal ${
                    isActive ? 'font-medium' : ''
                  }`}
                  onClick={() => navigate(item.id)}
                >
                  <Icon className="w-4 h-4 mr-2.5 flex-shrink-0" />
                  <span className="flex-1 text-left">{item.label}</span>
                  {item.badge !== undefined && item.badge > 0 && (
                    <Badge variant="destructive" className="ml-auto text-xs h-5 px-1.5">
                      {item.badge}
                    </Badge>
                  )}
                </Button>
              );
            })}
          </div>
        </nav>

        <div className="p-3 border-t">
          <div className="flex items-center gap-3 mb-2.5 px-2">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-white text-xs font-semibold">
                {currentUser?.nome?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{currentUser?.nome}</p>
              <p className="text-xs text-muted-foreground truncate">{currentUser?.email}</p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="w-full h-8 text-xs"
            onClick={logout}
          >
            <LogOut className="w-3.5 h-3.5 mr-1.5" />
            Sair
          </Button>
        </div>
      </aside>

      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b flex items-center justify-between px-4 lg:px-6 sticky top-0 z-30">
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="w-5 h-5" />
          </Button>

          <div className="hidden lg:flex items-center gap-1.5 text-sm text-muted-foreground">
            <span>SNH</span>
            <ChevronRight className="w-3.5 h-3.5" />
            <span className="text-foreground font-medium">
              {navItems.find((n) => n.id === activeScreen)?.label ?? 'Dashboard'}
            </span>
          </div>

          <div className="flex items-center gap-1 ml-auto">
            <Button
              variant="ghost"
              size="sm"
              className="relative"
              onClick={() => navigate('notifications')}
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              )}
            </Button>
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};
