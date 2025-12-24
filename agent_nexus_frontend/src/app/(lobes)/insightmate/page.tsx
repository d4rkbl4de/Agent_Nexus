'use client'

import { useEffect, useState } from 'react'
import InsightPanel from '@/lobes/insightmate/InsightPanel'
import SummaryView from '@/lobes/insightmate/SummaryView'

export default function InsightMatePage() {
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    setHydrated(true)
  }, [])

  if (!hydrated) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
        Loading InsightMate…
      </div>
    )
  }

  return (
    <div className="grid h-full grid-cols-1 lg:grid-cols-2 gap-4">
      <InsightPanel />
      <SummaryView />
    </div>
  )
}
