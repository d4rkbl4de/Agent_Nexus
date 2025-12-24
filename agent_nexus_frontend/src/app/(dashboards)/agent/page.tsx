'use client';

import { Shell } from '@/shell/shell';
import { PageHeader, PageTitle, PageDescription } from '@/shell/page-header';
import { AgentControlPanel } from '@/lobes/agent-control-panel';
import { AgentConfigurationForm } from '@/lobes/agent-configuration-form';
import { AgentChatInterface } from '@/shell/agent-chat-interface';
import { AgentTaskMonitor } from '@/introspection/agent-task-monitor';
import { AgentProvider } from '@/core/context/agent-context';
import { Suspense, useState } from 'react';
import { Skeleton } from '@/design-system/skeleton';

export default function AgentInterfacePage() {
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

  const handleAgentSelect = (agentId: string) => {
    setSelectedAgentId(agentId);
  };

  return (
    <Shell>
      <PageHeader>
        <PageTitle>Agent Control Matrix</PageTitle>
        <PageDescription>
          Direct interaction and parameter tuning for autonomous agents. Select an agent to begin real-time command execution and monitoring.
        </PageDescription>
      </PageHeader>

      <AgentProvider agentId={selectedAgentId}>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Column 1: Agent Selection and Configuration */}
          <div className="lg:col-span-1 space-y-6">
            <Suspense fallback={<Skeleton className="h-[200px]" />}>
              <AgentControlPanel onSelectAgent={handleAgentSelect} selectedAgentId={selectedAgentId} />
            </Suspense>
            {selectedAgentId && (
              <Suspense fallback={<Skeleton className="h-[400px]" />}>
                <AgentConfigurationForm agentId={selectedAgentId} />
              </Suspense>
            )}
          </div>

          {/* Column 2 & 3: Chat Interface and Real-time Output */}
          <div className="lg:col-span-3 space-y-6">
            <Suspense fallback={<Skeleton className="h-[600px]" />}>
              <AgentChatInterface agentId={selectedAgentId} />
            </Suspense>
            
            {/* Real-time Task Monitoring/Tool-use Visualization */}
            {selectedAgentId && (
              <Suspense fallback={<Skeleton className="h-[250px]" />}>
                <AgentTaskMonitor agentId={selectedAgentId} title="Agent Execution Trace" />
              </Suspense>
            )}
          </div>
        </div>
      </AgentProvider>
    </Shell>
  );
}