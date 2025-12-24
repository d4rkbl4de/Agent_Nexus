'use client'

import { usePathname, useRouter } from 'next/navigation'
import routes from '@/shell/navigation/routes'
import NavItem from '@/shell/navigation/NavItem'
import { useSession } from '@/core/hooks/useSession'

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { session } = useSession()

  if (!session) return null

  return (
    <aside className="flex h-full w-64 flex-col border-r bg-muted/30">
      <div className="flex h-14 items-center px-4 text-sm font-semibold">
        Agent Nexus
      </div>
      <nav className="flex-1 overflow-y-auto px-2 py-2">
        {routes.map(route => (
          <NavItem
            key={route.path}
            label={route.label}
            icon={route.icon}
            active={pathname.startsWith(route.path)}
            onClick={() => router.push(route.path)}
          />
        ))}
      </nav>
    </aside>
  )
}
