import { Agent } from '../../contracts/agent.schema';
import { StudyVariant } from '../../contracts/study.schema';
import { PlatformUser } from '../../contracts/user.schema';

export type EventPayloads = {
  'agent:created': Agent;
  'agent:updated': Agent;
  'agent:deleted': { id: string };
  'agent:deployed': { id: string; status: 'live' | 'failed' };

  'study:started': { id: string; variants: StudyVariant[] };
  'study:completed': { id: string; winningVariantId?: string };
  'study:update': { id: string; progress: number };

  'user:loggedIn': PlatformUser;
  'user:loggedOut': void;
  'user:profileUpdated': PlatformUser;

  'system:notification': { message: string; type: 'success' | 'error' | 'warning' | 'info' };
  'system:error': { code: string; message: string; details?: any };

  'chat:sessionCreated': { sessionId: string; agentId: string };
  'chat:messageReceived': { sessionId: string; message: any };
};

export type EventKey = keyof EventPayloads;

export type EventCallback<K extends EventKey> = (payload: EventPayloads[K]) => void;

class EventBus {
  private listeners: Map<EventKey, Set<EventCallback<any>>> = new Map();

  public subscribe<K extends EventKey>(event: K, callback: EventCallback<K>): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    const callbacks = this.listeners.get(event) as Set<EventCallback<K>>;
    callbacks.add(callback);

    return () => this.unsubscribe(event, callback);
  }

  public unsubscribe<K extends EventKey>(event: K, callback: EventCallback<K>): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.delete(callback);
      if (callbacks.size === 0) {
        this.listeners.delete(event);
      }
    }
  }

  public publish<K extends EventKey>(event: K, payload: EventPayloads[K]): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(payload);
        } catch (error) {
          // Internal error handling for listener failures to prevent cascade failures
          console.error(`EventBus: Error executing listener for event '${event}':`, error);
          this.publish('system:error', {
            code: 'EVENTBUS_LISTENER_FAILURE',
            message: `Event listener for ${event} failed.`,
            details: { listenerError: error, eventPayload: payload },
          });
        }
      });
    }
  }

  // Utility to clear all listeners (useful for testing or application shutdown)
  public clearAll(): void {
    this.listeners.clear();
  }
}

// Singleton instance to be used application-wide
export const eventBus = new EventBus();