import { useAgentPulseStore } from '../core/store/agent-pulse.store';

export const useAgentPulseSelector = (agentId: string) => {
  return useAgentPulseStore(state => state.pulses.get(agentId));
};