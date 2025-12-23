import { z } from "zod"

export const AgentStatusSchema = z.enum([
  "IDLE",
  "INGESTING",
  "ANALYZING",
  "REASONING",
  "COMPLETED",
  "ERROR",
])

export const AgentPulseSchema = z.object({
  agentId: z.string(),
  status: AgentStatusSchema,
  thoughts: z.array(z.string()).optional(),
  confidence: z.number().min(0).max(1).optional(),
  timestamp: z.number(),
})

export type AgentPulse = z.infer<typeof AgentPulseSchema>
export type AgentStatus = AgentPulse["status"]
