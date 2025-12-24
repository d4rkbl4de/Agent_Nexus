'use client'

import { ReactNode, useEffect, useState } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'
import Footer from './Footer'
import { useSession } from '@/core/hooks/useSession'

type Props = {
  children: ReactNode
}

export default function AppShell({ children }: Props) {
  const { session, status } = useSession()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted || status === 'loading') {
    return (
      <div className="flex h-screen w-screen items-center justify-center text-sm text-muted-foreground">
        Initializing application…
      </div>
    )
  }

  if (!session) {
    return (
      <div className="flex h-screen w-screen items-center justify-center text-sm text-muted-foreground">
        Unauthorized
      </div>
    )
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-auto bg-background">
          {children}
        </main>
        <Footer />
      </div>
    </div>
  )
}
