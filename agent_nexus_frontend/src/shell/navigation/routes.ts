import { IconName } from '@/design-system/icons/registry'

export type NavRoute = {
  label: string
  path: string
  icon: IconName
  requiresAuth?: boolean
  children?: NavRoute[]
}

const routes: NavRoute[] = [
  {
    label: 'Chat',
    path: '/chat',
    icon: 'command',
    requiresAuth: true
  },
  {
    label: 'InsightMate',
    path: '/insightmate',
    icon: 'brain',
    requiresAuth: true
  },
  {
    label: 'StudyFlow',
    path: '/studyflow',
    icon: 'memory',
    requiresAuth: true
  },
  {
    label: 'AutoAgent',
    path: '/autoagent',
    icon: 'agent',
    requiresAuth: true
  },
  {
    label: 'Dashboards',
    path: '/dashboards',
    icon: 'graph',
    requiresAuth: true,
    children: [
      {
        label: 'Agent',
        path: '/dashboards/agent',
        icon: 'agent'
      },
      {
        label: 'System',
        path: '/dashboards/system',
        icon: 'brain'
      },
      {
        label: 'Performance',
        path: '/dashboards/performance',
        icon: 'success'
      }
    ]
  }
]

export default routes
