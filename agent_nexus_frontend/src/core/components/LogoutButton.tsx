'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/core/store/auth.store';
import { LogOut } from 'lucide-react';

const LogoutButton: React.FC = () => {
  const router = useRouter();
  const logout = useAuthStore((state) => state.logout);

  const handleLogout = () => {
    logout();
    // Redirect to login page after clearing the state
    router.replace('/login');
  };

  return (
    <button
      onClick={handleLogout}
      className="flex items-center space-x-2 text-red-500 hover:text-red-600 transition-colors py-2 px-4 rounded-lg border border-red-500 hover:border-red-600"
      aria-label="Logout"
    >
      <LogOut className="w-5 h-5" />
      <span>Logout</span>
    </button>
  );
};

export default LogoutButton;
