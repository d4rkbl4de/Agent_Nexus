import React, { createContext, useContext, useEffect, useState, useMemo, useCallback } from 'react';
import { AuthSession, PlatformUser, LoginCredentials, RegisterCredentials } from '../../contracts/user.schema';
import { auth, request } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';
import { AgentNexusError, mapApiError, AuthenticationError } from '../api/errors';
import { eventBus } from '../mediator/eventBus';

export interface SessionContextType {
  session: AuthSession | null;
  user: PlatformUser | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: AgentNexusError | null;
  
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
  refetchUserProfile: () => Promise<void>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

const useSessionState = () => {
  const [session, setSession] = useState<AuthSession | null>(auth.getSession());
  const [user, setUser] = useState<PlatformUser | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<AgentNexusError | null>(null);

  const isAuthenticated = useMemo(() => !!session?.token, [session]);

  const handleError = useCallback((e: any): AgentNexusError => {
    const apiError = e.toApiError ? e.toApiError() : { message: e.message || 'An unknown error occurred.', error_code: 'CLIENT_UNKNOWN', timestamp: new Date().toISOString() };
    const mappedError = mapApiError(e.response?.status || 500, apiError);
    setError(mappedError);
    setLoading(false);
    return mappedError;
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    setLoading(true);
    setError(null);
    try {
      const authSession = await request<AuthSession>({
        url: API_ENDPOINTS.AUTH.LOGIN,
        method: 'POST',
        data: credentials,
      });
      auth.setSession(authSession);
      setSession(authSession);
      await refetchUserProfile();
      eventBus.publish('user:loggedIn', user!); 
    } catch (e) {
      auth.clearSession();
      setSession(null);
      setUser(null);
      handleError(e);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [handleError, user]);

  const register = useCallback(async (credentials: RegisterCredentials) => {
    setLoading(true);
    setError(null);
    try {
      const newUser = await request<PlatformUser>({
        url: API_ENDPOINTS.AUTH.REGISTER,
        method: 'POST',
        data: credentials,
      });
      
      const loginCredentials = { email: credentials.email, password: credentials.password };
      await login(loginCredentials);

    } catch (e) {
      handleError(e);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [handleError, login]);

  const logout = useCallback(() => {
    setLoading(true);
    setError(null);
    try {
      request<void>({ url: API_ENDPOINTS.AUTH.LOGOUT, method: 'POST' });
    } catch (e) {
      console.warn('Backend logout failed but client session cleared.', e);
    } finally {
      auth.clearSession();
      setSession(null);
      setUser(null);
      setLoading(false);
      eventBus.publish('user:loggedOut', undefined);
    }
  }, []);
  
  const refetchUserProfile = useCallback(async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    setError(null);
    try {
      const userProfile = await request<PlatformUser>({
        url: API_ENDPOINTS.AUTH.GET_PROFILE,
        method: 'GET',
      });
      setUser(userProfile);
      eventBus.publish('user:profileUpdated', userProfile);
    } catch (e) {
      if (e instanceof AuthenticationError || e.toApiError()?.error_code === 'UNAUTHORIZED') {
        logout();
      } else {
        handleError(e);
      }
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, handleError, logout]);

  useEffect(() => {
    if (session) {
      refetchUserProfile();
    } else {
      setLoading(false);
    }
  }, [session, refetchUserProfile]);
  
  useEffect(() => {
      const unsubscribe = eventBus.subscribe('user:loggedOut', () => {
          if (session) {
              setSession(null);
              setUser(null);
              auth.clearSession();
          }
      });
      return () => unsubscribe();
  }, [session]);


  const value = useMemo(() => ({
    session,
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    refetchUserProfile,
  }), [
    session,
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    refetchUserProfile,
  ]);

  return value;
};


interface SessionProviderProps {
  children: React.ReactNode;
}

export const SessionProvider: React.FC<SessionProviderProps> = ({ children }) => {
  const sessionState = useSessionState();

  return (
    <SessionContext.Provider value={sessionState}>
      {sessionState.loading ? null : children}
    </SessionContext.Provider>
  );
};

export const useSession = (): SessionContextType => {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};