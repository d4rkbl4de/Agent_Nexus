import { Shell } from '@/shell/shell';
import { PageHeader, PageTitle, PageDescription } from '@/shell/page-header';
import { PerformanceMetricsChart } from '@/visualization/performance-metrics-chart';
import { ResourceUtilizationGauge } from '@/visualization/resource-utilization-gauge';
import { AgentLatencyTable } from '@/dashboards/agent-latency-table';
import { ErrorRateMonitor } from '@/introspection/error-rate-monitor';
import { Suspense } from 'react';
import { Skeleton } from '@/design-system/skeleton';
import { Card, CardHeader, CardContent, CardTitle } from '@/design-system/card';

export default function PerformanceDashboardPage() {
  return (
    <Shell>
      <PageHeader>
        <PageTitle>Performance Nexus Monitor</PageTitle>
        <PageDescription>
          Detailed analysis of agent execution metrics, system throughput, and resource efficiency over time.
        </PageDescription>
      </PageHeader>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
        {/* Throughput and Latency Trends */}
        <div className="lg:col-span-3">
          <Suspense fallback={<Skeleton className="h-[400px]" />}>
            <PerformanceMetricsChart title="System Throughput and Latency" />
          </Suspense>
        </div>

        {/* Resource Utilization Gauges */}
        <div className="lg:col-span-1 space-y-6">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Resource Utilization</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Suspense fallback={<Skeleton className="h-24" />}>
                <ResourceUtilizationGauge metric="CPU" percentage={75} />
              </Suspense>
              <Suspense fallback={<Skeleton className="h-24" />}>
                <ResourceUtilizationGauge metric="Memory" percentage={60} />
              </Suspense>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Latency Breakdown Table */}
        <div className="lg:col-span-2">
          <Suspense fallback={<Skeleton className="h-[350px]" />}>
            <AgentLatencyTable title="Agent Response Time Breakdown" />
          </Suspense>
        </div>
        
        {/* Error Rate Monitor */}
        <div className="lg:col-span-1">
          <Suspense fallback={<Skeleton className="h-[350px]" />}>
            <ErrorRateMonitor title="Critical Error Rate" />
          </Suspense>
        </div>
      </div>
    </Shell>
  );
}