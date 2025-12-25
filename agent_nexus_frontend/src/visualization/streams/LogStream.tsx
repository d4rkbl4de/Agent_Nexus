'use client'

import { memo, useEffect, useRef, useState } from 'react'

type LogLevel = 'debug' | 'info' | 'warn' | 'error'

type LogEntry = {
  id: string
  level: LogLevel
  message: string
  timestamp: number
}

type LogStreamProps = {
  source: AsyncIterable<LogEntry> | (() => AsyncIterable<LogEntry>)
  maxEntries?: number
}

const levelStyle: Record<LogLevel, string> = {
  debug: 'text-slate-400',
  info: 'text-sky-400',
  warn: 'text-amber-400',
  error: 'text-red-500'
}

const LogStream = memo(function LogStream({
  source,
  maxEntries = 1000
}: LogStreamProps) {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const cancelled = useRef(false)

  useEffect(() => {
    cancelled.current = false
    const iterator = typeof source === 'function' ? source() : source

    const consume = async () => {
      try {
        for await (const entry of iterator) {
          if (cancelled.current) break
          setLogs(prev => {
            const next = [...prev, entry]
            return next.length > maxEntries ? next.slice(-maxEntries) : next
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
  }, [source, maxEntries])

  return (
    <div className="flex flex-col gap-1 overflow-auto font-mono text-xs">
      {logs.map(l => (
        <div key={l.id} className={levelStyle[l.level]}>
          {l.message}
        </div>
      ))}
    </div>
  )
})

export default LogStream
