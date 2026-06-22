import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import { LoginScreen } from './components/LoginScreen';
import { Topbar } from './components/Topbar';
import { Dashboard } from './pages/Dashboard';

function App() {
  const { isAuthenticated, isLoading, isInitialized, checkAuth } = useAuthStore();

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

  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Topbar />
        <main>
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