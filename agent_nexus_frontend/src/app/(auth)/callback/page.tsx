'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

export default function CallbackPage() {
  const router = useRouter()
  const params = useSearchParams()

  useEffect(() => {
    const code = params.get('code')
    const state = params.get('state')
    if (!code) {
      router.replace('/login')
      return
    }
    ;(async () => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ code, state })
      })
      if (!res.ok) {
        router.replace('/login')
        return
      }
      router.replace('/')
    })()
  }, [params, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-sm text-muted-foreground">Completing authentication…</div>
    </div>
  )
}
