import { Logger } from '../utils/logger';
import * as React from 'react';

const logger = new Logger('Profiler');

export interface ProfileResult {
  name: string;
  duration: number;
  timestamp: number;
  unit: 'ms';
  threshold_ms?: number;
}

const GLOBAL_PROFILER_CONFIG = {
  ENABLED: process.env.NODE_ENV === 'development' || process.env.NEXT_PUBLIC_PROFILER_ENABLED === 'true',
  DEFAULT_WARN_THRESHOLD_MS: 16.7,
  ENABLED_NAMES: new Set<string>((process.env.NEXT_PUBLIC_PROFILER_NAMES || '').split(',').filter(Boolean)),
};

export function profileFunction<T>(
  name: string,
  func: () => T,
  thresholdMs: number = GLOBAL_PROFILER_CONFIG.DEFAULT_WARN_THRESHOLD_MS
): T {
  if (!GLOBAL_PROFILER_CONFIG.ENABLED) {
    return func();
  }
  
  if (GLOBAL_PROFILER_CONFIG.ENABLED_NAMES.size > 0 && !GLOBAL_PROFILER_CONFIG.ENABLED_NAMES.has(name)) {
    return func();
  }

  const start = performance.now();
  let result: T;
  let error: unknown = null;
  
  try {
    result = func();
  } catch (e) {
    error = e;
    throw e;
  } finally {
    const end = performance.now();
    const duration = end - start;
    const timestamp = start;

    const profileResult: ProfileResult = {
      name,
      duration,
      timestamp,
      unit: 'ms',
      threshold_ms: thresholdMs,
    };

    if (duration > thresholdMs) {
      logger.warn(`HIGH LATENCY: ${name} took ${duration.toFixed(2)}ms (Threshold: ${thresholdMs.toFixed(2)}ms)`, profileResult);
    } else {
      logger.debug(`${name} finished in ${duration.toFixed(2)}ms`, profileResult);
    }
    
    if (error) {
      logger.error(`PROFILER ERROR in ${name}`, error, profileResult);
    }
  }

  return result;
}

export function useProfiler(
  componentName: string,
  thresholdMs: number = GLOBAL_PROFILER_CONFIG.DEFAULT_WARN_THRESHOLD_MS
): void {
  const isFirstRender = React.useRef(true);

  if (!GLOBAL_PROFILER_CONFIG.ENABLED) {
    return;
  }
  
  if (GLOBAL_PROFILER_CONFIG.ENABLED_NAMES.size > 0 && !GLOBAL_PROFILER_CONFIG.ENABLED_NAMES.has(componentName)) {
    return;
  }

  const name = `RENDER:${componentName}`;
  const startTimeRef = React.useRef<number>(performance.now());
  
  React.useEffect(() => {
    const duration = performance.now() - startTimeRef.current;
    
    const profileResult: ProfileResult = {
      name,
      duration,
      timestamp: startTimeRef.current,
      unit: 'ms',
      threshold_ms: thresholdMs,
    };

    if (isFirstRender.current) {
        logger.debug(`${name} mounted in ${duration.toFixed(2)}ms`, profileResult);
        isFirstRender.current = false;
    } else {
        if (duration > thresholdMs) {
            logger.warn(`HIGH LATENCY UPDATE: ${name} updated in ${duration.toFixed(2)}ms`, profileResult);
        } else {
            logger.debug(`${name} updated in ${duration.toFixed(2)}ms`, profileResult);
        }
    }
    
    return () => {
      startTimeRef.current = performance.now();
    };
  }, [componentName, thresholdMs]);
}

export function useProfileCallback<T extends (...args: unknown[]) => unknown>(
  name: string,
  callback: T,
  thresholdMs: number = GLOBAL_PROFILER_CONFIG.DEFAULT_WARN_THRESHOLD_MS
): T {
  const profiledCallback = React.useCallback((...args: unknown[]) => {
    return profileFunction(name, () => callback(...args), thresholdMs);
  }, [name, callback, thresholdMs]);

  return profiledCallback as T;
}