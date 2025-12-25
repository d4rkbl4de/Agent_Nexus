import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronRight, CheckCircle, XCircle, Clock, Zap } from 'lucide-react';
import { useScheduler } from '../../motion/performance/scheduler';
import { assertExists } from '../../utils/assert';

interface ExecutionStep {
  id: string;
  name: string;
  type: 'agent' | 'tool' | 'step';
  status: 'success' | 'failure' | 'in_progress' | 'pending';
  startTime: Date;
  endTime?: Date;
  details?: string;
  children?: ExecutionStep[];
}

interface ExecutionTimelineProps {
  rootSteps: ExecutionStep[];
  contextLabel?: string;
}

const statusColorMap = {
  success: { text: 'text-green-600', border: 'border-green-500', bg: 'bg-green-100' },
  failure: { text: 'text-red-600', border: 'border-red-500', bg: 'bg-red-100' },
  in_progress: { text: 'text-blue-600', border: 'border-blue-500', bg: 'bg-blue-100' },
  pending: { text: 'text-gray-600', border: 'border-gray-400', bg: 'bg-gray-100' },
};

const iconMap = {
  success: CheckCircle,
  failure: XCircle,
  in_progress: Zap,
  pending: Clock,
};

const formatDuration = (start: Date, end?: Date): string => {
  const diffMs = (end || new Date()).getTime() - start.getTime();
  if (diffMs < 0) return '0ms';
  
  if (diffMs < 1000) return `${diffMs}ms`;
  
  const seconds = (diffMs / 1000).toFixed(2);
  return `${seconds}s`;
};

interface StepProps {
  step: ExecutionStep;
  isRoot?: boolean;
}

const ExecutionStepComponent: React.FC<StepProps> = ({ step, isRoot = false }) => {
  assertExists(step.id, 'Execution step must have a valid ID.');
  const [isExpanded, setIsExpanded] = React.useState(true);
  const { canRunAnimation } = useScheduler();

  const hasChildren = step.children && step.children.length > 0;
  const colors = statusColorMap[step.status];
  const StatusIcon = iconMap[step.status];
  const toggleIcon = isExpanded ? ChevronDown : ChevronRight;

  const transitionProps = React.useMemo(() => {
    return canRunAnimation() ? {
      initial: { opacity: 0, height: 0 },
      animate: { opacity: 1, height: 'auto' },
      exit: { opacity: 0, height: 0 },
      transition: { duration: 0.25, ease: 'easeOut' },
    } : {
      initial: false,
      animate: { opacity: 1, height: 'auto' },
      exit: { opacity: 0, height: 0 },
      transition: { duration: 0.1 },
    };
  }, [canRunAnimation]);

  const headerTransition = canRunAnimation() ? { 
    whileHover: { backgroundColor: colors.bg, transition: { duration: 0.1 } } 
  } : {};

  return (
    <div className={`relative ${!isRoot ? 'ml-6' : ''}`}>
      {/* Connector Line (Vertical line for nested steps) */}
      {!isRoot && (
        <div className="absolute top-0 bottom-0 -left-6 w-px bg-gray-300" />
      )}

      {/* Step Header */}
      <motion.div
        className={`flex items-center cursor-pointer p-2 rounded-lg ${colors.text} ${colors.bg}`}
        onClick={() => hasChildren && setIsExpanded(!isExpanded)}
        {...headerTransition}
      >
        {/* Toggle Icon & Horizontal Connector */}
        <div className="flex items-center">
          {hasChildren && React.createElement(toggleIcon, { className: 'w-4 h-4 mr-1 flex-shrink-0' })}
          {/* Horizontal Connector (T-joint) */}
          {!isRoot && <div className="absolute w-4 h-px -left-4 bg-gray-300" />}
        </div>

        {/* Status Icon */}
        <StatusIcon className={`w-4 h-4 mr-2 flex-shrink-0 ${colors.text}`} />
        
        {/* Name and Metadata */}
        <span className="font-semibold text-sm flex-1 truncate">{step.name}</span>
        <span className="text-xs font-mono ml-4 text-gray-500">{formatDuration(step.startTime, step.endTime)}</span>
      </motion.div>

      {/* Expanded Content (Details and Children) */}
      <AnimatePresence initial={false}>
        {isExpanded && hasChildren && (
          <motion.div
            className="overflow-hidden"
            {...transitionProps}
          >
            {step.details && (
              <p className="mt-2 text-xs text-gray-500 border-l-2 border-gray-200 pl-4 ml-2">
                {step.details}
              </p>
            )}
            <div className="mt-2 space-y-1">
              {step.children?.map(child => (
                <ExecutionStepComponent key={child.id} step={child} />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const ExecutionTimeline: React.FC<ExecutionTimelineProps> = ({
  rootSteps,
  contextLabel = 'Agent Execution Flow',
}) => {
  if (rootSteps.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500 border border-dashed rounded-lg bg-gray-50">
        No execution steps recorded for this run.
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-xl shadow-2xl ring-1 ring-gray-100">
      <h3 className="mb-6 text-xl font-bold text-gray-800 border-b pb-3">{contextLabel}</h3>
      <div className="space-y-3">
        {rootSteps.map((step) => (
          <ExecutionStepComponent key={step.id} step={step} isRoot={true} />
        ))}
      </div>
    </div>
  );
};

export default ExecutionTimeline;