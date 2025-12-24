'use client'

import { useEffect, useState } from 'react'
import StudyPlanner from '@/lobes/studyflow/StudyPlanner'
import KnowledgeGraph from '@/lobes/studyflow/KnowledgeGraph'

export default function StudyFlowPage() {
  const [active, setActive] = useState(false)

  useEffect(() => {
    setActive(true)
  }, [])

  if (!active) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
        Preparing study environment…
      </div>
    )
  }

  return (
    <div className="flex h-full w-full flex-col gap-4">
      <StudyPlanner />
      <div className="flex-1 overflow-hidden">
        <KnowledgeGraph />
      </div>
    </div>
  )
}
