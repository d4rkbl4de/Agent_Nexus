import { Shell } from '@/shell/shell';
import { PageHeader, PageTitle, PageDescription } from '@/shell/page-header';
import { AgentStatusDashboard } from '@/dashboards/agent-status-dashboard';
import { SystemHealthMonitor } from '@/dashboards/system-health-monitor';
import { TaskQueueVisualizer } from '@/visualization/task-queue-visualizer';
import { LogStreamer } from '@/introspection/log-streamer';
import { Suspense } from 'react';
import { Skeleton } from '@/design-system/skeleton';

export default function SystemDashboardPage() {
  return (
    <Shell>
      <PageHeader>
        <PageTitle>System Nexus Status</PageTitle>
        <PageDescription>
          Real-time, granular view of the distributed agent network and core infrastructure health.
        </PageDescription>
      </PageHeader>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-8">
        <div className="md:col-span-3 lg:col-span-3">
          <AgentStatusDashboard />
        </div>
        <div className="md:col-span-1 lg:col-span-1">
          <Suspense fallback={<Skeleton className="h-[300px]" />}>
            <SystemHealthMonitor />
          </Suspense>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Suspense fallback={<Skeleton className="h-[400px]" />}>
            <TaskQueueVisualizer title="Task Queue & Throughput" />
          </Suspense>
        </div>
        <div className="lg:col-span-1">
          <Suspense fallback={<Skeleton className="h-[400px]" />}>
            <LogStreamer endpoint="/api/v1/system/logs" title="Core System Logs" height="400px" />
          </Suspense>
        </div>
      </div>
    </Shell>
  );
}