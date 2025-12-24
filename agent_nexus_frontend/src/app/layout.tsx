import type { Metadata } from 'next';
import { Inter, Fira_Code, Playfair_Display } from 'next/font/google';
import { AnalyticsProvider } from '@/core/providers';
import { cn } from '@/lib/utils';
import './globals.css';

// --- Font Definitions ---
const fontSans = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
});

const fontMono = Fira_Code({
  subsets: ['latin'],
  variable: '--font-mono',
});

const fontDisplay = Playfair_Display({
  subsets: ['latin'],
  weight: ['400', '700'],
  variable: '--font-display',
});

// --- Metadata ---
export const metadata: Metadata = {
  title: 'Agent Nexus | Distributed AI Command Console',
  description: 'A platform for building, managing, and interacting with modular AI agents and distributed systems.',
  robots: 'index, follow',
  keywords: ['AI', 'Agent', 'FastAPI', 'Next.js', 'Cyberpunk', 'LLM', 'Distributed'],
};

// --- Root Layout Component ---
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <body
        className={cn(
          'min-h-screen antialiased transition-colors duration-300',
          fontSans.variable,
          fontMono.variable,
          fontDisplay.variable
        )}
      >
        {/* Core Providers wrap the application, handling context, state, and themes */}
        <AnalyticsProvider>
          <div id="root-portal-target" />
          {children}
        </AnalyticsProvider>
      </body>
    </html>
  );
}