'use client'

import { memo, useEffect, useRef, useState } from 'react'

type Token = {
  id: string
  value: string
  timestamp: number
}

type TokenStreamProps = {
  source: AsyncIterable<Token> | (() => AsyncIterable<Token>)
  maxTokens?: number
  autoScroll?: boolean
}

const TokenStream = memo(function TokenStream({
  source,
  maxTokens = 1000,
  autoScroll = true
}: TokenStreamProps) {
  const [tokens, setTokens] = useState<Token[]>([])
  const containerRef = useRef<HTMLDivElement>(null)
  const cancelled = useRef(false)

  useEffect(() => {
    cancelled.current = false
    const iterator = typeof source === 'function' ? source() : source

    const consume = async () => {
      try {
        for await (const token of iterator) {
          if (cancelled.current) break
          setTokens(prev => {
            const next = [...prev, token]
            return next.length > maxTokens ? next.slice(-maxTokens) : next
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
  }, [source, maxTokens])

  useEffect(() => {
    if (!autoScroll || !containerRef.current) return
    containerRef.current.scrollTop = containerRef.current.scrollHeight
  }, [tokens, autoScroll])

  return (
    <div ref={containerRef} className="h-full w-full overflow-auto font-mono text-sm">
      {tokens.map(t => (
        <span key={t.id} className="inline-block whitespace-pre-wrap">
          {t.value}
        </span>
      ))}
    </div>
  )
})

export default TokenStream
