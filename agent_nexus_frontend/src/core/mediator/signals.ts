import { useState, useEffect, useCallback, useMemo } from 'react';
import { eventBus, EventKey, EventPayloads } from './eventBus';

type SignalStore = {
  [K in EventKey]?: {
    version: number;
    payload: EventPayloads[K];
  };
};

const signalStore: SignalStore = {};

const initializeSignals = () => {
  const allEventKeys: EventKey[] = [
    'agent:created', 'agent:updated', 'agent:deleted', 'agent:deployed',
    'study:started', 'study:completed', 'study:update',
    'user:loggedIn', 'user:loggedOut', 'user:profileUpdated',
    'system:notification', 'system:error',
    'chat:sessionCreated', 'chat:messageReceived',
  ];

  allEventKeys.forEach(event => {
    eventBus.subscribe(event as EventKey, (payload: EventPayloads[typeof event]) => {
      const current = signalStore[event] || { version: 0, payload: null };
      
      signalStore[event] = {
        version: current.version + 1,
        payload: payload,
      };
      
      eventBus.publish('system:notification', {
        message: `Signal updated for ${event}`,
        type: 'info',
      });
    });
  });
};

initializeSignals();

export function useSignal<K extends EventKey>(event: K): [EventPayloads[K] | undefined, number, () => void] {
  const [version, setVersion] = useState(0);
  const eventRef = useState(event)[0];
  
  const getLatest = useCallback(() => {
    const signal = signalStore[eventRef] as SignalStore[K];
    return {
      payload: signal?.payload,
      version: signal?.version || 0,
    };
  }, [eventRef]);
  
  const initial = getLatest();
  const [currentPayload, setCurrentPayload] = useState<EventPayloads[K] | undefined>(initial.payload);

  useEffect(() => {
    const unsubscribe = eventBus.subscribe('system:notification', () => {
      const latest = getLatest();
      
      if (latest.version !== version) {
        setVersion(latest.version);
        setCurrentPayload(latest.payload);
      }
    });

    return () => {
      unsubscribe();
    };
  }, [getLatest, version]);
  
  const unsubscribeFunction = useCallback(() => {
  }, []);


  return useMemo(() => [
    currentPayload, 
    version, 
    unsubscribeFunction
  ], [currentPayload, version, unsubscribeFunction]);
}