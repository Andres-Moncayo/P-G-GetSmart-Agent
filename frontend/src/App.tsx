import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import { setAuthRedirectCallback } from './services/api';
import { LoginScreen } from './components/LoginScreen';
import { Topbar } from './components/Topbar';
import { Dashboard } from './pages/Dashboard';
import PipelineProgressPage from './pages/PipelineProgressPage';

function AuthenticatedApp() {
  const navigate = useNavigate();

  useEffect(() => {
    // Set up the API client to use React Router navigation
    setAuthRedirectCallback(() => navigate('/'));
  }, [navigate]);

  return (
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
          <Route path="/pipeline/:reportId" element={<PipelineProgressPage />} />
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
  );
}

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
        <div className="relative flex items-center justify-center w-20 h-20 opacity-50">
          <img src="/logo.svg" alt="GetSmart Logo" className="w-20 h-20 drop-shadow-[0_0_15px_rgba(99,102,241,0.4)]" />
        </div>
        <div className="text-center">
          <h2 className="text-3xl font-bold text-primary mb-2">Bye bye!</h2>
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
      <AuthenticatedApp />
    </Router>
  );
}

export default App;
