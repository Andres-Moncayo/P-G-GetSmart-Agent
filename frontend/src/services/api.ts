import axios, { type AxiosRequestConfig } from 'axios';
import type { UserProfile, ApiKey, UserPreferences } from '../types';
import type { GameSearchResponse, GameConfirmResponse, GameCandidate } from '../types/game';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const TOKEN_KEY = 'gs_access_token';

// Utility to convert GameCandidate to scraper format
function convertGameCandidateToScraperFormat(game: GameCandidate) {
  // Generate a UUID for the game_id (browser-compatible)
  const generateUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  };

  return {
    game_id: generateUUID(),
    name: game.name,
    release_year: game.release_year || new Date().getFullYear(),
    igdb_id: 0,
    rawg_id: game.rawg_id ? parseInt(game.rawg_id, 10) : 0,
    steam_app_id: game.steam_app_id ? parseInt(game.steam_app_id, 10) : null,
    aliases: []
  };
}

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

  async get<T = any>(path: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(path, config);
    return response.data;
  }

  async post<T = any>(path: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(path, data, config);
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

async confirmGame(gameId: string, source: string = 'rawg'): Promise<GameConfirmResponse> {
    const response = await this.client.post('/api/v1/games/confirm', {
      game_id: gameId,
      source,
    });
    return response.data;
  }

async analyzeGame(gameData: {
    game_id: string;
    name: string;
    release_year: number;
    rawg_id: number;
    steam_app_id?: number | null;
    aliases?: string[];
  }) {
    const response = await this.client.post('/scraper/analyze', gameData);
    return response.data;
}

async getReportStatus(reportId: string) {
    const response = await this.client.get(`/scraper/api/v1/reports/${reportId}/status`);
    return response.data;
  }

  async getPipelineStatus(reportId: string) {
    const response = await this.client.get(`/api/v1/games/pipeline/${reportId}/status`);
    return response.data;
  }

  async getPipelineLogs(reportId: string) {
    const response = await this.client.get(`/api/v1/games/pipeline/${reportId}/logs`);
    return response.data;
  }

  async startPipeline(gameId: string, source: string = 'rawg') {
    const response = await this.client.post('/api/v1/games/pipeline/start', {
      game_id: gameId,
      source,
    });
    return response.data;
  }

}

export const apiClient = new ApiClient();
