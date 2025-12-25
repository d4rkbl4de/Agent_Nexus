'use client'

import { useEffect, useState } from 'react'
import { useAgent } from '@/core/hooks/useAgent'
import { Panel } from '@/design-system/layouts/Panel'
import { Stack } from '@/design-system/layouts/Stack'
import ThoughtStream from '@/visualization/streams/ThoughtStream'

export default function AgentMemory() {
  const { memoryStream, refreshMemory } = useAgent()
  const [active, setActive] = useState(false)

  useEffect(() => {
    refreshMemory().finally(() => setActive(true))
  }, [refreshMemory])

  if (!active) {
    return <div className="h-full w-full animate-pulse bg-muted" />
  }

  return (
    <Panel>
      <Stack gap="sm">
        <div className="text-sm font-semibold">Memory Trace</div>
        <div className="h-[400px] rounded-md border">
          <ThoughtStream source={memoryStream} />
        </div>
      </Stack>
    </Panel>
  )
}
