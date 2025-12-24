'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { EASING } from '../tokens/easing';
import { DURATION } from '../tokens/duration';

interface DecisionRippleProps {
  isDeciding: boolean;
  className?: string;
  dotClassName?: string;
  rippleCount?: 3 | 2 | 1;
  color?: string; // Tailwind class like 'bg-nexus-primary'
}

export const DecisionRipple: React.FC<DecisionRippleProps> = ({
  isDeciding,
  className,
  dotClassName,
  rippleCount = 3,
  color = 'bg-nexus-primary',
}) => {
  const ripples = Array.from({ length: rippleCount });

  const rippleVariants = {
    start: {
      scale: 0.1,
      opacity: 0.8,
    },
    animate: {
      scale: 3,
      opacity: 0,
    },
  };

  return (
    <AnimatePresence>
      {isDeciding && (
        <div
          className={cn(
            'relative flex items-center justify-center h-4 w-4',
            className
          )}
        >
          {/* Static Center Dot */}
          <motion.div
            className={cn('absolute h-2 w-2 rounded-full z-10', color, dotClassName)}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: DURATION.fast }}
          />

          {/* Expanding Ripples */}
          {ripples.map((_, index) => (
            <motion.div
              key={index}
              className={cn('absolute h-full w-full rounded-full', color)}
              variants={rippleVariants}
              initial="start"
              animate="animate"
              exit="start" 
              transition={{
                duration: DURATION.slow,
                ease: EASING.out,
                repeat: Infinity,
                delay: index * (DURATION.slow / rippleCount), 
              }}
            />
          ))}
        </div>
      )}
    </AnimatePresence>
  );
};