import { create } from 'zustand';
import { persist, PersistOptions } from 'zustand/middleware';
import { EventPayloads } from '@/core/mediator/events';

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
}

interface AuthState {
  isLoggedIn: boolean;
  user: User | null;
  accessToken: string | null;
  _hasHydrated: boolean; 

  _internalLogin: (payload: EventPayloads['USER_LOGGED_IN']) => void;
  logout: () => void; 
}

const authPersistOptions: PersistOptions<AuthState> = {
  name: 'auth-storage',
  onRehydrateStorage: () => (state) => {
    if (state) {
        state._hasHydrated = true;
    }
  },
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isLoggedIn: false,
      user: null,
      accessToken: null,
      _hasHydrated: false, 

      _internalLogin: (payload) =>
        set({
          isLoggedIn: true,
          user: payload.user,
          accessToken: payload.accessToken,
        }),

      logout: () => {
        set({
          isLoggedIn: false,
          user: null,
          accessToken: null,
        });
      },
    }),
    authPersistOptions
  )
);