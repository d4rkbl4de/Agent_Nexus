import * as React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Clock, TrendingUp, Zap, Server } from 'lucide-react';
import Card from '../../shared/ui/Card';
import Badge from '../../shared/ui/Badge';
import { useScheduler } from '../../motion/performance/scheduler';
import { motion } from 'framer-motion';

export interface LatencyDataPoint {
  period: string; // Time window (e.g., 'Last Hour', 'Day 1')
  avgTaskLatencyMs: number;
  avgApiLatencyMs: number;
  p95TaskLatencyMs: number; // 95th percentile latency
}

interface LatencyPanelProps {
  title: string;
  historicalData: LatencyDataPoint[];
  currentAvgLatencyMs: number;
  p95LatencyMs: number;
  isLoading: boolean;
}

const formatTimeMs = (ms: number): string => {
  if (ms < 1000) return `${ms.toFixed(1)}ms`;
  const seconds = ms / 1000;
  if (seconds < 60) return `${seconds.toFixed(2)}s`;
  const minutes = seconds / 60;
  return `${minutes.toFixed(2)}m`;
};

const SummaryMetric: React.FC<{ icon: React.ReactNode; label: string; value: string; color: string }> = ({ icon, label, value, color }) => (
  <Card className="p-4 flex items-center shadow-md">
    <div className={`p-3 rounded-full ${color} mr-4`}>
      {icon}
    </div>
    <div>
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className="text-xl font-bold text-gray-900">{value}</p>
    </div>
  </Card>
);

const CustomChartTooltip: React.FC<any> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="p-3 bg-white border border-gray-300 shadow-lg rounded-lg text-sm font-mono">
        <p className="font-bold text-gray-800 mb-1">{label}</p>
        {payload.map((p: any, index: number) => (
          <p key={index} className={`text-${p.color}-600`}>
            {`${p.name}: ${formatTimeMs(p.value)}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const LatencyPanel: React.FC<LatencyPanelProps> = ({
  title,
  historicalData,
  currentAvgLatencyMs,
  p95LatencyMs,
  isLoading,
}) => {
  const { canRunAnimation } = useScheduler();
  
  const formattedAvgLatency = formatTimeMs(currentAvgLatencyMs);
  const formattedP95Latency = formatTimeMs(p95LatencyMs);
  
  const motionProps = canRunAnimation() ? {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5 },
  } : {
    initial: false,
    animate: { opacity: 1 },
    transition: { duration: 0.1 },
  };

  return (
    <Card className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
        <Badge variant="secondary" className="text-sm">Time in ms/s</Badge>
      </div>

      {/* Summary Metrics */}
      <motion.div className="grid grid-cols-1 md:grid-cols-2 gap-4" {...motionProps}>
        <SummaryMetric
          icon={<Clock className="w-6 h-6 text-white" />}
          label="Current Avg Task Latency"
          value={isLoading ? '...' : formattedAvgLatency}
          color="bg-indigo-500"
        />
        <SummaryMetric
          icon={<TrendingUp className="w-6 h-6 text-white" />}
          label="P95 Task Latency"
          value={isLoading ? '...' : formattedP95Latency}
          color="bg-red-500"
        />
      </motion.div>

      {/* Historical Chart */}
      <motion.div className="h-80 w-full" {...motionProps}>
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Historical Latency Distribution</h3>
        {isLoading && historicalData.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 border border-dashed rounded-lg">
            <Loader className="w-6 h-6 mr-2 animate-spin"/> Loading chart data...
          </div>
        ) : historicalData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={historicalData}
              margin={{ top: 5, right: 20, left: -10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" vertical={false} />
              <XAxis dataKey="period" stroke="#718096" tickLine={false} axisLine={false} />
              <YAxis 
                stroke="#718096" 
                tickFormatter={formatTimeMs} 
                domain={['auto', 'auto']}
              />
              <Tooltip content={<CustomChartTooltip />} />
              
              <Bar dataKey="avgTaskLatencyMs" name="Avg Task Latency" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              <Bar dataKey="p95TaskLatencyMs" name="P95 Task Latency" fill="#ef4444" radius={[4, 4, 0, 0]} />
              <Bar dataKey="avgApiLatencyMs" name="Avg API Latency" fill="#34d399" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500 border border-dashed rounded-lg">
            No historical latency data available.
          </div>
        )}
      </motion.div>
    </Card>
  );
};

export default LatencyPanel;
