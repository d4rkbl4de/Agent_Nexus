'use client';

import React from 'react';

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 transition-colors duration-300">
      {children}
    </div>
  );
};