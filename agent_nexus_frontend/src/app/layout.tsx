import React from 'react';
import { Metadata } from 'next';
import { ThemeProvider } from '../core/providers/ThemeProvider';
import { QueryProvider } from '../core/providers/QueryProvider';
import { CoreProvider } from '../core/providers/CoreProvider';
import { AuthGuard } from '../components/AuthGuard';
import './globals.css';

export const metadata: Metadata = {
  title: 'Agent Nexus Frontend',
  description: 'Cognitive Substrate for Autonomous Agents',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <CoreProvider>
          <QueryProvider>
            <ThemeProvider>
              <AuthGuard>{children}</AuthGuard>
            </ThemeProvider>
          </QueryProvider>
        </CoreProvider>
      </body>
    </html>
  );
}