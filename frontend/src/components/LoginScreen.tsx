import React, { useState } from 'react';
import { useAuthStore } from '../stores/authStore';

export const LoginScreen: React.FC = () => {
  const { demoLogin, isLoading, error, clearError } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleCredentialsLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: wire up once backend endpoint is ready
  };

  const handleDemoLogin = async () => {
    clearError();
    await demoLogin();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center gap-6">
        <div className="relative flex items-center justify-center w-20 h-20">
          <img src="/logo.svg" alt="GetSmart Logo" className="w-20 h-20 drop-shadow-[0_0_15px_rgba(99,102,241,0.4)] relative z-10" />
          <div className="absolute -inset-2 rounded-3xl border-2 border-accent/30 animate-ping" />
        </div>
        <div className="text-center">
          <h2 className="text-xl font-semibold text-primary mb-1">
            Get<span className="text-accent">Smart</span>
          </h2>
          <p className="text-sm text-muted animate-pulse">Initializing demo session...</p>
        </div>
        <div className="flex gap-1.5">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-accent animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div
        className="absolute inset-0 opacity-50"
        style={{
          background: 'radial-gradient(ellipse at 50% 40%, rgba(59,130,246,0.08) 0%, transparent 80%)',
        }}
      />

      <div className="relative min-h-screen flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <img src="/logo.svg" alt="GetSmart Logo" className="w-20 h-20 drop-shadow-[0_0_15px_rgba(99,102,241,0.3)]" />
          </div>

          {/* Brand */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-primary mb-2">
              Get<span className="text-accent">Smart</span>
            </h1>
            <p className="text-sm text-muted">Game Intelligence Library</p>
          </div>

          {/* Credentials form */}
          <form onSubmit={handleCredentialsLogin} className="space-y-4 mb-5">
            <div>
              <label className="block text-xs font-medium text-muted mb-1.5">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full px-4 py-3 bg-black border border-border rounded-lg text-sm text-primary placeholder-muted focus:outline-none focus:border-accent transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-muted mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 bg-black border border-border rounded-lg text-sm text-primary placeholder-muted focus:outline-none focus:border-accent transition-colors pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-primary transition-colors"
                >
                  <i className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'} text-sm`} />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-border bg-black accent-accent cursor-pointer"
                />
                <span className="text-sm text-muted">Remember me</span>
              </label>
              <button type="button" className="text-xs text-accent hover:underline">
                Forgot password?
              </button>
            </div>

            <button
              type="submit"
              disabled={!email || !password}
              className="w-full px-4 py-3 bg-gradient-to-r from-accent to-secondary text-white rounded-lg text-sm font-medium hover:opacity-90 transition-opacity shadow-lg shadow-accent/20 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Sign in
            </button>
          </form>

          {/* Divider */}
          <div className="relative mb-5">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-3 bg-background text-muted">or</span>
            </div>
          </div>

          {/* Demo button */}
          <button
            onClick={handleDemoLogin}
            className="w-full px-4 py-3 bg-accent text-white rounded-lg font-medium hover:bg-blue-700 transition-colors duration-200 shadow-lg shadow-accent/25"
          >
            Sign in with demo account
          </button>

          {/* Error */}
          {error && (
            <div className="mt-4 p-3 bg-danger/10 border border-danger/20 rounded-lg">
              <p className="text-sm text-danger">{error}</p>
            </div>
          )}

          <p className="mt-8 text-center text-xs text-muted">
            By signing in, you agree to our Terms and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
};
