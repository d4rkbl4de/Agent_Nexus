import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { XCircle, Clock, FileText, Code, ChevronDown, Tag } from 'lucide-react';
import { useScheduler } from '../../motion/performance/scheduler';
import Card from '../../shared/ui/Card';
import Button from '../../shared/ui/Button';
import Tooltip from '../../shared/ui/Tooltip';

export interface FailureEntry {
  id: string;
  timestamp: string;
  task_id: string;
  agent_id: string;
  error_type: string; 
  summary: string;
  details: string; 
  stack_trace?: string;
}

interface FailureLogProps {
  failures: FailureEntry[];
  onReload?: () => void;
  isLoading?: boolean;
}

interface FailureItemProps {
  failure: FailureEntry;
}

const FailureItem: React.FC<FailureItemProps> = React.memo(({ failure }) => {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const { canRunAnimation } = useScheduler();

  const handleToggle = React.useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);

  const time = React.useMemo(() => new Date(failure.timestamp).toLocaleString(), [failure.timestamp]);

  return (
    <Card className="p-0 overflow-hidden shadow-lg border border-red-300">
      <div 
        role="button"
        tabIndex={0}
        aria-expanded={isExpanded}
        aria-controls={`failure-details-${failure.id}`}
        className="flex items-start p-4 cursor-pointer bg-red-50 hover:bg-red-100 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-red-500/50"
        onClick={handleToggle}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') handleToggle();
        }}
      >
        {/* Left Section: Icon and Summary */}
        <div className="flex-shrink-0 mr-4 mt-1">
          <XCircle className="w-6 h-6 text-red-600" aria-label="Failure icon" />
        </div>
        
        <div className="flex-grow min-w-0">
          <div className="flex items-center space-x-2 text-sm font-semibold text-red-800">
            <Tag className="w-4 h-4" />
            <span className="truncate">{failure.error_type}</span>
          </div>
          <p className="text-gray-700 text-sm mt-0.5 truncate">{failure.summary}</p>
          <div className="flex items-center space-x-4 text-xs text-gray-500 mt-1">
            <Tooltip label="Task ID" position="bottom">
              <span className="flex items-center"><FileText className="w-3 h-3 mr-1"/> {failure.task_id.substring(0, 8)}...</span>
            </Tooltip>
            <Tooltip label="Timestamp" position="bottom">
              <span className="flex items-center"><Clock className="w-3 h-3 mr-1"/> {time}</span>
            </Tooltip>
          </div>
        </div>

        {/* Right Section: Toggle */}
        <div className="flex-shrink-0 ml-4">
          <ChevronDown 
            className={`w-6 h-6 text-red-500 transition-transform duration-200 ${isExpanded ? 'rotate-180' : 'rotate-0'}`} 
            aria-hidden="true"
          />
        </div>
      </div>
      
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            id={`failure-details-${failure.id}`}
            initial={canRunAnimation() ? { opacity: 0, height: 0 } : false}
            animate={{ opacity: 1, height: 'auto' }}
            exit={canRunAnimation() ? { opacity: 0, height: 0 } : false}
            transition={{ duration: 0.3 }}
            className="p-4 border-t border-red-200 bg-white overflow-hidden"
          >
            <div className="text-sm space-y-3">
              <div className="font-semibold text-gray-800">Details:</div>
              <p className="whitespace-pre-wrap text-xs text-gray-700">{failure.details}</p>
              
              {failure.stack_trace && (
                <div>
                  <div className="font-semibold text-gray-800 flex items-center mt-3 mb-1">
                    <Code className="w-4 h-4 mr-1"/> Stack Trace:
                  </div>
                  <pre className="p-3 text-xs bg-gray-800 text-gray-100 rounded-lg overflow-x-auto font-mono">
                    <code className="whitespace-pre-wrap">{failure.stack_trace}</code>
                  </pre>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
});

const FailureLog: React.FC<FailureLogProps> = ({ failures, onReload, isLoading }) => {
  const { canRunAnimation } = useScheduler();

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
    <motion.div className="space-y-4" {...motionProps}>
      <div className="flex justify-between items-center pb-2 border-b border-gray-200">
        <h2 className="text-xl font-bold text-red-700">Agent Failure Log</h2>
        {onReload && (
          <Button 
            onClick={onReload} 
            variant="secondary" 
            size="sm" 
            isLoading={isLoading}
            leftIcon={<Clock className="w-4 h-4" />}
          >
            Refresh Log
          </Button>
        )}
      </div>

      {isLoading && failures.length === 0 && (
        <Card className="p-8 text-center text-indigo-600 shadow-lg" role="status" aria-live="polite">
          <Loader className="w-6 h-6 mx-auto mb-3 animate-spin" />
          <span className="font-medium">Loading failure logs...</span>
        </Card>
      )}

      {failures.length === 0 && !isLoading && (
        <Card className="p-8 text-center text-gray-500 border border-dashed rounded-xl bg-gray-50 min-h-[150px]">
          No agent failures recorded. The system is operating smoothly.
        </Card>
      )}

      <div className="space-y-3">
        {failures.map((failure) => (
          <FailureItem key={failure.id} failure={failure} />
        ))}
      </div>
    </motion.div>
  );
};

export default FailureLog;