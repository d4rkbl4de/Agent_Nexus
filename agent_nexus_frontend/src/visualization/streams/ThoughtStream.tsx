'use client'

import { memo, useEffect, useRef, useState } from 'react'

type Thought = {
  id: string
  content: string
  level: 'info' | 'reasoning' | 'decision'
  timestamp: number
}

type ThoughtStreamProps = {
  source: AsyncIterable<Thought> | (() => AsyncIterable<Thought>)
  maxItems?: number
}

const levelClass: Record<Thought['level'], string> = {
  info: 'text-slate-400',
  reasoning: 'text-sky-400',
  decision: 'text-emerald-400'
}

const ThoughtStream = memo(function ThoughtStream({
  source,
  maxItems = 500
}: ThoughtStreamProps) {
  const [items, setItems] = useState<Thought[]>([])
  const cancelled = useRef(false)

  useEffect(() => {
    cancelled.current = false
    const iterator = typeof source === 'function' ? source() : source

    const consume = async () => {
      try {
        for await (const thought of iterator) {
          if (cancelled.current) break
          setItems(prev => {
            const next = [...prev, thought]
            return next.length > maxItems ? next.slice(-maxItems) : next
          })
        }
      } catch {
        cancelled.current = true
      }
    }

    consume()
    return () => {
      cancelled.current = true
    }
  }, [source, maxItems])

  return (
    <div className="flex flex-col gap-2 overflow-auto font-mono text-sm">
      {items.map(t => (
        <div key={t.id} className={levelClass[t.level]}>
          {t.content}
        </div>
      ))}
    </div>
  )
})

export default ThoughtStream
