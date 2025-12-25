import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Loader, CheckCircle, XCircle, Code, MessageSquare, Briefcase, Clock, Zap } from 'lucide-react';
import { ExecutionStep, ExecutionStepType, ExecutionStepStatus } from '../../visualization/timelines/ExecutionTimeline';
import { useScheduler } from '../../motion/performance/scheduler';
import Tooltip from '../../shared/ui/Tooltip';
import Card from '../../shared/ui/Card';

interface ExecutionTraceProps {
  steps: ExecutionStep[];
  isLoading?: boolean;
}

interface StepHeaderProps {
  step: ExecutionStep;
  isExpanded: boolean;
  onToggle: (id: string) => void;
}

const STATUS_ICON_MAP: Record<ExecutionStepStatus, React.ReactNode> = {
  PENDING: <Loader className="w-5 h-5 text-gray-400 animate-spin" aria-label="Pending" />,
  RUNNING: <Zap className="w-5 h-5 text-indigo-500 animate-pulse" aria-label="Running" />,
  COMPLETE: <CheckCircle className="w-5 h-5 text-green-500" aria-label="Complete" />,
  ERROR: <XCircle className="w-5 h-5 text-red-500" aria-label="Error" />,
};

const TYPE_ICON_MAP: Record<ExecutionStepType, React.ReactNode> = {
  THOUGHT: <MessageSquare className="w-5 h-5 text-blue-500" aria-label="Thought" />,
  TOOL_CALL: <Briefcase className="w-5 h-5 text-yellow-600" aria-label="Tool Call" />,
  OBSERVATION: <Clock className="w-5 h-5 text-purple-500" aria-label="Observation" />,
  FINAL_ANSWER: <CheckCircle className="w-5 h-5 text-green-700" aria-label="Final Answer" />,
};

const StepHeader: React.FC<StepHeaderProps> = ({ step, isExpanded, onToggle }) => {
  const Icon = React.useMemo(() => TYPE_ICON_MAP[step.type], [step.type]);
  const StatusIcon = React.useMemo(() => STATUS_ICON_MAP[step.status], [step.status]);

  const durationMs = step.duration_ms !== undefined ? `${step.duration_ms.toFixed(2)}ms` : 'N/A';
  
  const title = React.useMemo(() => {
    if (step.title) return step.title;
    if (step.type === 'TOOL_CALL' && step.details?.tool_name) return `CALL: ${step.details.tool_name}`;
    if (step.type === 'OBSERVATION' && step.details?.result_type) return `OBSERVATION: ${step.details.result_type}`;
    return step.type.replace('_', ' ');
  }, [step.title, step.type, step.details?.tool_name, step.details?.result_type]);

  return (
    <div 
      role="button"
      tabIndex={0}
      aria-expanded={isExpanded}
      aria-controls={`step-details-${step.id}`}
      className="flex items-center justify-between p-4 cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors duration-150 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
      onClick={() => onToggle(step.id)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') onToggle(step.id);
      }}
    >
      <div className="flex items-center space-x-4 min-w-0">
        <Tooltip label={step.type} position="top">
          {Icon}
        </Tooltip>
        <span className="text-sm font-medium text-gray-800 truncate">
          {title}
        </span>
      </div>
      
      <div className="flex items-center space-x-4">
        <Tooltip label={`Duration: ${durationMs}`} position="top">
          <div className="text-xs text-gray-500 w-16 text-right tabular-nums">
            {durationMs}
          </div>
        </Tooltip>
        <Tooltip label={step.status} position="top">
          {StatusIcon}
        </Tooltip>
        <ChevronDown 
          className={`w-5 h-5 text-gray-500 transition-transform duration-200 ${isExpanded ? 'rotate-180' : 'rotate-0'}`} 
          aria-hidden="true"
        />
      </div>
    </div>
  );
};

const StepDetails: React.FC<{ step: ExecutionStep }> = ({ step }) => {
  const formatCode = (content: string) => {
    return (
      <pre className="p-3 mt-2 text-xs bg-gray-800 text-gray-100 rounded-lg overflow-x-auto font-mono">
        <code className="whitespace-pre-wrap">{content}</code>
      </pre>
    );
  };
  
  const content = React.useMemo(() => {
    if (step.type === 'TOOL_CALL' && step.details?.tool_args) {
      return {
        label: 'Tool Arguments:',
        icon: <Code className="w-4 h-4 mr-1"/>,
        data: JSON.stringify(step.details.tool_args, null, 2),
      };
    }
    if (step.type === 'OBSERVATION' && step.details?.result) {
      return {
        label: 'Tool Output:',
        icon: <MessageSquare className="w-4 h-4 mr-1"/>,
        data: step.details.result,
      };
    }
    if (step.content) {
      return {
        label: 'Content:',
        icon: <MessageSquare className="w-4 h-4 mr-1"/>,
        data: step.content,
        isPlain: true,
      };
    }
    return null;
  }, [step.type, step.details, step.content]);

  return (
    <motion.div
      id={`step-details-${step.id}`}
      initial="collapsed"
      animate="open"
      exit="collapsed"
      variants={{
        open: { opacity: 1, height: 'auto' },
        collapsed: { opacity: 0, height: 0 },
      }}
      transition={{ duration: 0.3 }}
      className="py-3 px-6 border-t border-gray-200 bg-white overflow-hidden"
    >
      <div className="text-sm text-gray-600 space-y-3">
        {content && (
          <div>
            <div className="font-semibold text-gray-800 flex items-center mb-1">
              {content.icon} {content.label}
            </div>
            {content.isPlain ? (
              <p className="whitespace-pre-wrap text-xs">{content.data}</p>
            ) : (
              formatCode(content.data as string)
            )}
          </div>
        )}

        {step.status === 'ERROR' && step.details?.error_message && (
          <div className="p-3 border border-red-300 bg-red-50 text-red-700 rounded-md" role="alert">
            <div className="font-semibold flex items-center">
                <XCircle className="w-4 h-4 mr-2"/> Error Detail:
            </div>
            <code className="text-xs mt-1 block">{step.details.error_message}</code>
          </div>
        )}

        {!content && step.status !== 'ERROR' && (
          <p className="text-xs text-gray-500 italic">No structured details or primary content available for this step.</p>
        )}
      </div>
    </motion.div>
  );
};


const ExecutionTrace: React.FC<ExecutionTraceProps> = ({ steps, isLoading = false }) => {
  const [expandedStepId, setExpandedStepId] = React.useState<string | null>(null);
  const { canRunAnimation } = useScheduler();

  const handleToggle = React.useCallback((stepId: string) => {
    setExpandedStepId(prevId => (prevId === stepId ? null : stepId));
  }, []);
  
  const motionProps = canRunAnimation() ? {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    transition: { duration: 0.5 },
  } : {
    initial: false,
    animate: { opacity: 1 },
    transition: { duration: 0.1 },
  };

  if (steps.length === 0 && !isLoading) {
    return (
      <Card className="p-8 text-center text-gray-500 border border-dashed rounded-xl bg-gray-50 min-h-[300px]">
        No execution steps recorded yet. Start the agent to generate a trace.
      </Card>
    );
  }

  return (
    <motion.div className="space-y-3" {...motionProps}>
      {steps.map((step, index) => (
        <Card key={`${step.id}-${index}`} className="p-0 overflow-hidden shadow-lg border border-gray-200">
          <StepHeader 
            step={step} 
            isExpanded={expandedStepId === step.id} 
            onToggle={handleToggle} 
          />
          <AnimatePresence>
            {expandedStepId === step.id && <StepDetails step={step} />}
          </AnimatePresence>
        </Card>
      ))}

      {isLoading && (
        <Card className="p-4 flex items-center justify-center text-indigo-600 shadow-lg" role="status" aria-live="polite">
          <Loader className="w-6 h-6 mr-3 animate-spin" />
          <span className="font-medium">Waiting for next step...</span>
        </Card>
      )}
    </motion.div>
  );
};

export default ExecutionTrace;