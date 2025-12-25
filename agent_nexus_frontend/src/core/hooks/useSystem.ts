import { useState, useCallback, useMemo } from 'react';
import { request } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';
import { AgentNexusError, mapApiError } from '../api/errors';
import {
  MetricData,
  ResourceUsageSummary,
  AgentInsight,
  TimePeriod,
  PerformanceBenchmark,
} from '../../contracts/insight.schema';
import { SuccessResponse } from '../../contracts/shared/meta';
import { PlatformUser, RolePermissions } from '../../contracts/user.schema';

export interface DashboardMetrics {
  totalAgents: MetricData;
  successRate: MetricData;
  totalCost: MetricData;
  averageLatency: MetricData;
}

export interface UseSystemResult {
  dashboard: DashboardMetrics | null;
  insights: AgentInsight[] | null;
  usageSummary: ResourceUsageSummary | null;
  permissions: RolePermissions | null;
  userProfile: PlatformUser | null;
  loading: boolean;
  error: AgentNexusError | null;

  fetchDashboardMetrics: () => Promise<void>;
  fetchAgentInsights: (agentId?: string) => Promise<void>;
  fetchResourceUsage: (period: TimePeriod) => Promise<void>;
  fetchUserPermissions: (role: PlatformUser['role']) => Promise<void>;
  fetchUserProfile: () => Promise<void>;
  getSystemHealth: () => Promise<SuccessResponse | undefined>;
  getAgentBenchmark: (agentId: string) => Promise<PerformanceBenchmark | undefined>;
}

export const useSystem = (): UseSystemResult => {
  const [dashboard, setDashboard] = useState<DashboardMetrics | null>(null);
  const [insights, setInsights] = useState<AgentInsight[] | null>(null);
  const [usageSummary, setUsageSummary] = useState<ResourceUsageSummary | null>(null);
  const [permissions, setPermissions] = useState<RolePermissions | null>(null);
  const [userProfile, setUserProfile] = useState<PlatformUser | null>(null);
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

  const fetchDashboardMetrics = useCallback(async () => {
    clearState();
    try {
      const data = await request<DashboardMetrics>({
        url: API_ENDPOINTS.PERFORMANCE.GET_DASHBOARD,
        method: 'GET',
      });
      setDashboard(data);
    } catch (e) {
      handleError(e);
      setDashboard(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchAgentInsights = useCallback(async (agentId?: string) => {
    clearState();
    try {
      const data = await request<AgentInsight[]>({
        url: API_ENDPOINTS.PERFORMANCE.GET_INSIGHTS,
        method: 'GET',
        params: agentId ? { agent_id: agentId } : {},
      });
      setInsights(data);
    } catch (e) {
      handleError(e);
      setInsights(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchResourceUsage = useCallback(async (period: TimePeriod = 'day') => {
    clearState();
    try {
      const data = await request<ResourceUsageSummary>({
        url: API_ENDPOINTS.PERFORMANCE.GET_RESOURCE_USAGE,
        method: 'GET',
        params: { period },
      });
      setUsageSummary(data);
    } catch (e) {
      handleError(e);
      setUsageSummary(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = useCallback(async () => {
    clearState();
    try {
      const data = await request<PlatformUser>({
        url: API_ENDPOINTS.AUTH.GET_PROFILE,
        method: 'GET',
      });
      setUserProfile(data);
    } catch (e) {
      handleError(e);
      setUserProfile(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchUserPermissions = useCallback(async (role: PlatformUser['role']) => {
    // This is typically a static or client-side derived fetch,
    // but assuming an API endpoint for comprehensive permissions
    clearState();
    try {
      const data = await request<RolePermissions>({
        url: `/system/permissions/${role}`,
        method: 'GET',
      });
      setPermissions(data);
    } catch (e) {
      handleError(e);
      setPermissions(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const getSystemHealth = useCallback(async () => {
    clearState();
    setLoading(false); // Health check should be quick and not block
    try {
      const data = await request<SuccessResponse>({
        url: '/system/health',
        method: 'GET',
      });
      return data;
    } catch (e) {
      handleError(e);
    }
  }, []);

  const getAgentBenchmark = useCallback(async (agentId: string) => {
    clearState();
    try {
      const data = await request<PerformanceBenchmark>({
        url: API_ENDPOINTS.PERFORMANCE.GET_METRIC(`benchmark/${agentId}`),
        method: 'GET',
      });
      return data;
    } catch (e) {
      handleError(e);
    } finally {
      setLoading(false);
    }
  }, []);

  return useMemo(() => ({
    dashboard,
    insights,
    usageSummary,
    permissions,
    userProfile,
    loading,
    error,
    fetchDashboardMetrics,
    fetchAgentInsights,
    fetchResourceUsage,
    fetchUserPermissions,
    fetchUserProfile,
    getSystemHealth,
    getAgentBenchmark,
  }), [
    dashboard,
    insights,
    usageSummary,
    permissions,
    userProfile,
    loading,
    error,
    fetchDashboardMetrics,
    fetchAgentInsights,
    fetchResourceUsage,
    fetchUserPermissions,
    fetchUserProfile,
    getSystemHealth,
    getAgentBenchmark,
  ]);
};