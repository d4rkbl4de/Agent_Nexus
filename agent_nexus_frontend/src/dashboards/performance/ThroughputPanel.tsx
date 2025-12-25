import * as React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Zap, Clock, TrendingUp, CheckCircle, XCircle } from 'lucide-react';
import Card from '../../shared/ui/Card';
import Badge from '../../shared/ui/Badge';
import { useScheduler } from '../../motion/performance/scheduler';
import { motion } from 'framer-motion';

export interface ThroughputDataPoint {
  time: string; // Period (e.g., hour, day)
  tasksCompleted: number;
  tasksFailed: number;
  successRate: number; // 0.0 to 1.0
}

interface ThroughputPanelProps {
  title: string;
  historicalData: ThroughputDataPoint[];
  totalTasksCompleted: number;
  currentSuccessRate: number; // Current overall success rate (0-1)
  isLoading: boolean;
}

const formatRate = (rate: number): string => `${(rate * 100).toFixed(1)}%`;

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
    const successRatePayload = payload.find((p: any) => p.dataKey === 'successRate');
    const completedPayload = payload.find((p: any) => p.dataKey === 'tasksCompleted');
    const failedPayload = payload.find((p: any) => p.dataKey === 'tasksFailed');

    return (
      <div className="p-3 bg-white border border-gray-300 shadow-lg rounded-lg text-sm font-mono">
        <p className="font-bold text-gray-800 mb-1">{label}</p>
        {completedPayload && (
          <p className="text-indigo-600">{`${completedPayload.name}: ${completedPayload.value}`}</p>
        )}
        {failedPayload && (
          <p className="text-red-600">{`${failedPayload.name}: ${failedPayload.value}`}</p>
        )}
        {successRatePayload && (
          <p className="text-green-600">{`${successRatePayload.name}: ${formatRate(successRatePayload.value)}`}</p>
        )}
      </div>
    );
  }
  return null;
};

const ThroughputPanel: React.FC<ThroughputPanelProps> = ({
  title,
  historicalData,
  totalTasksCompleted,
  currentSuccessRate,
  isLoading,
}) => {
  const { canRunAnimation } = useScheduler();
  
  const formattedSuccessRate = formatRate(currentSuccessRate);
  
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
        <Badge variant="secondary" className="text-sm">Tasks / Rate</Badge>
      </div>

      {/* Summary Metrics */}
      <motion.div className="grid grid-cols-1 md:grid-cols-2 gap-4" {...motionProps}>
        <SummaryMetric
          icon={<Zap className="w-6 h-6 text-white" />}
          label="Total Tasks Completed"
          value={isLoading ? '...' : totalTasksCompleted.toLocaleString()}
          color="bg-indigo-500"
        />
        <SummaryMetric
          icon={<CheckCircle className="w-6 h-6 text-white" />}
          label="Current Success Rate"
          value={isLoading ? '...' : formattedSuccessRate}
          color={currentSuccessRate >= 0.9 ? 'bg-green-500' : currentSuccessRate >= 0.7 ? 'bg-yellow-500' : 'bg-red-500'}
        />
      </motion.div>

      {/* Historical Chart */}
      <motion.div className="h-80 w-full" {...motionProps}>
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Task Volume and Success Trend</h3>
        {isLoading && historicalData.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 border border-dashed rounded-lg">
            <Clock className="w-6 h-6 mr-2 animate-spin"/> Loading chart data...
          </div>
        ) : historicalData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={historicalData}
              margin={{ top: 10, right: 20, left: -10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" vertical={false} />
              <XAxis dataKey="time" stroke="#718096" tickLine={false} axisLine={false} />
              <YAxis 
                yAxisId="left" 
                stroke="#4f46e5" 
                orientation="left" 
                tickLine={false} 
                axisLine={false} 
                label={{ value: 'Task Count', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#4f46e5' } }}
              />
              <YAxis 
                yAxisId="right" 
                stroke="#10b981" 
                orientation="right" 
                tickLine={false} 
                axisLine={false} 
                tickFormatter={formatRate} 
                domain={[0, 1]}
                label={{ value: 'Success Rate', angle: 90, position: 'insideRight', style: { textAnchor: 'middle', fill: '#10b981' } }}
              />
              <Tooltip content={<CustomChartTooltip />} />
              
              {/* Task Completion Area */}
              <Area 
                yAxisId="left"
                type="monotone" 
                dataKey="tasksCompleted" 
                name="Tasks Completed" 
                stroke="#4f46e5" 
                fill="#4f46e5" 
                fillOpacity={0.3} 
                dot={false}
              />
              {/* Success Rate Line */}
              <Area 
                yAxisId="right"
                type="monotone" 
                dataKey="successRate" 
                name="Success Rate" 
                stroke="#10b981" 
                fill="none" 
                strokeWidth={3} 
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500 border border-dashed rounded-lg">
            No historical throughput data available.
          </div>
        )}
      </motion.div>
    </Card>
  );
};

export default ThroughputPanel;