import { useState, useCallback, useMemo } from 'react';
import { Agent, AgentConfiguration, AgentCreation, AgentStatus, DeploymentStatus } from '../../contracts/agent.schema';
import { request } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';
import { AgentNexusError, mapApiError } from '../api/errors';
import { ListRequest, PaginatedListResponse } from '../../contracts/shared/pagination';

export interface UseAgentResult {
  agent: Agent | null;
  agents: Agent[] | null;
  loading: boolean;
  error: AgentNexusError | null;
  
  fetchAgent: (id: string) => Promise<void>;
  fetchAgents: (params?: ListRequest) => Promise<PaginatedListResponse<Agent> | undefined>;
  createAgent: (data: AgentCreation) => Promise<Agent | undefined>;
  updateAgent: (id: string, config: Partial<AgentConfiguration>) => Promise<Agent | undefined>;
  deleteAgent: (id: string) => Promise<void>;
  deployAgent: (id: string) => Promise<DeploymentStatus | undefined>;
  updateAgentStatus: (id: string, status: AgentStatus) => Promise<void>;
}

export const useAgent = (): UseAgentResult => {
  const [agent, setAgent] = useState<Agent | null>(null);
  const [agents, setAgents] = useState<Agent[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<AgentNexusError | null>(null);

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

  const fetchAgent = useCallback(async (id: string) => {
    clearState();
    try {
      const endpoint = API_ENDPOINTS.AGENTS.GET(id);
      const data = await request<Agent>({ url: endpoint, method: 'GET' });
      setAgent(data);
    } catch (e) {
      handleError(e);
      setAgent(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchAgents = useCallback(async (params: ListRequest = {}) => {
    clearState();
    try {
      const data = await request<PaginatedListResponse<Agent>>({ 
        url: API_ENDPOINTS.AGENTS.LIST, 
        method: 'GET',
        params: params,
      });
      setAgents(data.items);
      return data;
    } catch (e) {
      handleError(e);
      setAgents(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const createAgent = useCallback(async (data: AgentCreation) => {
    clearState();
    try {
      const newAgent = await request<Agent>({
        url: API_ENDPOINTS.AGENTS.CREATE,
        method: 'POST',
        data,
      });
      setAgent(newAgent);
      return newAgent;
    } catch (e) {
      handleError(e);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateAgent = useCallback(async (id: string, config: Partial<AgentConfiguration>) => {
    clearState();
    try {
      const updatedAgent = await request<Agent>({
        url: API_ENDPOINTS.AGENTS.CONFIG(id),
        method: 'PUT',
        data: config,
      });
      setAgent(prev => (prev && prev.id === id ? updatedAgent : updatedAgent));
      return updatedAgent;
    } catch (e) {
      handleError(e);
    } finally {
      setLoading(false);
    }
  }, []);
  
  const updateAgentStatus = useCallback(async (id: string, status: AgentStatus) => {
    clearState();
    try {
      // Assuming a specific endpoint or PUT payload for status change
      await request<void>({
        url: API_ENDPOINTS.AGENTS.UPDATE(id),
        method: 'PATCH', 
        data: { status },
      });
      setAgent(prev => {
        if (prev && prev.id === id) {
          return { ...prev, status };
        }
        return prev;
      });
    } catch (e) {
      handleError(e);
    } finally {
      setLoading(false);
    }
  }, []);


  const deleteAgent = useCallback(async (id: string) => {
    clearState();
    try {
      await request<void>({
        url: API_ENDPOINTS.AGENTS.DELETE(id),
        method: 'DELETE',
      });
      setAgent(prev => (prev && prev.id === id ? null : prev));
      setAgents(prev => (prev ? prev.filter(a => a.id !== id) : null));
    } catch (e) {
      handleError(e);
    } finally {
      setLoading(false);
    }
  }, []);

  const deployAgent = useCallback(async (id: string) => {
    clearState();
    try {
      const deploymentStatus = await request<DeploymentStatus>({
        url: API_ENDPOINTS.AGENTS.DEPLOY(id),
        method: 'POST',
      });
      setAgent(prev => {
        if (prev && prev.id === id) {
          return { ...prev, deployment_status: deploymentStatus.status, status: 'live' };
        }
        return prev;
      });
      return deploymentStatus;
    } catch (e) {
      handleError(e);
    } finally {
      setLoading(false);
    }
  }, []);

  return useMemo(() => ({
    agent,
    agents,
    loading,
    error,
    fetchAgent,
    fetchAgents,
    createAgent,
    updateAgent,
    deleteAgent,
    deployAgent,
    updateAgentStatus,
  }), [
    agent, 
    agents, 
    loading, 
    error, 
    fetchAgent, 
    fetchAgents, 
    createAgent, 
    updateAgent, 
    deleteAgent, 
    deployAgent,
    updateAgentStatus
  ]);
};