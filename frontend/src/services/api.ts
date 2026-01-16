/**
 * API Service for CommitQuest
 * 
 * Centralized API client with:
 * - Type-safe requests and responses
 * - Automatic token refresh
 * - Request/response interceptors
 * - Error handling
 */
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import {
  AuthTokens,
  AuthResponse,
  LoginCredentials,
  RegisterData,
  User,
  Challenge,
  ChallengeCreateData,
  ChallengeParticipant,
  Contribution,
  ContributionCreateData,
  Proof,
  Team,
  Duel,
  PaginatedResponse,
  ApiError,
} from '../types';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const TOKEN_KEY = 'commitquest_tokens';

// Token storage utilities
const getStoredTokens = (): AuthTokens | null => {
  const stored = localStorage.getItem(TOKEN_KEY);
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  }
  return null;
};

const setStoredTokens = (tokens: AuthTokens): void => {
  localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
};

const clearStoredTokens = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokens = getStoredTokens();
    if (tokens?.access && config.headers) {
      config.headers.Authorization = `Bearer ${tokens.access}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response interceptor - handle token refresh
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

const subscribeTokenRefresh = (cb: (token: string) => void): void => {
  refreshSubscribers.push(cb);
};

const onTokenRefreshed = (token: string): void => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    // Handle 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Wait for token refresh
        return new Promise((resolve) => {
          subscribeTokenRefresh((token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(apiClient(originalRequest));
          });
        });
      }
      
      originalRequest._retry = true;
      isRefreshing = true;
      
      const tokens = getStoredTokens();
      if (tokens?.refresh) {
        try {
          const response = await axios.post<{ access: string }>(
            `${API_BASE_URL}/auth/token/refresh/`,
            { refresh: tokens.refresh }
          );
          
          const newTokens: AuthTokens = {
            access: response.data.access,
            refresh: tokens.refresh,
          };
          setStoredTokens(newTokens);
          onTokenRefreshed(response.data.access);
          
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          }
          
          return apiClient(originalRequest);
        } catch (refreshError) {
          clearStoredTokens();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// API Error handler
const handleApiError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error) && error.response?.data) {
    return error.response.data as ApiError;
  }
  return { detail: 'An unexpected error occurred' };
};

// Auth API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login/', credentials);
    setStoredTokens(response.data.tokens);
    return response.data;
  },
  
  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register/', data);
    setStoredTokens(response.data.tokens);
    return response.data;
  },
  
  logout: async (): Promise<void> => {
    const tokens = getStoredTokens();
    if (tokens?.refresh) {
      try {
        await apiClient.post('/auth/logout/', { refresh: tokens.refresh });
      } catch {
        // Ignore logout errors
      }
    }
    clearStoredTokens();
  },
  
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me/');
    return response.data;
  },
  
  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.patch<User>('/auth/me/', data);
    return response.data;
  },
  
  isAuthenticated: (): boolean => {
    return getStoredTokens() !== null;
  },
};

// Challenges API
export const challengesApi = {
  list: async (params?: {
    status?: string;
    type?: string;
    page?: number;
  }): Promise<PaginatedResponse<Challenge>> => {
    const response = await apiClient.get<PaginatedResponse<Challenge>>('/challenges/', { params });
    return response.data;
  },
  
  get: async (id: number): Promise<Challenge> => {
    const response = await apiClient.get<Challenge>(`/challenges/${id}/`);
    return response.data;
  },
  
  create: async (data: ChallengeCreateData): Promise<Challenge> => {
    const response = await apiClient.post<Challenge>('/challenges/', data);
    return response.data;
  },
  
  update: async (id: number, data: Partial<ChallengeCreateData>): Promise<Challenge> => {
    const response = await apiClient.patch<Challenge>(`/challenges/${id}/`, data);
    return response.data;
  },
  
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/challenges/${id}/`);
  },
  
  join: async (id: number): Promise<ChallengeParticipant> => {
    const response = await apiClient.post<ChallengeParticipant>(`/challenges/${id}/join/`);
    return response.data;
  },
  
  leave: async (id: number): Promise<void> => {
    await apiClient.post(`/challenges/${id}/leave/`);
  },
  
  leaderboard: async (id: number): Promise<ChallengeParticipant[]> => {
    const response = await apiClient.get<ChallengeParticipant[]>(`/challenges/${id}/leaderboard/`);
    return response.data;
  },
};

// Contributions API
export const contributionsApi = {
  list: async (challengeId?: number): Promise<PaginatedResponse<Contribution>> => {
    const params = challengeId ? { challenge: challengeId } : undefined;
    const response = await apiClient.get<PaginatedResponse<Contribution>>('/contributions/', { params });
    return response.data;
  },
  
  create: async (data: ContributionCreateData): Promise<Contribution> => {
    const response = await apiClient.post<Contribution>('/contributions/', data);
    return response.data;
  },
  
  get: async (id: number): Promise<Contribution> => {
    const response = await apiClient.get<Contribution>(`/contributions/${id}/`);
    return response.data;
  },
};

// Proofs API
export const proofsApi = {
  submit: async (contributionId: number, data: FormData): Promise<Proof> => {
    data.append('contribution_id', contributionId.toString());
    const response = await apiClient.post<Proof>('/proofs/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  review: async (proofId: number, verdict: 'approved' | 'rejected', comment?: string): Promise<Proof> => {
    const response = await apiClient.post<Proof>(`/proofs/${proofId}/review/`, {
      verdict,
      comment,
    });
    return response.data;
  },
};

// Teams API
export const teamsApi = {
  list: async (): Promise<PaginatedResponse<Team>> => {
    const response = await apiClient.get<PaginatedResponse<Team>>('/teams/');
    return response.data;
  },
  
  get: async (id: number): Promise<Team> => {
    const response = await apiClient.get<Team>(`/teams/${id}/`);
    return response.data;
  },
  
  create: async (data: Partial<Team>): Promise<Team> => {
    const response = await apiClient.post<Team>('/teams/', data);
    return response.data;
  },
  
  join: async (id: number): Promise<void> => {
    await apiClient.post(`/teams/${id}/join/`);
  },
  
  leave: async (id: number): Promise<void> => {
    await apiClient.post(`/teams/${id}/leave/`);
  },
};

// Duels API
export const duelsApi = {
  list: async (): Promise<PaginatedResponse<Duel>> => {
    const response = await apiClient.get<PaginatedResponse<Duel>>('/duels/');
    return response.data;
  },
  
  get: async (id: number): Promise<Duel> => {
    const response = await apiClient.get<Duel>(`/duels/${id}/`);
    return response.data;
  },
  
  accept: async (id: number): Promise<Duel> => {
    const response = await apiClient.post<Duel>(`/duels/${id}/accept/`);
    return response.data;
  },
  
  decline: async (id: number): Promise<void> => {
    await apiClient.post(`/duels/${id}/decline/`);
  },
};

// Export error handler
export { handleApiError };

// Export axios instance for custom requests
export default apiClient;
