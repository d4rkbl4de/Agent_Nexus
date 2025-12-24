'use client'

import { memo } from 'react'
import { Icon } from '@/design-system/icons/Icon'
import clsx from 'clsx'

type Props = {
  label: string
  icon: string
  active?: boolean
  depth?: number
  onClick: () => void
}

function NavItem({ label, icon, active, depth = 0, onClick }: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        'flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm transition',
        active
          ? 'bg-primary text-primary-foreground'
          : 'text-muted-foreground hover:bg-muted hover:text-foreground'
      )}
      style={{ paddingLeft: `${12 + depth * 12}px` }}
      aria-current={active ? 'page' : undefined}
    >
      <Icon name={icon} size={16} />
      <span className="truncate">{label}</span>
    </button>
  )
}

export default memo(NavItem)
