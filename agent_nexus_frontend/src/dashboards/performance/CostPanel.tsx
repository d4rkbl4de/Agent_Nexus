import * as React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { DollarSign, Clock, Users, Zap } from 'lucide-react';
import Card from '../../shared/ui/Card';
import Badge from '../../shared/ui/Badge';
import { useScheduler } from '../../motion/performance/scheduler';
import { motion } from 'framer-motion';

export interface CostDataPoint {
  time: string; // ISO or short format for X-axis
  totalCost: number; // Cumulative or per-period total cost (USD)
  tokenCost: number; // Cost related to LLM tokens (USD)
  apiCost: number; // Cost related to external API calls (USD)
}

interface CostPanelProps {
  title: string;
  historicalData: CostDataPoint[];
  totalLifetimeCost: number;
  averageTaskCost: number;
  isLoading: boolean;
}

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
            {`${p.name}: $${p.value.toFixed(4)}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const CostPanel: React.FC<CostPanelProps> = ({
  title,
  historicalData,
  totalLifetimeCost,
  averageTaskCost,
  isLoading,
}) => {
  const { canRunAnimation } = useScheduler();
  
  const formattedTotalCost = `$${totalLifetimeCost.toFixed(4)}`;
  const formattedAverageCost = `$${averageTaskCost.toFixed(4)}`;
  
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
        <Badge variant="secondary" className="text-sm">USD</Badge>
      </div>

      {/* Summary Metrics */}
      <motion.div className="grid grid-cols-1 md:grid-cols-2 gap-4" {...motionProps}>
        <SummaryMetric
          icon={<DollarSign className="w-6 h-6 text-white" />}
          label="Total Lifetime Cost"
          value={isLoading ? '...' : formattedTotalCost}
          color="bg-indigo-500"
        />
        <SummaryMetric
          icon={<Clock className="w-6 h-6 text-white" />}
          label="Average Task Cost"
          value={isLoading ? '...' : formattedAverageCost}
          color="bg-green-500"
        />
      </motion.div>

      {/* Historical Chart */}
      <motion.div className="h-80 w-full" {...motionProps}>
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Cost Trend (Last 7 Periods)</h3>
        {isLoading && historicalData.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 border border-dashed rounded-lg">
            <Loader className="w-6 h-6 mr-2 animate-spin"/> Loading chart data...
          </div>
        ) : historicalData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={historicalData}
              margin={{ top: 5, right: 20, left: -10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="time" stroke="#718096" tickLine={false} axisLine={false} />
              <YAxis 
                stroke="#718096" 
                tickFormatter={(value) => `$${value.toFixed(2)}`} 
                domain={['auto', 'auto']}
              />
              <Tooltip content={<CustomChartTooltip />} />
              <Line 
                type="monotone" 
                dataKey="totalCost" 
                name="Total Cost" 
                stroke="#4f46e5" 
                strokeWidth={3} 
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey="tokenCost" 
                name="Token Cost" 
                stroke="#10b981" 
                strokeWidth={2} 
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey="apiCost" 
                name="API Cost" 
                stroke="#f59e0b" 
                strokeWidth={2} 
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500 border border-dashed rounded-lg">
            No historical cost data available.
          </div>
        )}
      </motion.div>
    </Card>
  );
};

export default CostPanel;