import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '../services/api';
import type { AuthState, UserProfile } from '../types';

interface AuthStore extends AuthState {
  login: (provider: string) => void;
  demoLogin: () => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: UserProfile) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  checkAuth: () => Promise<void>;
  isInitialized: boolean;
  isLoggingOut: boolean;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      isInitialized: false,
      isLoggingOut: false,

      login: async (provider: string) => {
        set({ isLoading: true, error: null });
        
        try {
          if (provider === 'demo') {
            const data = await apiClient.demoLogin();
            if (data?.user) {
              get().setUser(data.user);
            } else {
              set({ isLoading: false });
              await get().checkAuth();
            }
          } else {
            // Handle SSO login
            const data = await apiClient.login(provider);
            if (data.redirect_url) {
              window.location.href = data.redirect_url;
            } else {
              throw new Error('Login failed');
            }
          }
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false 
          });
        }
      },

      demoLogin: async () => {
        set({ isLoading: true, error: null });

        try {
          // Simulated delay for visual effect
          await new Promise(resolve => setTimeout(resolve, 1500));
          
          const demoUser: UserProfile = {
            id: 'demo-123',
            email: 'demo@getsmart.com',
            name: 'Demo User',
            role: 'demo',
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          };
          get().setUser(demoUser);
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Demo login failed',
            isLoading: false
          });
        }
      },

      logout: async () => {
        set({ isLoggingOut: true });
        try {
          await Promise.all([
            apiClient.logout().catch(() => {}),
            new Promise(resolve => setTimeout(resolve, 2000)),
          ]);
        } finally {
          set({
            user: null,
            isAuthenticated: false,
            error: null,
            isLoading: false,
            isInitialized: true,
            isLoggingOut: false,
          });
        }
      },

      setUser: (user: UserProfile) => {
        set({ 
          user, 
          isAuthenticated: true, 
          error: null,
          isLoading: false,
          isInitialized: true
        });
      },

      clearError: () => {
        set({ error: null });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      checkAuth: async () => {
        if (get().isLoading && get().isInitialized) {
          return;
        }

        // Force login screen on every initial load for visual demo purposes
        localStorage.removeItem('gs_access_token');
        localStorage.removeItem('auth-storage');

        set({
          isAuthenticated: false,
          user: null,
          error: null,
          isLoading: false,
          isInitialized: true,
        });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);