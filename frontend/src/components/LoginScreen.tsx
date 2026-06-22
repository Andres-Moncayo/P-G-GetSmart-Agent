import React from 'react';
import { useAuthStore } from '../stores/authStore';
import type { SsoProvider } from '../types';

const ssoProviders: SsoProvider[] = [
  {
    id: 'google',
    name: 'Google',
    icon: 'fab fa-google',
    color: '#4285F4',
  },
  {
    id: 'microsoft', 
    name: 'Microsoft',
    icon: 'fab fa-microsoft',
    color: '#00A4EF',
  },
  {
    id: 'okta',
    name: 'Okta',
    icon: 'fas fa-shield-alt',
    color: '#007DC1',
  },
];

export const LoginScreen: React.FC = () => {
  const { login, demoLogin, isLoading, error, clearError } = useAuthStore();

const handleLogin = async (provider: string) => {
    clearError();
    if (provider === 'demo') {
      await demoLogin();
    } else {
      login(provider);
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background pattern */}
      <div 
        className="absolute inset-0 grid-dots opacity-50"
        style={{
          background: 'radial-gradient(ellipse at 50% 40%, rgba(59,130,246,0.08) 0%, transparent 80%)',
        }}
      />
      
      {/* Login card */}
      <div className="relative min-h-screen flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent to-secondary flex items-center justify-center shadow-lg">
              <i className="fas fa-gamepad text-white text-2xl" />
            </div>
          </div>
          
          {/* Brand */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-primary mb-2">
              Get<span className="text-accent">Smart</span>
            </h1>
            <p className="text-sm text-muted">Game Intelligence Library</p>
          </div>
          
          {/* SSO Buttons */}
          <div className="space-y-3 mb-6">
            {ssoProviders.map((provider) => (
              <button
                key={provider.id}
onClick={() => handleLogin(provider.id)}
                disabled={isLoading}
                className="w-full flex items-center px-4 py-3 bg-surface border border-border rounded-lg hover:bg-elevated hover:border-border-hover transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <i 
                  className={`${provider.icon} text-lg min-w-[20px]`}
                  style={{ color: provider.color }}
                />
                <span className="ml-3 text-sm font-medium text-secondary">
                  Sign in with {provider.name}
                </span>
              </button>
            ))}
          </div>
          
          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-background text-muted">or</span>
            </div>
          </div>
          
          {/* Demo Account */}
          <button
onClick={() => handleLogin('demo')}
            disabled={isLoading}
            className="w-full px-4 py-3 bg-accent text-white rounded-lg font-medium hover:bg-accent-dark transition-all duration-200 shadow-lg shadow-accent/25 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Sign in with demo account
          </button>
          
          {/* Error */}
          {error && (
            <div className="mt-4 p-3 bg-danger/10 border border-danger/20 rounded-lg">
              <p className="text-sm text-danger">{error}</p>
            </div>
          )}
          
          {/* Footer */}
          <p className="mt-8 text-center text-xs text-muted">
            By signing in, you agree to our Terms and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
};