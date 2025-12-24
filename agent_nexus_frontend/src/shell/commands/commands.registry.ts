import { IconName } from '@/design-system/icons/registry'

export type CommandContext = {
  push: (path: string) => void
  logout: () => Promise<void>
}

export type Command = {
  id: string
  label: string
  icon: IconName
  shortcut?: string[]
  run: (ctx: CommandContext) => void | Promise<void>
}

export const commandRegistry = (): Command[] => [
  {
    id: 'nav-chat',
    label: 'Go to Chat',
    icon: 'command',
    shortcut: ['G', 'C'],
    run: ({ push }) => push('/chat')
  },
  {
    id: 'nav-insight',
    label: 'Go to InsightMate',
    icon: 'brain',
    shortcut: ['G', 'I'],
    run: ({ push }) => push('/insightmate')
  },
  {
    id: 'nav-study',
    label: 'Go to StudyFlow',
    icon: 'memory',
    shortcut: ['G', 'S'],
    run: ({ push }) => push('/studyflow')
  },
  {
    id: 'nav-autoagent',
    label: 'Go to AutoAgent',
    icon: 'agent',
    shortcut: ['G', 'A'],
    run: ({ push }) => push('/autoagent')
  },
  {
    id: 'nav-agent-dashboard',
    label: 'Open Agent Dashboard',
    icon: 'agent',
    shortcut: ['D', 'A'],
    run: ({ push }) => push('/dashboards/agent')
  },
  {
    id: 'nav-system-dashboard',
    label: 'Open System Dashboard',
    icon: 'brain',
    shortcut: ['D', 'S'],
    run: ({ push }) => push('/dashboards/system')
  },
  {
    id: 'nav-performance-dashboard',
    label: 'Open Performance Dashboard',
    icon: 'success',
    shortcut: ['D', 'P'],
    run: ({ push }) => push('/dashboards/performance')
  },
  {
    id: 'logout',
    label: 'Log out',
    icon: 'warning',
    shortcut: ['L', 'O'],
    run: async ({ logout }) => {
      await logout()
    }
  }
]
