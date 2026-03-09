import React from 'react';
import { AppProvider, useApp } from './contexts/AppContext';
import { LoginScreen } from './components/LoginScreen';
import { Dashboard } from './components/Dashboard';
import { Toaster } from './components/ui/sonner';

function AppContent() {
  const { currentUser } = useApp();
  return currentUser ? <Dashboard /> : <LoginScreen />;
}

export default function App() {
  return (
    <AppProvider>
      <div className="size-full">
        <AppContent />
        <Toaster position="top-right" />
      </div>
    </AppProvider>
  );
}
