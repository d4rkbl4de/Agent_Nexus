'use client'

import { usePathname, useRouter } from 'next/navigation'
import routes, { NavRoute } from './routes'
import NavItem from './NavItem'
import { useSession } from '@/core/hooks/useSession'

export default function NavTree() {
  const pathname = usePathname()
  const router = useRouter()
  const { session } = useSession()

  const renderRoute = (route: NavRoute, depth = 0) => {
    if (route.requiresAuth && !session) return null

    const active =
      pathname === route.path || pathname.startsWith(route.path + '/')

    return (
      <div key={route.path}>
        <NavItem
          label={route.label}
          icon={route.icon}
          active={active}
          depth={depth}
          onClick={() => router.push(route.path)}
        />
        {route.children &&
          route.children.map(child => renderRoute(child, depth + 1))}
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-1">
      {routes.map(route => renderRoute(route))}
    </div>
  )
}
