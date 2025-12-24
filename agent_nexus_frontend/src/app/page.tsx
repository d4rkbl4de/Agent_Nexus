import { Shell } from '@/shell/shell';
import { Hero } from '@/shell/hero';
import { AgentStatusDashboard } from '@/dashboards/agent-status-dashboard';
import { CommandPaletteButton } from '@/design-system/command-palette/command-palette-button';
import { MotionDiv } from '@/motion/motion-div';
import { StatusBadge } from '@/design-system/status-badge';
import { Button } from '@/design-system/button';
import Link from 'next/link';

export default function HomePage() {
  return (
    <Shell className="pt-24 pb-16">
      <MotionDiv
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      >
        <div className="text-center mb-16 space-y-4">
          <StatusBadge status="active" className="mx-auto animate-pulse-neon">
            Agent Nexus Online
          </StatusBadge>
          <Hero
            title="Distributed AI Command Console"
            subtitle="Harness the power of modular, autonomous agents with a secure, real-time interface."
          />
          <div className="flex justify-center space-x-4 pt-4">
            <Link href="/agent">
              <Button size="lg" className="shadow-glow-md">
                Launch Agent Interface
              </Button>
            </Link>
            <CommandPaletteButton />
          </div>
        </div>

        <section className="mt-20">
          <h2 className="text-3xl font-display text-nexus-primary mb-8 text-center border-b border-nexus-primary/20 pb-4">
            System Overview & Realtime Metrics
          </h2>
          <AgentStatusDashboard />
        </section>

        <section className="mt-20 text-center">
          <h2 className="text-2xl font-display text-nexus-light mb-4">
            Introspection & Debugging
          </h2>
          <p className="text-foreground/70 mb-8 max-w-2xl mx-auto">
            View detailed execution traces, token usage, and system health in real-time.
            Maintain full observability over your distributed agent network.
          </p>
          <Link href="/introspection">
            <Button variant="secondary" className="border border-nexus-secondary">
              Go to Introspection Panel
            </Button>
          </Link>
        </section>
      </MotionDiv>
    </Shell>
  );
}