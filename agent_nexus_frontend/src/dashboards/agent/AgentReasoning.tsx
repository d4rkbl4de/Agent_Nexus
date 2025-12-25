'use client'

import { useEffect, useState } from 'react'
import { useAgent } from '@/core/hooks/useAgent'
import { Panel } from '@/design-system/layouts/Panel'
import { Stack } from '@/design-system/layouts/Stack'
import TokenStream from '@/visualization/streams/TokenStream'
import LogStream from '@/visualization/streams/LogStream'

export default function AgentReasoning() {
  const { reasoningTokens, reasoningLogs, refreshReasoning } = useAgent()
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    refreshReasoning().finally(() => setLoaded(true))
  }, [refreshReasoning])

  if (!loaded) {
    return <div className="h-full w-full animate-pulse bg-muted" />
  }

  return (
    <Panel>
      <Stack gap="md">
        <div className="text-sm font-semibold">Reasoning Execution</div>
        <div className="grid grid-cols-2 gap-4 h-[420px]">
          <div className="rounded-md border overflow-hidden">
            <TokenStream source={reasoningTokens} />
          </div>
          <div className="rounded-md border overflow-hidden">
            <LogStream source={reasoningLogs} />
          </div>
        </div>
      </Stack>
    </Panel>
  )
}
