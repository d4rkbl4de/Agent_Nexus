import * as React from 'react';
import { useAnimate, AnimationPlaybackControls, TargetAndTransition, CustomValueType } from 'framer-motion';

type TimelineTarget = React.RefObject<HTMLElement> | number | string | null;

interface TimelineAnimation {
  target: TimelineTarget;
  animation: TargetAndTransition;
  options?: {
    duration?: number;
    ease?: string | string[];
  };
  at: number | string;
}

export function useTimeline(animations: TimelineAnimation[]): [React.RefObject<any>, () => AnimationPlaybackControls] {
  const [scope, animate] = useAnimate();

  const startTimeline = React.useCallback(() => {
    const timelineDefinition: [TimelineTarget, TargetAndTransition, { duration?: number, at: number | string, ease?: string | string[] }][] = animations.map((item) => {
      const { target, animation, options, at } = item;
      
      return [
        target,
        animation,
        {
          duration: options?.duration,
          ease: options?.ease,
          at: at,
        }
      ];
    });

    return animate(timelineDefinition);
  }, [animate, animations]);

  return [scope, startTimeline];
}