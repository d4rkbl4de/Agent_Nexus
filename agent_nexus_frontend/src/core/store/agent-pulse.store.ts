import { create } from "zustand"
import { subscribe } from "@/core/mediator/emit"
import { AgentPulse, AgentPulseSchema } from "@/contracts/agent-pulse.schema"

type AgentPulseState = {
  pulses: Map<string, AgentPulse>
  upsert: (pulse: AgentPulse) => void
}

export const useAgentPulseStore = create<AgentPulseState>((set) => ({
  pulses: new Map(),

  upsert: (pulse) =>
    set((state) => {
      const next = new Map(state.pulses)
      next.set(pulse.agentId, pulse)
      return { pulses: next }
    }),
}))

subscribe<'AGENT_STATUS_UPDATE'>("AGENT_STATUS_UPDATE", (pulse) => {
  const validatedPulse = AgentPulseSchema.safeParse(pulse);
  if (validatedPulse.success) {
    useAgentPulseStore.getState().upsert(validatedPulse.data);
  } else {
    console.error("[Store Guard] Malformed Agent Pulse received:", validatedPulse.error);
  }
});

export function useAgentPulseSelector(agentId: string) {
  return useAgentPulseStore((s) => s.pulses.get(agentId))
}