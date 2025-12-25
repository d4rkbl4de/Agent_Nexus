import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lightbulb, Code, Target, MessageSquare, ChevronDown, CheckCircle, XCircle } from 'lucide-react';
import { useScheduler } from '../../motion/performance/scheduler';
import Card from '../../shared/ui/Card';
import Badge from '../../shared/ui/Badge';

interface ReasoningStep {
  id: string;
  timestamp: string;
  step_number: number;
  type: 'Thought' | 'Decision' | 'Tool_Output' | 'Conclusion';
  title: string;
  content: string;
  associated_tool?: string;
  status: 'Success' | 'Failure' | 'Pending';
}

interface ReasoningTraceProps {
  steps: ReasoningStep[];
  isLoading?: boolean;
}

interface StepItemProps {
  step: ReasoningStep;
  isExpanded: boolean;
  onToggle: (id: string) => void;
}

const TYPE_ICON_MAP: Record<ReasoningStep['type'], React.ReactNode> = {
  Thought: <Lightbulb className="w-5 h-5"/>,
  Decision: <Target className="w-5 h-5"/>,
  Tool_Output: <Code className="w-5 h-5"/>,
  Conclusion: <MessageSquare className="w-5 h-5"/>,
};

const STATUS_COLOR_MAP: Record<ReasoningStep['status'], string> = {
  Success: 'bg-green-100 text-green-700 border-green-300',
  Failure: 'bg-red-100 text-red-700 border-red-300',
  Pending: 'bg-yellow-100 text-yellow-700 border-yellow-300',
};

const StatusIconMap: Record<ReasoningStep['status'], React.ReactNode> = {
  Success: <CheckCircle className="w-4 h-4 text-green-500"/>,
  Failure: <XCircle className="w-4 h-4 text-red-500"/>,
  Pending: <Clock className="w-4 h-4 text-yellow-500"/>,
};

const StepItem: React.FC<StepItemProps> = React.memo(({ step, isExpanded, onToggle }) => {
  const { canRunAnimation } = useScheduler();
  const Icon = React.useMemo(() => TYPE_ICON_MAP[step.type], [step.type]);
  const statusColorClass = STATUS_COLOR_MAP[step.status];

  const formattedTime = React.useMemo(() => {
    return new Date(step.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit'});
  }, [step.timestamp]);
  
  const formattedContent = React.useMemo(() => {
      // Use markdown-like formatting for reasoning content
      return step.content
        .split('\n')
        .map((line, index) => <p key={index} className="mb-1">{line}</p>);
  }, [step.content]);


  return (
    <div className="relative">
      {/* Timeline Connector */}
      <div className="absolute top-0 left-5 h-full w-0.5 bg-gray-200 -translate-x-1/2" />
      
      {/* Step Container */}
      <Card className="p-0 overflow-hidden mb-4 relative z-10 border border-gray-100">
        
        {/* Header/Toggle */}
        <div 
          role="button"
          tabIndex={0}
          aria-expanded={isExpanded}
          aria-controls={`reasoning-content-${step.id}`}
          className="flex items-center p-4 cursor-pointer bg-white hover:bg-gray-50 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
          onClick={() => onToggle(step.id)}
        >
          {/* Icon Circle */}
          <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center mr-4 shadow-md ${statusColorClass}`}>
            {Icon}
          </div>

          <div className="flex-grow min-w-0">
            <div className="flex items-center space-x-2">
                <Badge variant="primary" className="text-xs">{`STEP ${step.step_number}`}</Badge>
                <Badge className={`text-xs ${statusColorClass}`}>{step.type.toUpperCase().replace('_', ' ')}</Badge>
            </div>
            <h3 className="text-base font-semibold text-gray-900 mt-1 truncate">{step.title}</h3>
          </div>

          <div className="flex-shrink-0 flex items-center space-x-3 ml-4 text-sm text-gray-500">
            <span className="font-mono text-xs">{formattedTime}</span>
            {StatusIconMap[step.status]}
            <ChevronDown 
              className={`w-5 h-5 transition-transform duration-200 ${isExpanded ? 'rotate-180' : 'rotate-0'}`} 
              aria-hidden="true"
            />
          </div>
        </div>
        
        {/* Details */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              id={`reasoning-content-${step.id}`}
              initial={canRunAnimation() ? { opacity: 0, height: 0 } : false}
              animate={{ opacity: 1, height: 'auto' }}
              exit={canRunAnimation() ? { opacity: 0, height: 0 } : false}
              transition={{ duration: 0.3 }}
              className="p-4 border-t border-gray-100 bg-gray-50 overflow-hidden"
            >
              <div className="text-sm space-y-3">
                <div className="font-semibold text-gray-800">Rationale/Content:</div>
                <div className="text-xs text-gray-700 leading-normal border-l-2 border-indigo-300 pl-3">
                  {formattedContent}
                </div>
                
                {step.associated_tool && (
                  <div className="mt-3 text-xs text-gray-600">
                    <span className="font-semibold text-gray-800">Associated Tool:</span> {step.associated_tool}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </div>
  );
});

const ReasoningTrace: React.FC<ReasoningTraceProps> = ({ steps, isLoading = false }) => {
  const [expandedStepId, setExpandedStepId] = React.useState<string | null>(null);
  const { canRunAnimation } = useScheduler();

  const handleToggle = React.useCallback((stepId: string) => {
    setExpandedStepId(prevId => (prevId === stepId ? null : stepId));
  }, []);
  
  const sortedSteps = React.useMemo(() => {
    return [...steps].sort((a, b) => a.step_number - b.step_number);
  }, [steps]);

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
        No reasoning steps recorded. Execute an agent task to view its thought process.
      </Card>
    );
  }

  return (
    <motion.div className="pt-2" {...motionProps}>
      {sortedSteps.map((step, index) => (
        <StepItem 
          key={step.id} 
          step={step} 
          isExpanded={expandedStepId === step.id} 
          onToggle={handleToggle} 
        />
      ))}

      {isLoading && (
        <div className="relative">
          {/* Connector to loading step */}
          {sortedSteps.length > 0 && <div className="absolute top-0 left-5 h-2 w-0.5 bg-gray-200 -translate-x-1/2" />}

          <Card className="p-4 flex items-center text-indigo-600 shadow-lg relative z-10 border border-indigo-300">
            <Loader className="w-5 h-5 mr-3 animate-spin flex-shrink-0" />
            <span className="font-medium">Agent is actively reasoning...</span>
          </Card>
        </div>
      )}
    </motion.div>
  );
};

export default ReasoningTrace;