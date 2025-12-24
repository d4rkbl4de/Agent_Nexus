export interface Shortcut {
  key: string;
  commandId: string;
  description: string;
  display: string;
  global: boolean;
}

export const KEY_MAP: Shortcut[] = [

  {
    key: 'k',
    commandId: 'command.openPalette',
    description: 'Open Command Palette',
    display: '⌘K',
    global: true,
  },
  {
    key: 'i',
    commandId: 'navigation.toggleSidebar',
    description: 'Toggle Sidebar Navigation',
    display: '⌘I',
    global: true,
  },
  {
    key: 't',
    commandId: 'theme.toggle',
    description: 'Toggle Color Theme',
    display: '⌘T',
    global: true,
  },
  {
    key: 'n',
    commandId: 'agent.create',
    description: 'Create New Agent Instance',
    display: '⌘N',
    global: true,
  },
  

  {
    key: '1',
    commandId: 'navigation.toSystemDashboard',
    description: 'Go to System Dashboard',
    display: '⌘1',
    global: true,
  },
  {
    key: '2',
    commandId: 'navigation.toAgentDashboard',
    description: 'Go to Agent Dashboard',
    display: '⌘2',
    global: true,
  },
  {
    key: '3',
    commandId: 'navigation.toPerformanceDashboard',
    description: 'Go to Performance Dashboard',
    display: '⌘3',
    global: true,
  },
  

  {
    key: '4',
    commandId: 'navigation.toChatLobe',
    description: 'Go to Chat Lobe (Chat Buddy)',
    display: '⌘4',
    global: true,
  },
  {
    key: '5',
    commandId: 'navigation.toInsightLobe',
    description: 'Go to Insight Lobe (Insight Mate)',
    display: '⌘5',
    global: true,
  },
  

  {
    key: '/',
    commandId: 'input.focus',
    description: 'Focus Input/Search Bar',
    display: '/',
    global: true,
  },
  {
    key: 'enter',
    commandId: 'chat.sendMessage',
    description: 'Send Message (in Chat Lobe)',
    display: 'Enter',
    global: false,
  },
  {
    key: 'escape',
    commandId: 'ui.closeModal',
    description: 'Close Modal / Escape Context',
    display: 'Esc',
    global: true,
  },
];