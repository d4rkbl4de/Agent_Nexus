@'
'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/core/store/auth.store';

interface AuthGuardProps {
  children: React.ReactNode;
}

const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const router = useRouter();
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn);
  const isHydrated = useAuthStore((state) => state._hasHydrated);

  useEffect(() => {
    if (isHydrated && !isLoggedIn) {
      router.replace('/login');
    }
  }, [isLoggedIn, isHydrated, router]);

  if (!isLoggedIn) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-xl text-gray-500">Redirecting to login...</p>
      </div>
    );
  }

  return <>{children}</>;
};

export default AuthGuard;
'@ | Out-File -FilePath src/components/AuthGuard.tsx -Encoding UTF8 -Force