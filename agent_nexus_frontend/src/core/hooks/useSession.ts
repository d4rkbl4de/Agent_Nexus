import { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import { ChatSession, ChatMessage, ChatInput, ChatResponse, StreamingUpdate } from '../../contracts/chat.schema';
import { request } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';
import { AgentNexusError, mapApiError } from '../api/errors';
import { ListRequest, PaginatedListResponse } from '../../contracts/shared/pagination';

export interface UseSessionResult {
  session: ChatSession | null;
  messages: ChatMessage[];
  sessions: ChatSession[] | null;
  loading: boolean;
  error: AgentNexusError | null;
  isStreaming: boolean;
  
  fetchSessions: (agentId: string, params?: ListRequest) => Promise<PaginatedListResponse<ChatSession> | undefined>;
  fetchSession: (sessionId: string) => Promise<void>;
  createSession: (agentId: string) => Promise<ChatSession | undefined>;
  sendMessage: (input: ChatInput) => Promise<ChatResponse | undefined>;
  connectStreaming: (sessionId: string) => void;
  disconnectStreaming: () => void;
}

const useSession = (): UseSessionResult => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessions, setSessions] = useState<ChatSession[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<AgentNexusError | null>(null);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  
  const wsRef = useRef<WebSocket | null>(null);

  const clearState = () => {
    setError(null);
    setLoading(true);
  };

  const handleError = (e: any): AgentNexusError => {
    const apiError = e.toApiError ? e.toApiError() : { message: e.message || 'An unknown error occurred.', error_code: 'CLIENT_UNKNOWN', timestamp: new Date().toISOString() };
    const mappedError = mapApiError(e.response?.status || 500, apiError);
    setError(mappedError);
    setLoading(false);
    return mappedError;
  };

  const fetchSessions = useCallback(async (agentId: string, params: ListRequest = {}) => {
    clearState();
    try {
      const endpoint = API_ENDPOINTS.CHAT.LIST_SESSIONS(agentId);
      const data = await request<PaginatedListResponse<ChatSession>>({ 
        url: endpoint, 
        method: 'GET',
        params: params,
      });
      setSessions(data.items);
      return data;
    } catch (e) {
      handleError(e);
      setSessions(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSession = useCallback(async (sessionId: string) => {
    clearState();
    try {
      const endpoint = API_ENDPOINTS.CHAT.GET_SESSION(sessionId);
      const data = await request<ChatSession & { messages: ChatMessage[] }>({ url: endpoint, method: 'GET' });
      setSession(data);
      setMessages(data.messages || []);
    } catch (e) {
      handleError(e);
      setSession(null);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const createSession = useCallback(async (agentId: string) => {
    clearState();
    try {
      const endpoint = API_ENDPOINTS.CHAT.CREATE_SESSION(agentId);
      const newSession = await request<ChatSession>({
        url: endpoint,
        method: 'POST',
        data: {}, // Initial session creation may not require data
      });
      setSession(newSession);
      setMessages([]);
      return newSession;
    } catch (e) {
      handleError(e);
    } finally {
      setLoading(false);
    }
  }, []);
  
  const sendMessage = useCallback(async (input: ChatInput) => {
    clearState();
    
    // Add the user message immediately to the local state
    const userMessage: ChatMessage = {
        id: `local-${Date.now()}`,
        session_id: input.session_id,
        author: 'user',
        timestamp: new Date().toISOString(),
        content: input.prompt,
        status: 'sending',
    };
    setMessages(prev => [...prev, userMessage]);
    setLoading(false); // Don't block UI with API loading indicator for chat send

    try {
      const response = await request<ChatResponse>({
        url: API_ENDPOINTS.CHAT.SEND_MESSAGE(input.session_id),
        method: 'POST',
        data: input,
      });
      
      // Replace the local user message with the confirmed one
      setMessages(prev => prev.map(msg => msg.id === userMessage.id ? { ...response.message, status: 'received' } : msg));
      
      // Start a pending agent message to be filled by the stream
      const pendingAgentMessage: ChatMessage = {
          id: `${response.task_id}-agent`,
          session_id: input.session_id,
          author: 'agent',
          timestamp: new Date().toISOString(),
          content: '', // Empty content will be filled by stream
          status: 'sending',
          task_id: response.task_id,
      };
      setMessages(prev => [...prev, pendingAgentMessage]);

      // Automatically connect to the stream after sending the message
      connectStreaming(input.session_id);

      return response;
    } catch (e) {
      handleError(e);
      // Mark local user message as error on failure
      setMessages(prev => prev.map(msg => msg.id === userMessage.id ? { ...msg, status: 'error', content: `${msg.content} (Failed to Send)` } : msg));
    }
  }, []);

  const processStreamingUpdate = useCallback((update: StreamingUpdate) => {
    if (update.type === 'message_update' && update.message_chunk) {
        setMessages(prev => {
            const index = prev.findIndex(msg => msg.id === update.message_chunk!.message_id);
            if (index !== -1) {
                const newMessages = [...prev];
                const targetMessage = newMessages[index];
                
                // Append delta content
                targetMessage.content += update.message_chunk!.content_delta || '';
                
                // Update status if provided
                if (update.message_chunk!.status) {
                    targetMessage.status = update.message_chunk!.status;
                }
                return newMessages;
            }
            return prev;
        });
    } else if (update.type === 'end') {
        setIsStreaming(false);
    } else if (update.type === 'error') {
        setIsStreaming(false);
        setError(new AgentNexusError({
            error_code: update.error?.code || 'STREAM_ERROR',
            message: update.error?.message || 'A streaming error occurred.',
            timestamp: new Date().toISOString(),
            details: update.error,
        }));
    }
  }, []);

  const connectStreaming = useCallback((sessionId: string) => {
    if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
    }
    
    // Use window.location.host for relative pathing, assuming WebSocket is served on the same host/port
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}${API_ENDPOINTS.CHAT.STREAM_SESSION(sessionId)}`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    
    ws.onopen = () => {
        setIsStreaming(true);
        setError(null);
    };

    ws.onmessage = (event) => {
        try {
            const update: StreamingUpdate = JSON.parse(event.data);
            processStreamingUpdate(update);
        } catch (e) {
            console.error("Failed to parse streaming data:", e);
        }
    };

    ws.onerror = (e) => {
        console.error("WebSocket error:", e);
        setIsStreaming(false);
        setError(new AgentNexusError({
            error_code: 'WS_CONNECTION_ERROR',
            message: 'WebSocket connection failed or closed unexpectedly.',
            timestamp: new Date().toISOString(),
        }));
    };

    ws.onclose = () => {
        setIsStreaming(false);
    };
    
  }, [processStreamingUpdate]);

  const disconnectStreaming = useCallback(() => {
    if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
    }
    setIsStreaming(false);
  }, []);
  
  useEffect(() => {
      // Cleanup WebSocket connection when component unmounts
      return () => {
          disconnectStreaming();
      };
  }, [disconnectStreaming]);


  return useMemo(() => ({
    session,
    messages,
    sessions,
    loading,
    error,
    isStreaming,
    fetchSessions,
    fetchSession,
    createSession,
    sendMessage,
    connectStreaming,
    disconnectStreaming,
  }), [
    session, 
    messages, 
    sessions, 
    loading, 
    error, 
    isStreaming,
    fetchSessions, 
    fetchSession, 
    createSession, 
    sendMessage,
    connectStreaming,
    disconnectStreaming,
  ]);
};

export default useSession;