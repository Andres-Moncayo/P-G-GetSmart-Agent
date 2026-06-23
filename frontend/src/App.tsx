import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import { LoginScreen } from './components/LoginScreen';
import { Topbar } from './components/Topbar';
import { Dashboard } from './pages/Dashboard';

function App() {
  const { isAuthenticated, isLoading, isInitialized, isLoggingOut, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Show loading ONLY during initial auth check, not during regular loading states
  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted">Loading...</p>
        </div>
      </div>
    );
  }

  if (isLoggingOut) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center gap-6">
        <div className="relative">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent to-secondary flex items-center justify-center shadow-lg shadow-accent/30 opacity-50">
            <i className="fas fa-gamepad text-white text-3xl" />
          </div>
        </div>
        <div className="text-center">
          <h2 className="text-3xl font-bold text-primary mb-2">Bye bye! 👋</h2>
          <p className="text-sm text-muted animate-pulse">See you next time...</p>
        </div>
        <div className="flex gap-1.5">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-accent animate-bounce"
              style={{ animationDelay: `${i * 0.10}s` }}
            />
          ))}
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="h-screen flex flex-col bg-background overflow-hidden">
        <Topbar />
        <main className="flex-1 min-h-0 overflow-hidden">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/reports" element={
              <div className="container mx-auto px-6 py-8">
                <h2 className="text-2xl font-bold text-primary mb-4">Reports</h2>
                <p className="text-muted">Game analysis reports will appear here.</p>
              </div>
            } />
            <Route path="/pipeline" element={
              <div className="container mx-auto px-6 py-8">
                <h2 className="text-2xl font-bold text-primary mb-4">Pipeline</h2>
                <p className="text-muted">Data processing pipeline status.</p>
              </div>
            } />
            <Route path="/templates" element={
              <div className="container mx-auto px-6 py-8">
                <h2 className="text-2xl font-bold text-primary mb-4">Templates</h2>
                <p className="text-muted">Report templates and examples.</p>
              </div>
            } />
            <Route path="/docs" element={
              <div className="container mx-auto px-6 py-8">
                <h2 className="text-2xl font-bold text-primary mb-4">Documentation</h2>
                <p className="text-muted">Help documentation and guides.</p>
              </div>
            } />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;