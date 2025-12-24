import * as React from 'react';
import { useFrameBudget } from './frameBudget';

type Task = () => void;
type TaskPriority = 'high' | 'low';

const useIdleCallback = typeof window !== 'undefined' && window.requestIdleCallback ? window.requestIdleCallback : (fn: (deadline: { didTimeout: boolean }) => void) => setTimeout(fn, 1);
const cancelIdleCallback = typeof window !== 'undefined' && window.cancelIdleCallback ? window.cancelIdleCallback : (handle: number) => clearTimeout(handle);

export function useScheduler() {
  const budget = useFrameBudget();
  const queueRef = React.useRef<{ task: Task; priority: TaskPriority }[]>([]);
  const idleHandleRef = React.useRef<number | null>(null);

  const processQueue = React.useCallback((deadline?: { didTimeout: boolean }) => {
    const startTime = performance.now();
    
    while (queueRef.current.length > 0) {
      const { task, priority } = queueRef.current[0];

      if (
        (deadline && deadline.timeRemaining <= 0 && !deadline.didTimeout) ||
        (performance.now() - startTime) >= budget.maxFrameTime ||
        (priority === 'low' && budget.isUnderLoad)
      ) {
        break;
      }

      task();
      queueRef.current.shift();
    }

    if (queueRef.current.length > 0) {
      idleHandleRef.current = useIdleCallback(processQueue);
    } else {
      idleHandleRef.current = null;
    }
  }, [budget.isUnderLoad, budget.maxFrameTime]);

  const scheduleTask = React.useCallback((task: Task, priority: TaskPriority = 'low') => {
    queueRef.current.push({ task, priority });
    
    if (idleHandleRef.current === null) {
      idleHandleRef.current = useIdleCallback(processQueue);
    }
  }, [processQueue]);

  const cancelAll = React.useCallback(() => {
    if (idleHandleRef.current !== null) {
      cancelIdleCallback(idleHandleRef.current);
      idleHandleRef.current = null;
    }
    queueRef.current = [];
  }, []);

  React.useEffect(() => {
    return () => {
      cancelAll();
    };
  }, [cancelAll]);

  return {
    scheduleTask,
    cancelAll,
    isIdle: queueRef.current.length === 0,
    currentFPS: budget.currentFPS,
    isUnderLoad: budget.isUnderLoad,
    canRunAnimation: budget.canRunAnimation,
  };
}