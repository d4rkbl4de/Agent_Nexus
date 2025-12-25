import * as React from 'react';
import { Agent, AgentConfiguration, AgentStatus, AgentTool, ToolType } from '../../types/agent';
import { Cpu, Zap, Settings, Clock, CheckCircle, XCircle, Code, DollarSign, Package } from 'lucide-react';
import Card from '../../shared/ui/Card';
import Badge from '../../shared/ui/Badge';
import Tooltip from '../../shared/ui/Tooltip';

interface AgentIdentityProps {
  agent: Agent;
}

const STATUS_COLOR_MAP: Record<AgentStatus, string> = {
  idle: 'bg-gray-200 text-gray-700',
  running: 'bg-indigo-100 text-indigo-700 animate-pulse',
  paused: 'bg-yellow-100 text-yellow-700',
  error: 'bg-red-100 text-red-700',
  complete: 'bg-green-100 text-green-700',
};

const TOOL_TYPE_ICON_MAP: Record<ToolType, React.ReactNode> = {
  api: <Zap className="w-4 h-4 mr-1"/>,
  internal: <Code className="w-4 h-4 mr-1"/>,
  database: <Package className="w-4 h-4 mr-1"/>,
  file_system: <FileText className="w-4 h-4 mr-1"/>,
};

const ConfigurationDetail: React.FC<{ icon: React.ReactNode; label: string; value: string | number }> = ({ icon, label, value }) => (
  <div className="flex items-center text-sm text-gray-700">
    <Tooltip label={label} position="top">
      <span className="flex-shrink-0 mr-2 text-indigo-500">{icon}</span>
    </Tooltip>
    <div className="flex flex-col min-w-0">
      <span className="font-medium truncate">{label}:</span>
      <span className="text-gray-900 font-mono text-xs">{value}</span>
    </div>
  </div>
);

const AgentToolItem: React.FC<{ tool: AgentTool }> = ({ tool }) => {
  const Icon = TOOL_TYPE_ICON_MAP[tool.type] || <Package className="w-4 h-4 mr-1"/>;
  const statusIcon = tool.is_enabled ? <CheckCircle className="w-4 h-4 text-green-500"/> : <XCircle className="w-4 h-4 text-red-500"/>;

  return (
    <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg bg-white hover:shadow-sm transition-shadow duration-150">
      <div className="flex items-center min-w-0 space-x-2">
        <Tooltip label={tool.type.toUpperCase()} position="top">
            {Icon}
        </Tooltip>
        <div className="truncate text-sm font-medium text-gray-800">
          {tool.name}
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <Tooltip label={tool.is_enabled ? 'Enabled' : 'Disabled'} position="top">
          {statusIcon}
        </Tooltip>
        <Badge variant="secondary" className="text-xs">{tool.type.toUpperCase()}</Badge>
      </div>
    </div>
  );
};

const AgentIdentity: React.FC<AgentIdentityProps> = ({ agent }) => {
  const statusClass = STATUS_COLOR_MAP[agent.status] || STATUS_COLOR_MAP.idle;
  
  const formattedDate = React.useMemo(() => {
    return new Date(agent.created_at).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }, [agent.created_at]);

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-start justify-between border-b pb-4 mb-4">
          <div className="min-w-0 pr-4">
            <h1 className="text-3xl font-extrabold text-gray-900 truncate">{agent.name}</h1>
            <p className="mt-1 text-sm text-gray-500 font-mono">ID: {agent.id}</p>
          </div>
          <div className="flex-shrink-0">
            <Badge className={`text-base font-semibold px-3 py-1 ${statusClass}`}>
              {agent.status.toUpperCase()}
            </Badge>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-2 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-indigo-500"/> Description
            </h2>
            <p className="text-gray-600 leading-relaxed italic border-l-4 border-indigo-200 pl-3">
              {agent.description || 'No detailed description provided for this agent.'}
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <ConfigurationDetail 
              icon={<Clock className="w-4 h-4"/>} 
              label="Created On" 
              value={formattedDate} 
            />
            <ConfigurationDetail 
              icon={<Settings className="w-4 h-4"/>} 
              label="Last Updated" 
              value={new Date(agent.updated_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit'})} 
            />
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <Cpu className="w-5 h-5 mr-2 text-indigo-500"/> Configuration Parameters
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-y-4 gap-x-6">
          <ConfigurationDetail 
            icon={<Code className="w-4 h-4"/>} 
            label="Model Name" 
            value={agent.config.model_name} 
          />
          <ConfigurationDetail 
            icon={<Zap className="w-4 h-4"/>} 
            label="Temperature" 
            value={agent.config.temperature} 
          />
          <ConfigurationDetail 
            icon={<DollarSign className="w-4 h-4"/>} 
            label="Max Tokens" 
            value={agent.config.max_tokens} 
          />
        </div>
        <div className="mt-4 pt-4 border-t border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">System Prompt:</h3>
            <pre className="p-3 text-xs bg-gray-50 border border-gray-100 rounded-lg overflow-x-auto whitespace-pre-wrap font-mono text-gray-700">
                {agent.config.system_prompt || 'No system prompt defined.'}
            </pre>
        </div>
      </Card>
      
      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <Briefcase className="w-5 h-5 mr-2 text-indigo-500"/> Available Tools ({agent.tools.length})
        </h2>
        <div className="space-y-2">
          {agent.tools.length > 0 ? (
            agent.tools.map(tool => (
              <AgentToolItem key={tool.id} tool={tool} />
            ))
          ) : (
            <p className="text-gray-500 italic">This agent is configured with no external tools.</p>
          )}
        </div>
      </Card>
    </div>
  );
};

export default AgentIdentity;