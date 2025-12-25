import { create } from 'zustand';
import { TimePeriod, ResourceUsageSummary, AgentInsight, PerformanceBenchmark } from '../../contracts/insight.schema';
import { DashboardMetrics } from '../hooks/useSystem';
import { eventBus } from '../mediator/eventBus';
import { PlatformUser, RolePermissions } from '../../contracts/user.schema';

export interface SystemStore {
  dashboard: DashboardMetrics | null;
  insights: AgentInsight[] | null;
  resourceUsage: ResourceUsageSummary | null;
  activeUserPermissions: RolePermissions | null;
  
  loadingDashboard: boolean;
  loadingInsights: boolean;
  loadingUsage: boolean;
  
  setDashboard: (dashboard: DashboardMetrics | null) => void;
  setLoadingDashboard: (loading: boolean) => void;
  
  setInsights: (insights: AgentInsight[] | null) => void;
  setLoadingInsights: (loading: boolean) => void;
  
  setResourceUsage: (usage: ResourceUsageSummary | null) => void;
  setLoadingUsage: (loading: boolean) => void;

  setActiveUserPermissions: (permissions: RolePermissions | null) => void;
}

export const useSystemStore = create<SystemStore>((set) => ({
  dashboard: null,
  insights: null,
  resourceUsage: null,
  activeUserPermissions: null,
  
  loadingDashboard: false,
  loadingInsights: false,
  loadingUsage: false,

  setDashboard: (dashboard) => set({ dashboard, loadingDashboard: false }),
  setLoadingDashboard: (loading) => set({ loadingDashboard: loading }),
  
  setInsights: (insights) => set({ insights, loadingInsights: false }),
  setLoadingInsights: (loading) => set({ loadingInsights: loading }),
  
  setResourceUsage: (usage) => set({ resourceUsage: usage, loadingUsage: false }),
  setLoadingUsage: (loading) => set({ loadingUsage: loading }),

  setActiveUserPermissions: (permissions) => set({ activeUserPermissions: permissions }),
}));

const initializeEventBusListeners = () => {
    const { setActiveUserPermissions } = useSystemStore.getState();

    eventBus.subscribe('user:loggedOut', () => {
        setActiveUserPermissions(null);
    });
    
    eventBus.subscribe('user:loggedIn', (user: PlatformUser) => {
        console.log(`User logged in. Permissions for role ${user.role} should be loaded.`);
    });
    
    eventBus.subscribe('user:profileUpdated', (user: PlatformUser) => {
        console.log(`User profile updated. Check if permissions for role ${user.role} need updating.`);
    });
};

initializeEventBusListeners();

export const useDashboardData = () => useSystemStore(state => ({
    dashboard: state.dashboard,
    loading: state.loadingDashboard,
}));

export const useInsightsData = () => useSystemStore(state => ({
    insights: state.insights,
    loading: state.loadingInsights,
}));

export const useResourceUsageData = () => useSystemStore(state => ({
    resourceUsage: state.resourceUsage,
    loading: state.loadingUsage,
}));

export const useUserPermissions = () => useSystemStore(state => state.activeUserPermissions);