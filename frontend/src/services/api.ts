import axios, { type AxiosRequestConfig } from 'axios';
import type { UserProfile, ApiKey, UserPreferences } from '../types';
import type { GameSearchResponse, GameConfirmResponse, GameCandidate, ApiReport, ApiReportListResponse } from '../types/game';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';
const TOKEN_KEY = 'gs_access_token';

// Callback for navigation to avoid React Router conflicts
let authRedirectCallback: (() => void) | null = null;

export const setAuthRedirectCallback = (callback: () => void) => {
  authRedirectCallback = callback;
};

const handleAuthRedirect = () => {
  if (authRedirectCallback) {
    authRedirectCallback();
  } else {
    // Fallback to window.location if no callback is set
    window.location.href = '/';
  }
};

// ─── Frontend Mock Data Fallback (Serverless Mode) ───────────────────────────
const MOCK_GAMES = [
  {
    id: "b995247f-5b34-431e-ae69-3e5c7bf08776",
    name: "Ark: Survival Evolved",
    developer: "Studio Wildcard",
    release_year: 2017,
    primary_genre: "Adventure",
    primary_platform: "PC",
    all_genres: ["Adventure", "Indie", "RPG", "Simulator"],
    all_platforms: ["PC", "PlayStation 4", "Xbox One", "Nintendo Switch"],
    cover_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1vce.png",
    slug: "ark-survival-evolved"
  },
  {
    id: "c225247f-5b34-431e-ae69-3e5c7bf08776",
    name: "Hades",
    developer: "Supergiant Games",
    release_year: 2020,
    primary_genre: "Indie",
    primary_platform: "PC",
    all_genres: ["Indie", "Action", "RPG"],
    all_platforms: ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S", "Nintendo Switch"],
    cover_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1v7f.png",
    slug: "hades"
  },
  {
    id: "d335247f-5b34-431e-ae69-3e5c7bf08776",
    name: "Cyberpunk 2077",
    developer: "CD PROJEKT RED",
    release_year: 2020,
    primary_genre: "RPG",
    primary_platform: "PC",
    all_genres: ["RPG", "Action", "Sci-Fi"],
    all_platforms: ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S"],
    cover_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co2m76.png",
    slug: "cyberpunk-2077"
  },
  {
    id: "e445247f-5b34-431e-ae69-3e5c7bf08776",
    name: "The Witcher 3: Wild Hunt",
    developer: "CD PROJEKT RED",
    release_year: 2015,
    primary_genre: "RPG",
    primary_platform: "PC",
    all_genres: ["RPG", "Action", "Adventure"],
    all_platforms: ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S", "Nintendo Switch"],
    cover_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1sf5.png",
    slug: "the-witcher-3-wild-hunt"
  },
  {
    id: "f555247f-5b34-431e-ae69-3e5c7bf08776",
    name: "Minecraft",
    developer: "Mojang Studios",
    release_year: 2011,
    primary_genre: "Simulator",
    primary_platform: "PC",
    all_genres: ["Simulator", "Adventure", "Indie"],
    all_platforms: ["PC", "PlayStation 4", "Xbox One", "Nintendo Switch", "Mobile"],
    cover_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1r78.png",
    slug: "minecraft"
  },
  {
    id: "a115247f-5b34-431e-ae69-3e5c7bf08776",
    name: "Elden Ring",
    developer: "FromSoftware",
    release_year: 2022,
    primary_genre: "RPG",
    primary_platform: "PC",
    all_genres: ["RPG", "Action"],
    all_platforms: ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S"],
    cover_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co4hju.png",
    slug: "elden-ring"
  },
  {
    id: "a225247f-5b34-431e-ae69-3e5c7bf08776",
    name: "Red Dead Redemption 2",
    developer: "Rockstar Games",
    release_year: 2018,
    primary_genre: "Adventure",
    primary_platform: "PlayStation 4",
    all_genres: ["Adventure", "Action"],
    all_platforms: ["PC", "PlayStation 4", "Xbox One"],
    cover_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1q1f.png",
    slug: "red-dead-redemption-2"
  },
  {
    id: "a335247f-5b34-431e-ae69-3e5c7bf08776",
    name: "The Legend of Zelda: Breath of the Wild",
    developer: "Nintendo EPD",
    release_year: 2017,
    primary_genre: "Adventure",
    primary_platform: "Nintendo Switch",
    all_genres: ["Adventure", "RPG"],
    all_platforms: ["Nintendo Switch", "Wii U"],
    cover_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1r7f.png",
    slug: "the-legend-of-zelda-breath-of-the-wild"
  },
  {
    id: "a445247f-5b34-431e-ae69-3e5c7bf08776",
    name: "Grand Theft Auto V",
    developer: "Rockstar North",
    release_year: 2013,
    primary_genre: "Action",
    primary_platform: "PC",
    all_genres: ["Action", "Adventure"],
    all_platforms: ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S", "PlayStation 3", "Xbox 360"],
    cover_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1r8c.png",
    slug: "grand-theft-auto-v"
  },
  {
    id: "a555247f-5b34-431e-ae69-3e5c7bf08776",
    name: "Portal 2",
    developer: "Valve",
    release_year: 2011,
    primary_genre: "Indie",
    primary_platform: "PC",
    all_genres: ["Indie", "Action", "Adventure"],
    all_platforms: ["PC", "PlayStation 3", "Xbox 360", "Nintendo Switch"],
    cover_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1r7a.png",
    slug: "portal-2"
  }
];

function getMockStructuredSkills(gameName: string, scores: Record<string, number>): any[] {
  return [
    {
      skill_key: "design_art",
      skill_label: "Design & Art",
      score: scores["Design & Art"] || 9.0,
      confidence_raw: 0.95,
      summary: `La dirección artística de ${gameName} destaca de manera sobresaliente. Presenta una estética visual sumamente pulida, una paleta de colores bien equilibrada y un diseño de personajes/entornos que consolida perfectamente su identidad visual.`,
      strengths: ["Dirección de arte única y memorable.", "Excelente uso de la iluminación.", "Coherencia estética en todos los niveles."],
      weaknesses: ["Ciertas texturas secundarias muestran baja resolución.", "Consumo elevado de recursos gráficos en ultra."],
      key_findings: ["La identidad visual ha sido clave para su posicionamiento.", "El diseño ambiental apoya de forma orgánica la narrativa."],
      risks: ["Incompatibilidad de shaders en ciertos modelos de GPU antiguos."],
      opportunities: ["Lanzamiento de un libro de arte digital o skins estéticas exclusivas."],
      evidence_count: 15
    },
    {
      skill_key: "user_experience",
      skill_label: "User Experience",
      score: scores["User Experience"] || 8.8,
      confidence_raw: 0.92,
      summary: `La interfaz y el flujo del jugador en ${gameName} están diseñados intuitivamente. Los menús son de fácil acceso, la curva de aprendizaje está bien balanceada y el sistema de tutoría se integra de manera orgánica con el juego.`,
      strengths: ["Interfaz limpia y minimalista.", "Controles altamente responsivos.", "Curva de aprendizaje fluida."],
      weaknesses: ["Falta de opciones avanzadas de accesibilidad.", "Ciertos submenús de configuración requieren demasiados clics."],
      key_findings: ["Los jugadores reportan alta satisfacción con los controles.", "El onboarding inicial reduce considerablemente la tasa de abandono."],
      risks: ["Frustración potencial en consolas si el mapeado por defecto no se optimiza."],
      opportunities: ["Implementar un HUD dinámico personalizable."],
      evidence_count: 12
    },
    {
      skill_key: "tech_systems",
      skill_label: "Technology Systems",
      score: scores["Technology Systems"] || 8.5,
      confidence_raw: 0.89,
      summary: `El apartado tecnológico y de optimización de ${gameName} demuestra bases sólidas. Se destaca por una tasa de refresco estable y tiempos de carga reducidos gracias a un buen manejo de memoria.`,
      strengths: ["Estabilidad de FPS en situaciones de alto procesamiento.", "Excelente compresión de archivos reduciendo el peso.", "Manejo eficiente del streaming de texturas."],
      weaknesses: ["Bugs menores en la detección de colisiones.", "El motor físico muestra comportamientos erráticos bajo estrés extremo."],
      key_findings: ["La tasa de frames promedio se mantiene estable.", "La carga asíncrona de assets reduce los tiempos de pantalla de carga."],
      risks: ["Posibles cuellos de botella en CPUs de gamas bajas."],
      opportunities: ["Actualización para soporte nativo de Ray Tracing."],
      evidence_count: 18
    },
    {
      skill_key: "strategy_market",
      skill_label: "Strategy Market",
      score: scores["Strategy Market"] || 9.2,
      confidence_raw: 0.94,
      summary: `Estratégicamente, ${gameName} goza de un excelente posicionamiento de mercado. Su modelo de negocio se alinea con las demandas de su audiencia y presenta un alto potencial de monetización.`,
      strengths: ["Fuerte retención a través de eventos estacionales.", "Estrategia de precios competitiva.", "Excelente recepción crítica."],
      weaknesses: ["Dependencia excesiva de un nicho particular.", "Poca visibilidad de marketing en mercados emergentes."],
      key_findings: ["El ROI de campañas de marketing de influencers ha sido superior.", "Soporte continuo garantiza estabilidad de ventas."],
      risks: ["Saturación de competidores directos en el mismo trimestre."],
      opportunities: ["Expandir a plataformas móviles o nube."],
      evidence_count: 14
    }
  ];
}

const MOCK_REPORTS: Record<string, ApiReport> = {};

MOCK_GAMES.forEach((game, index) => {
  const scores = {
    "Design & Art": [8.0, 9.8, 9.4, 9.5, 8.5, 9.8, 9.9, 9.7, 9.2, 9.5][index],
    "User Experience": [7.5, 9.6, 8.5, 9.2, 9.2, 8.8, 9.2, 9.5, 9.4, 9.7][index],
    "Technology Systems": [6.8, 9.4, 8.0, 8.8, 9.4, 9.0, 9.4, 9.4, 9.0, 9.5][index],
    "Strategy Market": [8.5, 9.5, 9.0, 9.4, 9.8, 9.6, 9.5, 9.6, 9.8, 9.2][index]
  };

  const summaries = [
    "Un sandbox masivo de supervivencia y domesticación de dinosaurios con una progresión tecnológica única.",
    "Un exponente perfecto de cómo fusionar narrativa rica y jugabilidad roguelike adictiva.",
    "Un ambicioso RPG de acción en primera persona que explora el transhumanismo en una distopía futurista.",
    "Una de las cumbres del diseño de misiones y mundos abiertos de fantasía oscura.",
    "Un sandbox infinito que se ha convertido en un fenómeno cultural y educativo global.",
    "Una magistral evolución del género Souls-like hacia un sandbox abierto de exploración libre.",
    "Una de las narrativas más profundas e inmersivas y un nivel de detalle técnico casi inigualable en la industria.",
    "Una revolución en el diseño de niveles que incentiva al jugador a experimentar en lugar de seguir marcadores.",
    "Un coloso comercial indiscutible impulsado por su masivo ecosistema en línea (GTA Online).",
    "Uno de los juegos de puzles perfectos, aclamado por su narrativa ingeniosa y su modo cooperativo."
  ];

  MOCK_REPORTS[game.id] = {
    id: game.id,
    status: 'completed',
    game: game,
    created_at: new Date(2026, 7, index + 1).toISOString(),
    updated_at: new Date(2026, 7, index + 1).toISOString(),
    confidence_score: [0.95, 0.98, 0.91, 0.96, 0.99, 0.97, 0.95, 0.98, 0.94, 0.97][index],
    tags: [["Survival", "Dinosaur"], ["Roguelike", "Action"], ["Cyberpunk", "Sci-Fi"], ["Fantasy", "Story Rich"], ["Sandbox", "Crafting"], ["Souls-like", "Open World"], ["Western", "Realistic"], ["Open World", "Fantasy"], ["Crime", "Sandbox"], ["Puzzle", "Comedy"]][index],
    current_phase: 'storage',
    pipeline_progress: 100,
    executive_summary: {
      summary: summaries[index],
      verdict: "Análisis integral completado con el más alto nivel de recomendación crítica."
    },
    thematic_analysis: {
      skill_scores: scores,
      structured_skills: getMockStructuredSkills(game.name, scores)
    },
    confidence_analysis: {
      score: [0.95, 0.98, 0.91, 0.96, 0.99, 0.97, 0.95, 0.98, 0.94, 0.97][index],
      notes: "Análisis offline completado a partir de base estructurada local."
    }
  };
});

function handleMockFallback(config: AxiosRequestConfig): any {
  const url = config.url || '';
  
  if (url === '/api/v1/reports') {
    const listResponse: ApiReportListResponse = {
      items: Object.values(MOCK_REPORTS),
      pagination: { page: 1, page_size: 200, total: MOCK_GAMES.length, total_pages: 1 },
      facets: {
        genre: [{ value: 'Adventure', count: 3 }, { value: 'RPG', count: 4 }, { value: 'Indie', count: 3 }, { value: 'Simulator', count: 2 }],
        platform: [{ value: 'PC', count: 8 }, { value: 'PlayStation 4', count: 6 }, { value: 'Xbox One', count: 5 }, { value: 'Nintendo Switch', count: 4 }],
        developer: [{ value: 'CD PROJEKT RED', count: 2 }, { value: 'Rockstar Games', count: 2 }],
        status: [{ value: 'completed', count: MOCK_GAMES.length }]
      }
    };
    return { data: listResponse, status: 200, statusText: 'OK', headers: {}, config };
  }
  
  const reportDetailMatch = url.match(/^\/api\/v1\/reports\/([a-fA-F0-9-]+)$/);
  if (reportDetailMatch) {
    const reportId = reportDetailMatch[1];
    const report = MOCK_REPORTS[reportId];
    if (report) {
      return { data: report, status: 200, statusText: 'OK', headers: {}, config };
    }
  }

  const reportContentMatch = url.match(/^\/api\/v1\/reports\/([a-fA-F0-9-]+)\/content/);
  if (reportContentMatch) {
    const reportId = reportContentMatch[1];
    const report = MOCK_REPORTS[reportId];
    if (report) {
      const content = `# ${report.game.name} - Análisis Completo Offline\n\nEste reporte se está sirviendo de forma serverless en el navegador porque el servidor backend no se encuentra activo.`;
      return { data: { format: 'markdown', content }, status: 200, statusText: 'OK', headers: {}, config };
    }
  }

  const pipelineStatusMatch = url.match(/^\/api\/v1\/games\/pipeline\/([a-fA-F0-9-]+)\/status$/);
  if (pipelineStatusMatch) {
    const reportId = pipelineStatusMatch[1];
    const report = MOCK_REPORTS[reportId];
    if (report) {
      const statusData = {
        report_id: reportId,
        phase: 'storage',
        status: 'completed',
        is_complete: true,
        overall_progress: 100,
        phases: {
          scraping: { status: 'completed', progress: 100, tasks: [] },
          analysis: { status: 'completed', progress: 100, tasks: [] },
          synthesis: { status: 'completed', progress: 100, tasks: [] },
          storage: { status: 'completed', progress: 100, tasks: [] }
        },
        logs: [{ timestamp: new Date().toISOString(), level: 'info', message: 'Offline Mode Activated' }]
      };
      return { data: statusData, status: 200, statusText: 'OK', headers: {}, config };
    }
  }

  const scraperStatusMatch = url.match(/^\/scraper\/api\/v1\/reports\/([a-fA-F0-9-]+)\/status$/);
  if (scraperStatusMatch) {
    const reportId = scraperStatusMatch[1];
    const report = MOCK_REPORTS[reportId];
    if (report) {
      return { data: { status: 'completed', overall_progress: 100 }, status: 200, statusText: 'OK', headers: {}, config };
    }
  }

  return null;
}

// ──────────────────────────────────────────────────────────────────────────────

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
        // Intercept network errors, proxy errors, or 404 static hosting errors (no backend exists) to apply mock fallback
        const status = error.response?.status;
        if (!error.response || error.code === 'ERR_NETWORK' || status === 404 || status === 502 || status === 503 || status === 504) {
          const fallbackResponse = handleMockFallback(error.config);
          if (fallbackResponse) {
            console.warn("API request failed. Falling back to frontend serverless mock data!");
            return fallbackResponse;
          }
        }

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
              handleAuthRedirect();
            }
          }
        }

        if (isRefreshRequest && error.response?.status === 401) {
          this.clearAuthState();
          handleAuthRedirect();
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
    // Intercept demo login offline
    try {
      const response = await this.client.post('/api/v1/auth/demo');
      if (response.data?.access_token) {
        localStorage.setItem(TOKEN_KEY, response.data.access_token);
      }
      return response.data;
    } catch (e) {
      localStorage.setItem(TOKEN_KEY, "mock-offline-token");
      return { access_token: "mock-offline-token", user: { id: "00000000-0000-0000-0000-000000000001", name: "Offline Developer" } };
    }
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
    try {
      const response = await this.client.get('/api/v1/me');
      return response.data;
    } catch (e) {
      return { id: "00000000-0000-0000-0000-000000000001", email: "mock@developer.com", name: "Offline Developer", role: "developer", created_at: new Date().toISOString() };
    }
  }

  async updateProfile(updates: { name?: string; preferences?: UserPreferences }): Promise<UserProfile> {
    const response = await this.client.patch('/api/v1/me', updates);
    return response.data;
  }

  async getApiKeys(): Promise<ApiKey[]> {
    try {
      const response = await this.client.get('/api/v1/me/api-keys');
      return response.data;
    } catch (e) {
      return [];
    }
  }

  async createApiKey(name: string, scopes: string[] = ['read']): Promise<ApiKey & { key: string }> {
    const response = await this.client.post('/api/v1/me/api-keys', { name, scopes });
    return response.data;
  }

  async revokeApiKey(keyId: string): Promise<void> {
    await this.client.delete(`/api/v1/me/api-keys/${keyId}`);
  }

  async searchGames(query: string, limit = 10): Promise<GameSearchResponse> {
    try {
      const response = await this.client.get('/api/v1/games/search', {
        params: { q: query, limit },
      });
      return response.data;
    } catch (e) {
      // Return a simulated search result offline
      const matches = MOCK_GAMES.filter(g => g.name.toLowerCase().includes(query.toLowerCase()));
      return {
        query,
        total: matches.length,
        candidates: matches as any,
        sources_queried: ['offline-cache'],
        latency_ms: 5
      };
    }
  }

  async confirmGame(gameId: string, source: string = 'rawg'): Promise<GameConfirmResponse> {
    try {
      const response = await this.client.post('/api/v1/games/confirm', {
        game_id: gameId,
        source,
      });
      return response.data;
    } catch (e) {
      const game = MOCK_GAMES.find(g => g.id === gameId);
      return {
        confirmed_game: game as any,
        can_run_pipeline: true,
        pipeline_token: "mock-offline-pipeline-token"
      };
    }
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
    try {
      const response = await this.client.post('/api/v1/games/pipeline/start', {
        game_id: gameId,
        source,
      });
      return response.data;
    } catch (e) {
      return {
        report_id: gameId,
        phase: 'storage',
        status: 'completed',
        is_complete: true,
        message: 'Offline analysis simulated successfully',
        result: {},
        seconds_elapsed: 0.5,
        seconds_remaining: 0,
        tasks_succeeded: 4,
        tasks_failed: 0,
        tasks_total: 4
      };
    }
  }

  async getReports(params?: {
    genre?: string[];
    developer?: string[];
    platform?: string[];
    status?: string[];
    year_from?: number;
    year_to?: number;
    search?: string;
    sort_by?: string;
    sort_dir?: 'asc' | 'desc';
    page?: number;
    page_size?: number;
  }): Promise<ApiReportListResponse> {
    const response = await this.client.get('/api/v1/reports', { params });
    return response.data;
  }

  async getReportDetail(reportId: string): Promise<ApiReport> {
    const response = await this.client.get(`/api/v1/reports/${reportId}`);
    return response.data;
  }

  async getReportContent(reportId: string): Promise<string> {
    const response = await this.client.get(`/api/v1/reports/${reportId}/content?format=markdown`);
    return response.data?.content || '';
  }

  async getReportPdfUrl(reportId: string): Promise<string> {
    try {
      const response = await this.client.get(`/api/v1/reports/${reportId}/content?format=pdf`);
      return response.data?.content_url || '';
    } catch (e) {
      return '';
    }
  }

  async deleteReport(reportId: string): Promise<void> {
    await this.client.delete(`/api/v1/reports/${reportId}`);
  }
}

export const apiClient = new ApiClient();
