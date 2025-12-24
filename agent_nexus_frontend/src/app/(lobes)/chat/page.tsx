'use client'

import { useEffect, useState } from 'react'
import ChatView from '@/lobes/chat/ChatView'

export default function ChatPage() {
  const [ready, setReady] = useState(false)

  useEffect(() => {
    setReady(true)
  }, [])

  if (!ready) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
        Initializing chat…
      </div>
    )
  }

  return (
    <div className="h-full w-full">
      <ChatView />
    </div>
  )
}
