'use client'

import { useEffect, useState } from 'react'
import PlannerView from '@/lobes/autoagent/PlannerView'
import ToolRunner from '@/lobes/autoagent/ToolRunner'
import ExecutionLog from '@/lobes/autoagent/ExecutionLog'

export default function AutoAgentPage() {
  const [booted, setBooted] = useState(false)

  useEffect(() => {
    setBooted(true)
  }, [])

  if (!booted) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
        Booting autonomous agent…
      </div>
    )
  }

  return (
    <div className="grid h-full grid-rows-[auto_1fr_auto] gap-4">
      <PlannerView />
      <ToolRunner />
      <ExecutionLog />
    </div>
  )
}
