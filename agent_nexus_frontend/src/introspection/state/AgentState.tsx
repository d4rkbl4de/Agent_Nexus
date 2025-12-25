import * as React from 'react';
import { motion } from 'framer-motion';
import { Agent, AgentStatus, AgentTelemetry, AgentTask } from '../../types/agent';
import { Cpu, Zap, Activity, Clock, AlertTriangle, CheckCircle, Package, Database, Hash, ListChecks } from 'lucide-react';
import Card from '../../shared/ui/Card';
import Badge from '../../shared/ui/Badge';
import Tooltip from '../../shared/ui/Tooltip';
import { useScheduler } from '../../motion/performance/scheduler';

interface AgentStateProps {
  agent: Agent;
  currentTask: AgentTask | null;
  telemetry: AgentTelemetry | null;
}

const STATUS_COLOR_MAP: Record<AgentStatus, string> = {
  idle: 'bg-gray-200 text-gray-700',
  running: 'bg-indigo-100 text-indigo-700',
  paused: 'bg-yellow-100 text-yellow-700',
  error: 'bg-red-100 text-red-700',
  complete: 'bg-green-100 text-green-700',
};

const StateDetail: React.FC<{ icon: React.ReactNode; label: string; value: string | number | undefined; unit?: string }> = 
  ({ icon, label, value, unit = '' }) => (
  <div className="flex items-center text-sm text-gray-700">
    <Tooltip label={label} position="top">
      <span className="flex-shrink-0 mr-2 text-indigo-500">{icon}</span>
    </Tooltip>
    <div className="flex flex-col min-w-0">
      <span className="font-medium truncate">{label}:</span>
      <span className="text-gray-900 font-mono text-xs truncate">
        {value !== undefined ? `${value}${unit}` : 'N/A'}
      </span>
    </div>
  </div>
);

const formatDuration = (startTime: Date, endTime?: Date): string => {
    if (!startTime) return 'N/A';
    
    const start = new Date(startTime).getTime();
    const end = endTime ? new Date(endTime).getTime() : Date.now();
    const durationMs = end - start;

    if (durationMs < 0) return 'N/A';

    const seconds = Math.floor(durationMs / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    const pad = (num: number) => num.toString().padStart(2, '0');

    return `${pad(hours)}h ${pad(minutes % 60)}m ${pad(seconds % 60)}s`;
};


const AgentState: React.FC<AgentStateProps> = ({ agent, currentTask, telemetry }) => {
  const { canRunAnimation } = useScheduler();

  const statusClass = STATUS_COLOR_MAP[agent.status] || STATUS_COLOR_MAP.idle;
  
  const currentStep = currentTask?.execution_log.length || 0;
  const lastStep = currentTask?.execution_log[currentStep - 1];

  const motionProps = canRunAnimation() ? {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    transition: { duration: 0.5 },
  } : {
    initial: false,
    animate: { opacity: 1 },
    transition: { duration: 0.1 },
  };

  return (
    <motion.div className="space-y-6" {...motionProps}>
      <Card className="p-6 border-l-4 border-indigo-500">
        <div className="flex justify-between items-center mb-4 pb-4 border-b border-gray-100">
            <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                <Activity className="w-6 h-6 mr-2 text-indigo-500"/> Current Agent State
            </h2>
            <Badge className={`text-lg font-semibold px-3 py-1 ${statusClass}`}>
                {agent.status.toUpperCase()}
            </Badge>
        </div>

        {/* Current Task Status */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-700 flex items-center">
            <ListChecks className="w-5 h-5 mr-2 text-indigo-500"/> Task Execution
          </h3>
          
          {currentTask && agent.status !== 'idle' ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StateDetail 
                    icon={<Hash className="w-4 h-4"/>} 
                    label="Current Step" 
                    value={currentStep} 
                />
                <StateDetail 
                    icon={<Clock className="w-4 h-4"/>} 
                    label="Run Time" 
                    value={formatDuration(currentTask.start_time, currentTask.end_time)} 
                />
                <StateDetail 
                    icon={<CheckCircle className="w-4 h-4"/>} 
                    label="Task Status" 
                    value={currentTask.status.toUpperCase()} 
                />
                <StateDetail 
                    icon={<Zap className="w-4 h-4"/>} 
                    label="Last Action" 
                    value={lastStep?.type?.replace('_', ' ') || 'N/A'} 
                />
                <div className="col-span-full">
                    <span className="font-semibold text-sm text-gray-700">Prompt: </span>
                    <p className="text-xs text-gray-600 italic truncate max-w-full">{currentTask.prompt}</p>
                </div>
            </div>
          ) : (
            <p className="text-gray-500 italic">Agent is currently idle or awaiting a new task submission.</p>
          )}
        </div>
      </Card>

      {/* Telemetry/Performance Indicators */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <Cpu className="w-5 h-5 mr-2 text-green-600"/> Resource Telemetry
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StateDetail 
            icon={<Cpu className="w-4 h-4"/>} 
            label="CPU Usage" 
            value={telemetry?.cpu_usage_percent?.toFixed(1)} 
            unit="%"
          />
          <StateDetail 
            icon={<Database className="w-4 h-4"/>} 
            label="Memory Usage" 
            value={telemetry?.memory_usage_mb?.toFixed(0)} 
            unit=" MB"
          />
          <StateDetail 
            icon={<Package className="w-4 h-4"/>} 
            label="API Calls" 
            value={telemetry?.api_calls_count} 
          />
          <StateDetail 
            icon={<AlertTriangle className="w-4 h-4"/>} 
            label="Token Cost" 
            value={telemetry?.token_cost_usd?.toFixed(4)} 
            unit=" USD"
          />
        </div>
      </Card>
    </motion.div>
  );
};

export default AgentState;