import {
  QueryClient,
  QueryClientProvider,
  MutationCache,
  QueryCache,
  onlineManager,
  focusManager,
} from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import React, { useMemo, useEffect, useState } from 'react';
import { eventBus } from '../mediator/eventBus';
import { isAgentNexusError } from '../api/errors';
import { auth } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';

const QUERY_STALE_TIME_MS = 1000 * 60 * 5;
const QUERY_CACHE_TIME_MS = 1000 * 60 * 15;

const errorHandler = (error: unknown) => {
  if (isAgentNexusError(error)) {
    eventBus.publish('system:error', {
      code: error.code,
      message: error.message,
      details: error.details,
    });
    
    if (error.code === 'UNAUTHORIZED' && error.details?.url !== API_ENDPOINTS.AUTH.LOGIN) {
      auth.clearSession();
      eventBus.publish('user:loggedOut', undefined);
      eventBus.publish('system:notification', {
        message: 'Your session expired. Please log in again.',
        type: 'warning',
      });
    }
  } else {
    eventBus.publish('system:error', {
      code: 'REACT_QUERY_ERROR',
      message: (error as Error).message || 'An unknown data fetching error occurred.',
    });
  }
};

function useOnlineStatusSync() {
  const [isOnline, setIsOnline] = useState(onlineManager.isOnline());

  useEffect(() => {
    const unsubscribe = onlineManager.subscribe(status => {
      setIsOnline(status);
      if (status) {
        eventBus.publish('system:notification', { message: 'Reconnected to server.', type: 'info' });
      } else {
        eventBus.publish('system:notification', { message: 'Network offline. Check your connection.', type: 'warning' });
      }
    });
    return () => unsubscribe();
  }, []);
  
  return isOnline;
}

function useFocusStatusSync() {
  useEffect(() => {
    const handleVisibilityChange = () => {
      focusManager.setFocused(document.visibilityState === 'visible');
      if (document.visibilityState === 'visible') {
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);
}

interface QueryProviderProps {
  children: React.ReactNode;
}

export const QueryProvider: React.FC<QueryProviderProps> = ({ children }) => {
  useOnlineStatusSync();
  useFocusStatusSync();

  const queryClient = useMemo(() => new QueryClient({
    queryCache: new QueryCache({
      onError: errorHandler,
    }),
    mutationCache: new MutationCache({
      onError: errorHandler,
    }),
    defaultOptions: {
      queries: {
        staleTime: QUERY_STALE_TIME_MS,
        cacheTime: QUERY_CACHE_TIME_MS,
        retry: 2,
        refetchOnWindowFocus: true,
        refetchOnMount: false,
      },
      mutations: {
        retry: false,
      }
    },
  }), []);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};