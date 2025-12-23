'use client';

import React, { useEffect } from 'react';
import { initWebSocket } from '../api-client/websocket.client';

interface CoreProviderProps {
  children: React.ReactNode;
}

export const CoreProvider: React.FC<CoreProviderProps> = ({ children }) => {
  
  useEffect(() => {
    if (typeof window !== 'undefined') {
      console.log("[Core] Initializing WebSocket client...");
      initWebSocket();
    }
    return () => {
    };
  }, []);

  return <>{children}</>;
};