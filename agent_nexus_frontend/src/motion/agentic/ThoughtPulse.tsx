'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { EASING } from '../tokens/easing';
import { DURATION } from '../tokens/duration';

interface ThoughtPulseProps {
  isThinking: boolean;
  className?: string;
  dotSize?: 'sm' | 'md' | 'lg';
  color?: string; // Tailwind class like 'bg-nexus-primary'
}

const sizeMap = {
  sm: 'h-1.5 w-1.5',
  md: 'h-2 w-2',
  lg: 'h-2.5 w-2.5',
};

const pulseVariants = {
  start: {
    y: '0%',
    opacity: 0.8,
  },
  end: {
    y: '-100%',
    opacity: 0.2,
  },
};

export const ThoughtPulse: React.FC<ThoughtPulseProps> = ({
  isThinking,
  className,
  dotSize = 'md',
  color = 'bg-nexus-primary',
}) => {
  const dotClassName = sizeMap[dotSize];
  const dots = [0, 1, 2];
  const delayStep = DURATION.fast * 0.5;

  return (
    <AnimatePresence>
      {isThinking && (
        <div className={cn('flex items-center space-x-1.5 overflow-hidden', className)}>
          {dots.map((index) => (
            <motion.div
              key={index}
              className={cn(dotClassName, 'rounded-full', color)}
              variants={pulseVariants}
              initial="start"
              animate="end"
              transition={{
                duration: DURATION.fast,
                ease: EASING.easeInOut,
                repeat: Infinity,
                repeatType: 'reverse',
                delay: index * delayStep,
              }}
            />
          ))}
        </div>
      )}
    </AnimatePresence>
  );
};