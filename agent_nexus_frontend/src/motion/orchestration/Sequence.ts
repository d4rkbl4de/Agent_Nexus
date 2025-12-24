import * as React from 'react';
import { useAnimate, stagger, AnimationPlaybackControls, TargetAndTransition, CustomValueType } from 'framer-motion';

type SequenceTarget = React.RefObject<HTMLElement> | number | string | null;

interface SequenceAnimation {
  target: SequenceTarget;
  animation: TargetAndTransition;
  options?: {
    duration?: number;
    delay?: number;
    ease?: string | string[];
    staggerDelay?: number;
  };
}

export function useSequence(sequences: SequenceAnimation[]): [React.RefObject<any>, () => AnimationPlaybackControls] {
  const [scope, animate] = useAnimate();

  const startSequence = React.useCallback(() => {
    const sequenceDefinition: [SequenceTarget, TargetAndTransition, { duration?: number, delay?: number | CustomValueType, ease?: string | string[] }][] = sequences.map((item) => {
      const { target, animation, options } = item;
      
      const staggerDelay = options?.staggerDelay;
      let delay = options?.delay ?? 0;

      if (staggerDelay) {
        delay = stagger(staggerDelay, { start: delay as number });
      }

      return [
        target,
        animation,
        {
          duration: options?.duration,
          delay: delay,
          ease: options?.ease,
        }
      ];
    });

    return animate(sequenceDefinition);
  }, [animate, sequences]);

  return [scope, startSequence];
}