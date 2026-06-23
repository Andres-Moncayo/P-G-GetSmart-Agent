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
        // Prevent multiple simultaneous auth checks
        if (get().isLoading && get().isInitialized) {
          return;
        }

        set({ isLoading: true });
        
        try {
          // Use apiClient.getProfile() which uses the configured axios with withCredentials: true
          // Note: Refresh is handled by the axios interceptor, so we don't need to duplicate it here
          const user = await apiClient.getProfile();
          get().setUser(user);
        } catch (error: any) {
          // Any error means we're not authenticated
          // The axios interceptor will handle token refresh automatically ONLY for valid tokens
          // If refresh fails, it will redirect to login
          set({ 
            user: null, 
            isAuthenticated: false, 
            error: null
          });
        } finally {
          // GUARANTEE loading is set to false and initialization flag is set
          set({ 
            isLoading: false,
            isInitialized: true
          });
        }
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