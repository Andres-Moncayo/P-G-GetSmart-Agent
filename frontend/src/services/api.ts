import axios from 'axios';
import type { UserProfile, ApiKey, UserPreferences } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private client = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  constructor() {
    // Add CSRF token to state-changing requests
    this.client.interceptors.request.use((config) => {
      if (['post', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
        const csrfToken = this.getCsrfToken();
        if (csrfToken) {
          config.headers['X-CSRF-Token'] = csrfToken;
        }
      }
      return config;
    });

// Handle 401 responses with loop prevention
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalConfig = error.config;
        const isRefreshRequest = originalConfig.url === '/api/v1/auth/refresh';

        // Prevent infinite loops and don't retry unknown/no-token requests
        if (error.response?.status === 401 && !originalConfig._isRetry && !isRefreshRequest) {
          // Only attempt refresh if this isn't a simple auth check (getProfile during init)
          // Let the auth store handle the 401 gracefully for initial auth checks
          if (originalConfig.url !== '/api/v1/me') {
            originalConfig._isRetry = true;

            try {
              // Try to refresh token
              await this.client.post('/api/v1/auth/refresh');
              // Retry original request
              return this.client.request(originalConfig);
            } catch (refreshError) {
              // Refresh failed - clear state and redirect to login
              this.clearAuthState();
              window.location.href = '/';
            }
          }
        }

        // If refresh endpoint fails with 401, just redirect
        if (isRefreshRequest && error.response?.status === 401) {
          this.clearAuthState();
          window.location.href = '/';
        }

        return Promise.reject(error);
      }
    );
  }

  private clearAuthState(): void {
    // Clear auth-related cookies
    document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    // Clear any local storage we might have
    localStorage.removeItem('auth-storage');
  }

  private getCsrfToken(): string | null {
    const match = document.cookie.match(/(^|;)\\\\s*csrf_token\\\\s*=\\\\s*([^;]+)/);
    return match ? match[2] : null;
  }

  // Auth endpoints
  async login(provider: string) {
    const response = await this.client.post(`/api/v1/auth/login/${provider}`);
    return response.data;
  }

  async demoLogin() {
    const response = await this.client.post('/api/v1/auth/demo');
    return response.data;
  }

  async logout() {
    await this.client.post('/api/v1/auth/logout');
  }

  async refreshToken() {
    const response = await this.client.post('/api/v1/auth/refresh');
    return response.data;
  }

  // User profile endpoints
  async getProfile(): Promise<UserProfile> {
    const response = await this.client.get('/api/v1/me');
    return response.data;
  }

  async updateProfile(updates: { name?: string; preferences?: UserPreferences }): Promise<UserProfile> {
    const response = await this.client.patch('/api/v1/me', updates);
    return response.data;
  }

  // API keys endpoints
  async getApiKeys(): Promise<ApiKey[]> {
    const response = await this.client.get('/api/v1/me/api-keys');
    return response.data;
  }

  async createApiKey(name: string, scopes: string[] = ['read']): Promise<ApiKey & { key: string }> {
    const response = await this.client.post('/api/v1/me/api-keys', {
      name,
      scopes,
    });
    return response.data;
  }

  async revokeApiKey(keyId: string): Promise<void> {
    await this.client.delete(`/api/v1/me/api-keys/${keyId}`);
  }
}

export const apiClient = new ApiClient();