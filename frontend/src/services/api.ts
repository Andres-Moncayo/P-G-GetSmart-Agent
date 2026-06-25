import axios from 'axios';
import type { UserProfile, ApiKey, UserPreferences } from '../types';
import type { GameSearchResponse, GameConfirmResponse } from '../types/game';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const TOKEN_KEY = 'gs_access_token';

class ApiClient {
  private client = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  constructor() {
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem(TOKEN_KEY);
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }

      if (['post', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
        const csrfToken = this.getCsrfToken();
        if (csrfToken) {
          config.headers['X-CSRF-Token'] = csrfToken;
        }
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalConfig = error.config;
        const isRefreshRequest = originalConfig.url === '/api/v1/auth/refresh';

        if (error.response?.status === 401 && !originalConfig._isRetry && !isRefreshRequest) {
          if (originalConfig.url !== '/api/v1/me') {
            originalConfig._isRetry = true;

            try {
              const refreshData = await this.client.post('/api/v1/auth/refresh');
              if (refreshData.data?.access_token) {
                localStorage.setItem(TOKEN_KEY, refreshData.data.access_token);
              }
              return this.client.request(originalConfig);
            } catch {
              this.clearAuthState();
              window.location.href = '/';
            }
          }
        }

        if (isRefreshRequest && error.response?.status === 401) {
          this.clearAuthState();
          window.location.href = '/';
        }

        return Promise.reject(error);
      }
    );
  }

  private clearAuthState(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem('auth-storage');
  }

  private getCsrfToken(): string | null {
    const match = document.cookie.match(/(^|;)\s*csrf_token\s*=\s*([^;]+)/);
    return match ? match[2] : null;
  }

  async login(provider: string) {
    const response = await this.client.post(`/api/v1/auth/login/${provider}`);
    return response.data;
  }

  async demoLogin() {
    const response = await this.client.post('/api/v1/auth/demo');
    if (response.data?.access_token) {
      localStorage.setItem(TOKEN_KEY, response.data.access_token);
    }
    return response.data;
  }

  async logout() {
    try {
      await this.client.post('/api/v1/auth/logout');
    } finally {
      this.clearAuthState();
    }
  }

  async refreshToken() {
    const response = await this.client.post('/api/v1/auth/refresh');
    if (response.data?.access_token) {
      localStorage.setItem(TOKEN_KEY, response.data.access_token);
    }
    return response.data;
  }

  async getProfile(): Promise<UserProfile> {
    const response = await this.client.get('/api/v1/me');
    return response.data;
  }

  async updateProfile(updates: { name?: string; preferences?: UserPreferences }): Promise<UserProfile> {
    const response = await this.client.patch('/api/v1/me', updates);
    return response.data;
  }

  async getApiKeys(): Promise<ApiKey[]> {
    const response = await this.client.get('/api/v1/me/api-keys');
    return response.data;
  }

  async createApiKey(name: string, scopes: string[] = ['read']): Promise<ApiKey & { key: string }> {
    const response = await this.client.post('/api/v1/me/api-keys', { name, scopes });
    return response.data;
  }

  async revokeApiKey(keyId: string): Promise<void> {
    await this.client.delete(`/api/v1/me/api-keys/${keyId}`);
  }

  async searchGames(query: string, limit = 10): Promise<GameSearchResponse> {
    const response = await this.client.get('/api/v1/games/search', {
      params: { q: query, limit },
    });
    return response.data;
  }

  async confirmGame(gameId: string, source: string = 'igdb'): Promise<GameConfirmResponse> {
    const response = await this.client.post('/api/v1/games/confirm', {
      game_id: gameId,
      source,
    });
    return response.data;
  }
}

export const apiClient = new ApiClient();
