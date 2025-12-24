'use client';

import * as React from 'react';
import { useSidebarStore } from '@/core/store/app.store';
import { useShortcutListener } from './shortcuts/listener';
import { CommandPalette } from './commands/CommandPalette';
import { cn } from '@/lib/utils';
import { Icons } from '@/design-system/icons';

interface ShellProps {
  children: React.ReactNode;
  Sidebar: React.ComponentType<{ isOpen: boolean }>;
  Header: React.ComponentType;
}

export function Shell({ children, Sidebar, Header }: ShellProps) {
  const { isSidebarOpen, toggleSidebar } = useSidebarStore((state) => ({
    isSidebarOpen: state.isSidebarOpen,
    toggleSidebar: state.toggleSidebar,
  }));
  
  // Activate global keyboard shortcuts (e.g., Cmd+K for CommandPalette)
  useShortcutListener();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-nexus-dark text-foreground">
      {/* 1. Sidebar */}
      <aside
        className={cn(
          'flex-shrink-0 border-r border-nexus-primary/20 transition-all duration-300 ease-in-out',
          isSidebarOpen ? 'w-64' : 'w-0 overflow-hidden'
        )}
      >
        <Sidebar isOpen={isSidebarOpen} />
      </aside>

      {/* 2. Main Content Area */}
      <main className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="flex-shrink-0 border-b border-nexus-primary/20">
          <Header />
        </header>

        {/* Content Area */}
        <div className="relative flex-1 overflow-y-auto p-8">
          {children}

          {/* Sidebar Toggle Button (when closed) */}
          {!isSidebarOpen && (
            <button
              onClick={toggleSidebar}
              className="absolute top-4 left-4 p-2 rounded-full bg-nexus-dark/80 border border-nexus-primary/50 text-nexus-primary shadow-neon-sm hover:bg-nexus-primary/20 transition-colors z-50"
              aria-label="Open Sidebar"
            >
              <Icons.menu className="h-5 w-5" />
            </button>
          )}
        </div>
      </main>

      {/* 3. Global Modals/Tools */}
      <CommandPalette />
      {/* <ToastProvider /> (To be implemented later) */}
    </div>
  );
}