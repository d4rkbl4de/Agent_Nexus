'use client';

import React, { useEffect } from 'react';
import { WebSocketClient } from '@/core/api-client/websocket.client';

interface CoreProviderProps {
  children: React.ReactNode;
}

export const CoreProvider: React.FC<CoreProviderProps> = ({ children }) => {
  useEffect(() => {
    const wsClient = new WebSocketClient();
    return () => {
      wsClient.close();
    };
  }, []);

  return <>{children}</>;
};
