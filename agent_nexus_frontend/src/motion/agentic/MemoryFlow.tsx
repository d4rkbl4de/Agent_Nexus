'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { EASING } from '../tokens/easing';
import { DURATION } from '../tokens/duration';

interface MemoryFlowProps {
  isProcessing: boolean;
  className?: string;
  dotSize?: 'sm' | 'md' | 'lg';
  flowSpeed?: 'slow' | 'normal' | 'fast';
  color?: string; // Tailwind class like 'bg-nexus-light'
  flowDirection?: 'x' | 'y';
}

const speedMap = {
  slow: DURATION.slow * 2,
  normal: DURATION.slow,
  fast: DURATION.fast,
};

const sizeMap = {
  sm: 'h-1 w-1',
  md: 'h-1.5 w-1.5',
  lg: 'h-2 w-2',
};

export const MemoryFlow: React.FC<MemoryFlowProps> = ({
  isProcessing,
  className,
  dotSize = 'md',
  flowSpeed = 'normal',
  color = 'bg-nexus-light',
  flowDirection = 'x',
}) => {
  const dotCount = 8;
  const speed = speedMap[flowSpeed];
  const dotClassName = sizeMap[dotSize];

  const flowDistance = flowDirection === 'x' ? -50 : -50; // Pixels
  const flowProperty = flowDirection === 'x' ? 'x' : 'y';

  const dotVariants = {
    initial: {
      opacity: 0,
      [flowProperty]: 0,
    },
    animate: {
      opacity: [0.2, 1, 0.2],
      [flowProperty]: [flowDistance, 0, flowDistance],
    },
  };

  return (
    <AnimatePresence>
      {isProcessing && (
        <div
          className={cn(
            'relative flex items-center justify-center overflow-hidden',
            flowDirection === 'x' ? 'w-full h-4' : 'h-full w-4 flex-col',
            className
          )}
        >
          {Array.from({ length: dotCount }).map((_, index) => (
            <motion.div
              key={index}
              className={cn('absolute rounded-full', color, dotClassName)}
              variants={dotVariants}
              initial="initial"
              animate="animate"
              transition={{
                duration: speed,
                ease: EASING.easeInOut,
                repeat: Infinity,
                delay: index * (speed / dotCount),
              }}
            />
          ))}
        </div>
      )}
    </AnimatePresence>
  );
};