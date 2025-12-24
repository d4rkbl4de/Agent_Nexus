import * as React from 'react';
import { useReducedMotion } from '../hooks/useReducedMotion';

const TARGET_FPS = 60;
const MS_PER_FRAME = 1000 / TARGET_FPS;
const MIN_FRAME_TIME = MS_PER_FRAME * 0.8; 

export interface FrameBudget {
  maxFrameTime: number;
  isUnderLoad: boolean;
  canRunAnimation: (workloadTimeEstimate?: number) => boolean;
  currentFPS: number;
}

export function useFrameBudget(budgetMs: number = MS_PER_FRAME * 1.5): FrameBudget {
  const reducedMotion = useReducedMotion();
  
  const [currentFPS, setCurrentFPS] = React.useState(TARGET_FPS);
  const [lastFrameTime, setLastFrameTime] = React.useState(performance.now());
  const isUnderLoad = currentFPS < (TARGET_FPS * 0.9);

  const currentWorkloadRef = React.useRef(0);

  React.useEffect(() => {
    let animationFrameId: number;

    const monitor = (timestamp: number) => {
      const deltaTime = timestamp - lastFrameTime;
      const calculatedFPS = 1000 / deltaTime;
      
      setCurrentFPS(Math.round(calculatedFPS));
      setLastFrameTime(timestamp);

      currentWorkloadRef.current = 0;

      animationFrameId = requestAnimationFrame(monitor);
    };

    animationFrameId = requestAnimationFrame(monitor);

    return () => cancelAnimationFrame(animationFrameId);
  }, [lastFrameTime]);

  const canRunAnimation = React.useCallback((workloadTimeEstimate: number = MIN_FRAME_TIME * 0.2): boolean => {
    if (reducedMotion) {
      return false;
    }

    if (isUnderLoad) {
      return false;
    }

    const projectedWorkload = currentWorkloadRef.current + workloadTimeEstimate;

    if (projectedWorkload < budgetMs) {
      currentWorkloadRef.current = projectedWorkload;
      return true;
    }

    return false;
  }, [reducedMotion, isUnderLoad, budgetMs]);

  return {
    maxFrameTime: budgetMs,
    isUnderLoad,
    canRunAnimation,
    currentFPS,
  };
}