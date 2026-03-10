import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { useApp } from '../contexts/AppContext';
import { AlertCircle, Loader2, Heart } from 'lucide-react';
import { Alert, AlertDescription } from './ui/alert';

interface QuickLogin { email: string; role: string; name: string; password: string }

const QUICK_LOGINS: QuickLogin[] = [
  { email: 'nutricionista@hospital.com', password: 'nutri123',    role: 'Nutricionista', name: 'Dra. Ana Silva'  },
  { email: 'copeiro@hospital.com',       password: 'copeiro123',  role: 'Copeiro',       name: 'João Copeiro'   },
  { email: 'admin@hospital.com',         password: 'admin123',    role: 'Administrador', name: 'Maria Admin'    },
];

const ROLE_COLORS: Record<string, string> = {
  Nutricionista: 'text-emerald-600',
  Copeiro:       'text-amber-600',
  Administrador: 'text-blue-600',
};

export const LoginScreen: React.FC = () => {
  const [email, setEmail]     = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]     = useState('');
  const { login, isLoading }  = useApp();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? 'Email ou senha inválidos.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
  };

  const fillQuick = (q: QuickLogin) => {
    setEmail(q.email);
    setPassword(q.password);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-100/60 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-indigo-100/60 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md animate-fade-in">
        {/* Logo / Header */}
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-blue-200">
            <Heart className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">SNH</h1>
          <p className="text-sm text-gray-500 mt-1">Sistema de Nutrição Hospitalar</p>
        </div>

        <Card className="shadow-xl shadow-blue-100/50 border-0">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg">Entrar no sistema</CardTitle>
            <CardDescription>Acesse com suas credenciais institucionais</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu@hospital.com"
                  required
                  autoFocus
                  className="h-10"
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="password">Senha</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="h-10"
                />
              </div>

              {error && (
                <Alert variant="destructive" className="py-2">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-sm">{error}</AlertDescription>
                </Alert>
              )}

              <Button
                type="submit"
                className="w-full h-10 bg-blue-600 hover:bg-blue-700"
                disabled={isLoading}
              >
                {isLoading ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Entrando...</>
                ) : (
                  'Entrar'
                )}
              </Button>
            </form>

            {/* Quick access */}
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-muted-foreground">Acesso rápido (demo)</span>
                </div>
              </div>

              <div className="mt-4 space-y-2">
                {QUICK_LOGINS.map((q) => (
                  <Button
                    key={q.email}
                    type="button"
                    variant="outline"
                    size="sm"
                    className="w-full justify-between h-9 font-normal"
                    onClick={() => fillQuick(q)}
                  >
                    <span className="text-gray-700">{q.name}</span>
                    <span className={`text-xs font-medium ${ROLE_COLORS[q.role]}`}>{q.role}</span>
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        <p className="mt-4 text-center text-xs text-gray-400">
          UFCA · ES0008 POO · Sistema acadêmico
        </p>
      </div>
    </div>
  );
};
