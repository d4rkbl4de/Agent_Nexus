'use client'

import { useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'

export default function RegisterPage() {
  const router = useRouter()
  const [pending, startTransition] = useTransition()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)

  const submit = () => {
    if (password !== confirm) {
      setError('Passwords do not match')
      return
    }
    setError(null)
    startTransition(async () => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      if (!res.ok) {
        const data = await res.json().catch(() => null)
        setError(data?.detail ?? 'Registration failed')
        return
      }
      router.replace('/login')
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-sm space-y-6">
        <h1 className="text-2xl font-semibold">Create account</h1>
        {error && <div className="text-sm text-destructive">{error}</div>}
        <input
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="Email"
          className="w-full rounded border px-3 py-2 bg-transparent"
        />
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="Password"
          className="w-full rounded border px-3 py-2 bg-transparent"
        />
        <input
          type="password"
          value={confirm}
          onChange={e => setConfirm(e.target.value)}
          placeholder="Confirm password"
          className="w-full rounded border px-3 py-2 bg-transparent"
        />
        <button
          disabled={pending}
          onClick={submit}
          className="w-full rounded bg-primary text-primary-foreground py-2 disabled:opacity-50"
        >
          {pending ? 'Creating…' : 'Create account'}
        </button>
      </div>
    </div>
  )
}
