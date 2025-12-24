import { 
  Menu, 
  Settings, 
  X, 
  Cpu, 
  LayoutDashboard, 
  Zap, 
  Database, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  Search, 
  MessageSquare, 
  BarChart4,
  ArrowRight
} from 'lucide-react';

export type Icon = React.ForwardRefExoticComponent<Omit<React.SVGProps<SVGSVGElement>, "ref"> & {
    title?: string | undefined;
    titleId?: string | undefined;
} & React.RefAttributes<SVGSVGElement>>;

export const Icons = {
  // Navigation & UI
  menu: Menu,
  settings: Settings,
  close: X,
  search: Search,
  arrowRight: ArrowRight,

  // Core System & Agents
  cpu: Cpu,
  agent: Cpu, // Alias for Agent icon
  dashboard: LayoutDashboard,
  performance: Zap, // For performance metrics
  database: Database,
  clock: Clock,

  // Lobes
  chat: MessageSquare,
  insight: BarChart4, // For data analysis/insight generation

  // Status & Alerts
  warning: AlertTriangle,
  success: CheckCircle,
};