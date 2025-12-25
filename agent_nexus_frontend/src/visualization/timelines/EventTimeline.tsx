import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useScheduler } from '../../motion/performance/scheduler';
import { assert } from '../../utils/assert';

interface TimelineEvent {
  id: string | number;
  time: Date | string;
  title: string;
  description: string;
  status: 'success' | 'failure' | 'in_progress' | 'pending';
  icon?: React.ReactNode;
}

interface EventTimelineProps {
  events: TimelineEvent[];
  contextLabel?: string;
  reverseOrder?: boolean;
}

const statusColorMap = {
  success: 'border-green-500 bg-green-100 text-green-800',
  failure: 'border-red-500 bg-red-100 text-red-800',
  in_progress: 'border-blue-500 bg-blue-100 text-blue-800 animate-pulse',
  pending: 'border-gray-400 bg-gray-100 text-gray-600',
};

const EventTimeline: React.FC<EventTimelineProps> = ({
  events,
  contextLabel = 'Execution Timeline',
  reverseOrder = false,
}) => {
  const { canRunAnimation } = useScheduler();

  const sortedEvents = React.useMemo(() => {
    // Ensure stable sort for consistent rendering
    const sorted = [...events].sort((a, b) => {
      const timeA = new Date(a.time).getTime();
      const timeB = new Date(b.time).getTime();
      return timeA - timeB;
    });

    return reverseOrder ? sorted.reverse() : sorted;
  }, [events, reverseOrder]);

  const transitionProps = React.useMemo(() => {
    return canRunAnimation() ? {
      initial: { opacity: 0, y: 20 },
      animate: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: -20 },
      transition: { duration: 0.3, ease: 'easeOut' },
    } : {
      initial: false,
      animate: { opacity: 1 },
      exit: { opacity: 0 },
      transition: { duration: 0.1 },
    };
  }, [canRunAnimation]);

  if (events.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500 border border-dashed rounded-lg">
        No events recorded yet.
      </div>
    );
  }

  return (
    <div className="relative p-6 bg-white rounded-xl shadow-lg">
      <h3 className="mb-6 text-lg font-semibold text-gray-700">{contextLabel}</h3>
      <div className="space-y-8">
        <AnimatePresence initial={false}>
          {sortedEvents.map((event, index) => {
            assert(event.id !== null && event.id !== undefined, 'Event must have a valid ID.');
            const statusClass = statusColorMap[event.status];
            const isLast = index === sortedEvents.length - 1;

            const timeString = event.time instanceof Date ? event.time.toLocaleTimeString() : String(event.time);

            return (
              <motion.div
                key={event.id}
                {...transitionProps}
                className="flex"
              >
                {/* Timeline Marker and Line */}
                <div className="flex flex-col items-center mr-4">
                  <div className={`w-4 h-4 rounded-full border-2 ${statusClass}`} />
                  {!isLast && (
                    <div className={`flex-grow w-px ${reverseOrder ? 'bg-gray-300' : 'bg-gray-300'}`} />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 pb-4">
                  <p className="text-xs font-medium text-gray-500 mb-1">{timeString}</p>
                  <h4 className="text-sm font-semibold text-gray-800 flex items-center">
                    {event.icon && <span className="mr-2 text-md">{event.icon}</span>}
                    {event.title}
                  </h4>
                  <p className="mt-1 text-sm text-gray-600">{event.description}</p>
                  <span className={`inline-block mt-2 px-2 py-0.5 text-xs font-semibold rounded-full ${statusClass.replace('border-', 'text-').replace('bg-', 'bg-')}`}>
                    {event.status.toUpperCase().replace('_', ' ')}
                  </span>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default EventTimeline;