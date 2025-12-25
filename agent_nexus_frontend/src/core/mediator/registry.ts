import { EventKey, eventBus } from './eventBus';
import { Agent } from '../../contracts/agent.schema';
import { PlatformUser } from '../../contracts/user.schema';
import { AgentNexusError } from '../api/errors';

export type EntityId = string;

/**
 * Defines the standard shape of a shared state entity managed by the Registry.
 * This ensures consistency across all registered entities.
 */
interface IRegistryEntity {
  id: EntityId;
}

/**
 * Defines the structure for a handler function that processes an event.
 * T is the type of the event payload.
 */
type EventHandler<T> = (payload: T) => void;

/**
 * The Central Registry acts as the application's single source of truth for
 * in-memory caching and state derived from event streams and API calls.
 * It integrates with the EventBus to maintain consistency.
 * 
 */
class Registry {
  private agentCache: Map<EntityId, Agent> = new Map();
  private userCache: Map<EntityId, PlatformUser> = new Map();

  constructor() {
    this.setupListeners();
  }

  // --- Listener Setup ---

  private setupListeners(): void {
    // Agent Events
    eventBus.subscribe('agent:created', this.handleAgentCreated);
    eventBus.subscribe('agent:updated', this.handleAgentUpdated);
    eventBus.subscribe('agent:deleted', this.handleAgentDeleted);

    // User Events
    eventBus.subscribe('user:profileUpdated', this.handleUserProfileUpdated);
    eventBus.subscribe('user:loggedIn', this.handleUserLoggedIn);
    eventBus.subscribe('user:loggedOut', this.handleUserLoggedOut);
  }

  // --- Agent Handlers ---

  private handleAgentCreated: EventHandler<Agent> = (agent) => {
    this.agentCache.set(agent.id, agent);
  };

  private handleAgentUpdated: EventHandler<Agent> = (agent) => {
    this.agentCache.set(agent.id, { ...this.agentCache.get(agent.id), ...agent });
  };

  private handleAgentDeleted: EventHandler<{ id: string }> = ({ id }) => {
    this.agentCache.delete(id);
  };

  // --- User Handlers ---

  private handleUserLoggedIn: EventHandler<PlatformUser> = (user) => {
    this.userCache.set(user.id, user);
  };

  private handleUserProfileUpdated: EventHandler<PlatformUser> = (user) => {
    this.userCache.set(user.id, { ...this.userCache.get(user.id), ...user });
  };

  private handleUserLoggedOut: EventHandler<void> = () => {
    // Clear all user-specific data upon logout
    this.userCache.clear();
  };

  // --- Public Read Methods ---

  /** Retrieves an Agent by ID from the cache. */
  public getAgent(id: EntityId): Agent | undefined {
    return this.agentCache.get(id);
  }

  /** Retrieves all Agents from the cache as an array. */
  public getAllAgents(): Agent[] {
    return Array.from(this.agentCache.values());
  }

  /** Retrieves the currently logged-in user profile, assuming only one active user. */
  public getCurrentUser(): PlatformUser | undefined {
    // In a single-user application, the current user is the only one in the cache.
    // If the cache is empty, return undefined.
    return Array.from(this.userCache.values())[0];
  }
  
  /** Retrieves a user by ID from the cache. */
  public getUser(id: EntityId): PlatformUser | undefined {
    return this.userCache.get(id);
  }

  // --- Public Write/Initialization Methods ---

  /** Initializes or replaces the entire Agent cache (e.g., after fetching a list). */
  public initializeAgents(agents: Agent[]): void {
    this.agentCache.clear();
    agents.forEach(agent => this.agentCache.set(agent.id, agent));
  }
  
  /** Sets the current authenticated user explicitly (e.g., after successful API login). */
  public setCurrentUser(user: PlatformUser): void {
    // Ensure cleanup of any previous user data before setting the new one
    this.userCache.clear();
    this.userCache.set(user.id, user);
    eventBus.publish('user:loggedIn', user);
  }

  // --- Utility ---

  /** Clears all caches for a clean state (e.g., for full application reset). */
  public reset(): void {
    this.agentCache.clear();
    this.userCache.clear();
  }
}

// Singleton instance
export const registry = new Registry();