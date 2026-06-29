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
          const [data] = await Promise.all([
            apiClient.demoLogin(),
            new Promise(resolve => setTimeout(resolve, 3000)),
          ]);
          if (data?.user) {
            get().setUser(data.user);
          } else {
            set({ isLoading: false });
            await get().checkAuth();
          }
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

        const hasToken = !!localStorage.getItem('gs_access_token');

        set({
          isAuthenticated: hasToken,
          isLoading: false,
          isInitialized: true,
          ...(hasToken ? {} : { user: null, error: null }),
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