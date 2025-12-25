import { create } from 'zustand';
import { eventBus } from '../mediator/eventBus';
import { PlatformUser } from '../../contracts/user.schema';

export type AppState = 'INITIALIZING' | 'UNAUTHENTICATED' | 'AUTHENTICATED' | 'ERROR';

export interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  timestamp: string;
  autoDismiss?: boolean;
}

export interface AppStore {
  state: AppState;
  globalLoading: boolean;
  activeUser: PlatformUser | null;
  notifications: Notification[];
  
  // State control
  setAppState: (state: AppState) => void;
  setGlobalLoading: (loading: boolean) => void;
  
  // User control (synced with SessionProvider)
  setActiveUser: (user: PlatformUser | null) => void;
  
  // Notification control
  addNotification: (message: string, type: Notification['type']) => void;
  dismissNotification: (id: string) => void;
}

export const useAppStore = create<AppStore>((set, get) => ({
  state: 'INITIALIZING',
  globalLoading: false,
  activeUser: null,
  notifications: [],

  setAppState: (state) => set({ state }),
  setGlobalLoading: (globalLoading) => set({ globalLoading }),

  setActiveUser: (user) => {
    set({ activeUser: user });
    if (user) {
      get().setAppState('AUTHENTICATED');
    } else if (get().state !== 'ERROR') {
      get().setAppState('UNAUTHENTICATED');
    }
  },

  addNotification: (message, type) => {
    const newNotification: Notification = {
      id: Date.now().toString(),
      message,
      type,
      timestamp: new Date().toISOString(),
      autoDismiss: type !== 'error' && type !== 'warning',
    };
    
    set((state) => ({
      notifications: [newNotification, ...state.notifications],
    }));

    if (newNotification.autoDismiss) {
      setTimeout(() => {
        get().dismissNotification(newNotification.id);
      }, 5000);
    }
  },

  dismissNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }));
  },
}));

// --- Event Bus Integration ---

const initializeEventBusListeners = () => {
  const { setActiveUser, addNotification, setAppState } = useAppStore.getState();

  eventBus.subscribe('user:loggedIn', (user) => {
    setActiveUser(user);
    addNotification(`Welcome back, ${user.email}!`, 'success');
  });

  eventBus.subscribe('user:loggedOut', () => {
    setActiveUser(null);
    addNotification('You have been logged out successfully.', 'info');
  });

  eventBus.subscribe('system:notification', ({ message, type }) => {
    addNotification(message, type);
  });

  eventBus.subscribe('system:error', ({ message, code, details }) => {
    const fullMessage = `${code}: ${message}`;
    addNotification(fullMessage, 'error');
    console.error('System Error Captured:', { code, message, details });
    
    // Potentially transition app state to ERROR on severe, unrecoverable system errors
    if (code === 'FATAL_API_ERROR') {
      setAppState('ERROR');
    }
  });
};

initializeEventBusListeners();

// --- Selector Hooks for convenience ---

export const useAppStatus = () => useAppStore((state) => ({
  state: state.state,
  loading: state.globalLoading,
  user: state.activeUser,
}));

export const useNotifications = () => useAppStore((state) => state.notifications);