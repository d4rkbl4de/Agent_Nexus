'use client'

import { useEffect, useState } from 'react'
import { Panel } from '@/design-system/layouts/Panel'
import { Stack } from '@/design-system/layouts/Stack'
import { useSystem } from '@/core/hooks/useSystem'
import BarChart from '@/visualization/charts/BarChart'

export default function DatabasePanel() {
  const { database, refreshDatabase } = useSystem()
  const [ready, setReady] = useState(false)

  useEffect(() => {
    refreshDatabase().finally(() => setReady(true))
  }, [refreshDatabase])

  if (!ready || !database) {
    return <div className="h-full w-full animate-pulse bg-muted" />
  }

  return (
    <Panel>
      <Stack gap="md">
        <div className="text-sm font-semibold">Database</div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs uppercase text-muted-foreground">Status</div>
            <div
              className={`text-sm ${
                database.status === 'online'
                  ? 'text-green-500'
                  : 'text-red-500'
              }`}
            >
              {database.status}
            </div>
          </div>
          <div>
            <div className="text-xs uppercase text-muted-foreground">Latency</div>
            <div className="text-sm">{database.latency} ms</div>
          </div>
          <div>
            <div className="text-xs uppercase text-muted-foreground">Connections</div>
            <div className="text-sm">{database.connections}</div>
          </div>
          <div>
            <div className="text-xs uppercase text-muted-foreground">Size</div>
            <div className="text-sm">{database.sizeGb} GB</div>
          </div>
        </div>
        <div className="h-[200px]">
          <BarChart data={database.tables} xKey="table" yKey="rows" />
        </div>
      </Stack>
    </Panel>
  )
}
