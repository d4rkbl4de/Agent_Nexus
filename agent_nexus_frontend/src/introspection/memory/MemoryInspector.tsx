import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Memory, AgentMemory } from '../../types/agent';
import { Clock, BookOpen, Layers, Search, ChevronDown, ListPlus, Database } from 'lucide-react';
import { useScheduler } from '../../motion/performance/scheduler';
import Card from '../../shared/ui/Card';
import Input from '../../shared/ui/Input';
import Badge from '../../shared/ui/Badge';
import Button from '../../shared/ui/Button';

export interface MemoryInspectorProps {
  memoryEntries: AgentMemory[];
  isLoading?: boolean;
  onSearch?: (query: string) => void;
  onRefresh?: () => void;
}

type MemoryType = 'short_term' | 'long_term' | 'episodic';

const TYPE_ICON_MAP: Record<MemoryType, React.ReactNode> = {
  short_term: <Clock className="w-4 h-4 mr-1"/>,
  long_term: <Database className="w-4 h-4 mr-1"/>,
  episodic: <BookOpen className="w-4 h-4 mr-1"/>,
};

const MemoryEntryItem: React.FC<{ entry: AgentMemory }> = React.memo(({ entry }) => {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const { canRunAnimation } = useScheduler();

  const handleToggle = React.useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);

  const time = React.useMemo(() => new Date(entry.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }), [entry.timestamp]);
  const date = React.useMemo(() => new Date(entry.timestamp).toLocaleDateString(), [entry.timestamp]);

  const summary = entry.content.substring(0, 120) + (entry.content.length > 120 ? '...' : '');

  return (
    <Card className="p-0 overflow-hidden border border-gray-200">
      <div 
        role="button"
        tabIndex={0}
        aria-expanded={isExpanded}
        aria-controls={`memory-details-${entry.id}`}
        className="flex items-center p-4 cursor-pointer bg-white hover:bg-gray-50 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
        onClick={handleToggle}
      >
        <div className="flex-shrink-0 mr-4 text-indigo-500">
          {TYPE_ICON_MAP[entry.type] || <Layers className="w-5 h-5" />}
        </div>
        
        <div className="flex-grow min-w-0">
          <p className="text-sm text-gray-800 truncate font-medium">
            {summary}
          </p>
          <div className="flex items-center space-x-3 text-xs text-gray-500 mt-1">
            <span className="font-mono">{time} on {date}</span>
            <Badge variant="secondary" className="text-xs">{entry.type.toUpperCase().replace('_', ' ')}</Badge>
          </div>
        </div>

        <div className="flex-shrink-0 ml-4">
          <ChevronDown 
            className={`w-5 h-5 text-gray-500 transition-transform duration-200 ${isExpanded ? 'rotate-180' : 'rotate-0'}`} 
            aria-hidden="true"
          />
        </div>
      </div>
      
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            id={`memory-details-${entry.id}`}
            initial={canRunAnimation() ? { opacity: 0, height: 0 } : false}
            animate={{ opacity: 1, height: 'auto' }}
            exit={canRunAnimation() ? { opacity: 0, height: 0 } : false}
            transition={{ duration: 0.3 }}
            className="p-4 border-t border-gray-200 bg-gray-50 overflow-hidden"
          >
            <div className="text-sm space-y-3">
              <div className="font-semibold text-gray-800">Full Content:</div>
              <pre className="p-3 text-xs bg-white border border-gray-100 rounded-lg overflow-x-auto whitespace-pre-wrap font-mono text-gray-700">
                {entry.content}
              </pre>
              
              <div className="font-semibold text-gray-800 mt-3">Metadata:</div>
              {Object.keys(entry.metadata).length > 0 ? (
                <pre className="p-3 text-xs bg-white border border-gray-100 rounded-lg overflow-x-auto font-mono text-gray-700">
                  {JSON.stringify(entry.metadata, null, 2)}
                </pre>
              ) : (
                <p className="text-xs text-gray-500 italic">No associated metadata.</p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
});

const MemoryInspector: React.FC<MemoryInspectorProps> = ({ memoryEntries, isLoading = false, onSearch, onRefresh }) => {
  const [activeTab, setActiveTab] = React.useState<MemoryType | 'all'>('all');
  const [searchQuery, setSearchQuery] = React.useState('');
  const { canRunAnimation } = useScheduler();

  const handleSearchChange = React.useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  }, []);

  const handleSearchSubmit = React.useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(searchQuery);
    }
  }, [onSearch, searchQuery]);

  const filteredEntries = React.useMemo(() => {
    let entries = memoryEntries;
    
    if (activeTab !== 'all') {
      entries = entries.filter(e => e.type === activeTab);
    }

    if (searchQuery.trim() !== '') {
        const query = searchQuery.toLowerCase();
        entries = entries.filter(e => 
            e.content.toLowerCase().includes(query) || 
            (e.metadata && JSON.stringify(e.metadata).toLowerCase().includes(query))
        );
    }

    // Sort by timestamp descending
    return entries.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [memoryEntries, activeTab, searchQuery]);

  const motionProps = canRunAnimation() ? {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    transition: { duration: 0.5 },
  } : {
    initial: false,
    animate: { opacity: 1 },
    transition: { duration: 0.1 },
  };

  const tabs: { key: MemoryType | 'all'; label: string }[] = [
    { key: 'all', label: `All (${memoryEntries.length})` },
    { key: 'short_term', label: `Short Term (${memoryEntries.filter(e => e.type === 'short_term').length})` },
    { key: 'episodic', label: `Episodic (${memoryEntries.filter(e => e.type === 'episodic').length})` },
    { key: 'long_term', label: `Long Term (${memoryEntries.filter(e => e.type === 'long_term').length})` },
  ];

  return (
    <motion.div className="space-y-4" {...motionProps}>
      <Card className="p-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
          
          <form onSubmit={handleSearchSubmit} className="flex-grow w-full sm:w-auto">
            <Input
              type="search"
              placeholder="Search memory content or metadata..."
              value={searchQuery}
              onChange={handleSearchChange}
              leftIcon={<Search className="w-5 h-5"/>}
              size="md"
              className="w-full"
            />
          </form>

          <div className="flex space-x-2 flex-shrink-0">
            {onRefresh && (
              <Button 
                onClick={onRefresh} 
                variant="secondary" 
                size="md" 
                isLoading={isLoading}
                leftIcon={<ListPlus className="w-5 h-5" />}
                aria-label="Refresh memory logs"
              >
                Refresh
              </Button>
            )}
          </div>
        </div>
        
        {/* Tabs for filtering */}
        <div className="mt-4 border-b border-gray-200">
          <nav className="-mb-px flex space-x-4" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`py-2 px-3 text-sm font-medium border-b-2 transition-colors duration-150 focus:outline-none 
                  ${activeTab === tab.key
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  }`
                }
                aria-current={activeTab === tab.key ? 'page' : undefined}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </Card>
      
      {isLoading && filteredEntries.length === 0 && (
        <Card className="p-8 text-center text-indigo-600 shadow-lg" role="status" aria-live="polite">
          <Loader className="w-6 h-6 mx-auto mb-3 animate-spin" />
          <span className="font-medium">Loading memory entries...</span>
        </Card>
      )}

      {filteredEntries.length === 0 && !isLoading && (
        <Card className="p-8 text-center text-gray-500 border border-dashed rounded-xl bg-gray-50 min-h-[150px]">
          No memory entries found for the current filter and search query.
        </Card>
      )}

      <div className="space-y-3">
        {filteredEntries.map((entry) => (
          <MemoryEntryItem key={entry.id} entry={entry} />
        ))}
      </div>
    </motion.div>
  );
};

export default MemoryInspector;