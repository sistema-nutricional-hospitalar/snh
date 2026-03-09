import React, {
  createContext, useContext, useState,
  useEffect, useCallback, ReactNode,
} from 'react';
import { User, Patient, Notificacao } from '../types';
import { saveSession, clearSession, getToken, getSavedUser } from '../lib/auth';
import { apiLogin, apiGetMe, apiGetPatients, apiGetNotifications, apiMarkNotificationRead, apiMarkAllNotificationsRead } from '../lib/api';

interface AppContextType {
  // Auth
  currentUser: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;

  // Patients
  patients: Patient[];
  patientsLoading: boolean;
  refreshPatients: (params?: { setor_id?: string; busca?: string }) => Promise<void>;

  // Notifications
  notifications: Notificacao[];
  unreadCount: number;
  markRead: (id: string) => Promise<void>;
  markAllRead: () => Promise<void>;
}

const AppContext = createContext<AppContextType | null>(null);

export const useApp = () => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
};

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(getSavedUser());
  const [token, setToken]             = useState<string | null>(getToken());
  const [isLoading, setIsLoading]     = useState(false);

  const [patients, setPatients]               = useState<Patient[]>([]);
  const [patientsLoading, setPatientsLoading] = useState(false);

  const [notifications, setNotifications] = useState<Notificacao[]>([]);

  // ─── Login ────────────────────────────────────────────────────────────────
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const { access_token } = await apiLogin({ email, password });
      setToken(access_token);
      // Temporarily save token so apiGetMe can read it
      localStorage.setItem('snh_token', access_token);
      const me = await apiGetMe();
      saveSession(access_token, me);
      setCurrentUser(me);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = useCallback(() => {
    clearSession();
    setCurrentUser(null);
    setToken(null);
    setPatients([]);
    setNotifications([]);
  }, []);

  // ─── Patients ─────────────────────────────────────────────────────────────
  const refreshPatients = useCallback(async (params?: { setor_id?: string; busca?: string }) => {
    if (!token) return;
    setPatientsLoading(true);
    try {
      const data = await apiGetPatients(params);
      setPatients(data);
    } catch {
      // silently fail – UI shows empty state
    } finally {
      setPatientsLoading(false);
    }
  }, [token]);

  // ─── Notifications ────────────────────────────────────────────────────────
  const refreshNotifications = useCallback(async () => {
    if (!token) return;
    try {
      const data = await apiGetNotifications();
      setNotifications(data);
    } catch { /* ignore */ }
  }, [token]);

  const markRead = useCallback(async (id: string) => {
    await apiMarkNotificationRead(id);
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, lida: true } : n));
  }, []);

  const markAllRead = useCallback(async () => {
    await apiMarkAllNotificationsRead();
    setNotifications(prev => prev.map(n => ({ ...n, lida: true })));
  }, []);

  // ─── Bootstrap on login ───────────────────────────────────────────────────
  useEffect(() => {
    if (currentUser && token) {
      refreshPatients();
      refreshNotifications();
    }
  }, [currentUser, token, refreshPatients, refreshNotifications]);

  const unreadCount = notifications.filter(n => !n.lida).length;

  return (
    <AppContext.Provider value={{
      currentUser, token, isLoading,
      login, logout,
      patients, patientsLoading, refreshPatients,
      notifications, unreadCount, markRead, markAllRead,
    }}>
      {children}
    </AppContext.Provider>
  );
};
