import { create } from 'zustand';
import { Agent, AgentConfiguration, DeploymentStatus } from '../../contracts/agent.schema';
import { eventBus } from '../mediator/eventBus';

export interface AgentStore {
  agents: Agent[];
  selectedAgentId: string | null;
  loading: boolean;
  error: any;

  setLoading: (loading: boolean) => void;
  setError: (error: any) => void;
  
  initializeAgents: (agents: Agent[]) => void;
  selectAgent: (id: string | null) => void;
  
  // CRUD operations
  addAgent: (agent: Agent) => void;
  updateAgent: (id: string, updates: Partial<Agent>) => void;
  deleteAgent: (id: string) => void;
  
  // Specific updates
  updateAgentConfig: (id: string, config: Partial<AgentConfiguration>) => void;
  updateDeploymentStatus: (id: string, status: DeploymentStatus['status']) => void;
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  agents: [],
  selectedAgentId: null,
  loading: false,
  error: null,

  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  
  initializeAgents: (agents) => {
    set({ agents, loading: false, error: null });
  },

  selectAgent: (id) => set({ selectedAgentId: id }),
  
  addAgent: (agent) => {
    set((state) => ({ 
      agents: [...state.agents.filter(a => a.id !== agent.id), agent],
    }));
    eventBus.publish('agent:created', agent);
  },

  updateAgent: (id, updates) => {
    let updatedAgent: Agent | undefined;
    set((state) => ({
      agents: state.agents.map((agent) => {
        if (agent.id === id) {
          updatedAgent = { ...agent, ...updates };
          return updatedAgent;
        }
        return agent;
      }),
    }));
    if (updatedAgent) {
      eventBus.publish('agent:updated', updatedAgent);
    }
  },

  deleteAgent: (id) => {
    set((state) => ({
      agents: state.agents.filter((agent) => agent.id !== id),
      selectedAgentId: state.selectedAgentId === id ? null : state.selectedAgentId,
    }));
    eventBus.publish('agent:deleted', { id });
  },
  
  updateAgentConfig: (id, config) => {
    get().updateAgent(id, { config: { ...get().agents.find(a => a.id === id)?.config, ...config } as AgentConfiguration });
  },
  
  updateDeploymentStatus: (id, status) => {
    get().updateAgent(id, { 
      deployment_status: status, 
      status: status === 'live' ? 'live' : (status === 'failed' ? 'error' : 'offline')
    });
    eventBus.publish('agent:deployed', { id, status });
  },
}));



export const useSelectedAgent = () => {
  const selectedAgentId = useAgentStore((state) => state.selectedAgentId);
  const agents = useAgentStore((state) => state.agents);
  
  return useMemo(() => {
    if (!selectedAgentId) return null;
    return agents.find((a) => a.id === selectedAgentId) || null;
  }, [selectedAgentId, agents]);
};

export const useAgentList = () => useAgentStore((state) => state.agents);