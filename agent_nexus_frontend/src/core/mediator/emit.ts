import { EventType, EventPayloads, EventHandler } from './events';

const listeners = new Map<EventType, Set<EventHandler<any>>>();

export const subscribe = <T extends EventType>(
  event: T, 
  handler: EventHandler<T>
): () => void => {
  if (!listeners.has(event)) {
    listeners.set(event, new Set());
  }
  
  listeners.get(event)?.add(handler);

  return () => {
    listeners.get(event)?.delete(handler);
  };
};

export const emit = <T extends EventType>(
  event: T, 
  payload: EventPayloads[T]
): void => {
  const eventListeners = listeners.get(event);
  
  if (eventListeners) {
    eventListeners.forEach(handler => {
      handler(payload);
    });
  }
};