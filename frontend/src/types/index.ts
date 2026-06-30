export interface UserProfile {
  id: string;
  email: string;
  name: string;
  first_name?: string;
  last_name?: string;
  role: 'admin' | 'editor' | 'viewer' | 'demo';
  avatar_url?: string;
  avatar_initials?: string;
  department?: string;
  sso_provider?: 'google' | 'microsoft' | 'okta' | 'demo';
  preferences?: UserPreferences;
  created_at: string;
  updated_at: string;
  last_login_at?: string;
  is_active: boolean;
}

export interface UserPreferences {
  theme: 'dark' | 'light' | 'system';
  language: 'en' | 'es';
  notifications_email: boolean;
  notifications_push: boolean;
}

export interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  scopes: string[];
  created_at: string;
  last_used_at?: string;
}

export interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface UIState {
  profileModalOpen: boolean;
  activeNavItem: string;
}

export interface SsoProvider {
  id: string;
  name: string;
  icon: string;
  color: string;
}
