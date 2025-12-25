'use client'

import { useEffect, useState } from 'react'
import { Panel } from '@/design-system/layouts/Panel'
import { Stack } from '@/design-system/layouts/Stack'
import { useSystem } from '@/core/hooks/useSystem'
import LineChart from '@/visualization/charts/LineChart'

export default function QueuePanel() {
  const { queueStats, refreshQueue } = useSystem()
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    refreshQueue().finally(() => setLoaded(true))
  }, [refreshQueue])

  if (!loaded || !queueStats) {
    return <div className="h-full w-full animate-pulse bg-muted" />
  }

  return (
    <Panel>
      <Stack gap="md">
        <div className="text-sm font-semibold">Task Queues</div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="text-xs uppercase text-muted-foreground">Pending</div>
            <div className="text-lg">{queueStats.pending}</div>
          </div>
          <div>
            <div className="text-xs uppercase text-muted-foreground">Running</div>
            <div className="text-lg">{queueStats.running}</div>
          </div>
          <div>
            <div className="text-xs uppercase text-muted-foreground">Failed</div>
            <div className="text-lg text-red-500">{queueStats.failed}</div>
          </div>
        </div>
        <div className="h-[200px]">
          <LineChart data={queueStats.history} xKey="time" yKey="depth" />
        </div>
      </Stack>
    </Panel>
  )
}
