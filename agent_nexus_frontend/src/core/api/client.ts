import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { AuthSession } from '../../contracts/user.schema';
import { ApiError } from '../../contracts/shared/meta';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1';

let currentSession: AuthSession | null = null;

const setSession = (session: AuthSession | null) => {
  currentSession = session;
  if (session) {
    localStorage.setItem('agentNexusAuth', JSON.stringify(session));
  } else {
    localStorage.removeItem('agentNexusAuth');
  }
};

const getSession = (): AuthSession | null => {
  if (currentSession) return currentSession;
  const storedSession = localStorage.getItem('agentNexusAuth');
  if (storedSession) {
    try {
      const session = JSON.parse(storedSession) as AuthSession;
      currentSession = session;
      return session;
    } catch (e) {
      localStorage.removeItem('agentNexusAuth');
      return null;
    }
  }
  return null;
};

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const session = getSession();
    if (session && session.token) {
      // @ts-ignore
      config.headers.Authorization = `Bearer ${session.token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    if (error.response && error.response.status === 401) {
        
        // TODO: Implement Token Refresh Logic
        
        if (originalRequest && originalRequest.url !== '/auth/login') {
            setSession(null);
            console.warn("Authentication failed, session cleared.");
        }
    }

    const apiError: ApiError = {
      error_code: error.code || 'UNKNOWN_ERROR',
      message: error.message || 'An unexpected network error occurred.',
      timestamp: new Date().toISOString(),
      details: error.response?.data,
    };
    
    return Promise.reject(apiError);
  }
);

export const request = async <T = any>(config: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.request<T>(config);
  return response.data;
};

export const auth = {
  setSession,
  getSession,
  clearSession: () => setSession(null),
};

export default apiClient;