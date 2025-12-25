import * as React from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { motion } from 'framer-motion';
import { useScheduler } from '../../motion/performance/scheduler';
import { assertExists } from '../../utils/assert';

interface AgentNode {
  id: string;
  name: string;
  type: 'agent' | 'tool' | 'data';
  status: 'running' | 'idle' | 'error' | 'complete';
  val: number; 
}

interface AgentLink {
  source: string;
  target: string;
  value: number; 
  label?: string;
}

interface AgentGraphData {
  nodes: AgentNode[];
  links: AgentLink[];
}

interface AgentGraphProps {
  graphData: AgentGraphData;
  contextLabel?: string;
  height?: number;
}

const TYPE_COLOR_MAP = {
  agent: '#10B981', 
  tool: '#3B82F6',   
  data: '#F59E0B',   
};

const STATUS_COLOR_MAP = {
  running: '#EF4444', 
  idle: '#9CA3AF',    
  error: '#DC2626',   
  complete: '#10B981', 
};

const NODE_SIZE_FACTOR = 10;
const LINK_WIDTH_FACTOR = 1;

const AgentGraph: React.FC<AgentGraphProps> = ({
  graphData,
  contextLabel = 'Agent Interaction Graph',
  height = 500,
}) => {
  const fgRef = React.useRef(null);
  const { canRunAnimation } = useScheduler();
  const [hoverNode, setHoverNode] = React.useState<AgentNode | null>(null);

  React.useEffect(() => {
    if (fgRef.current) {
      // Set simulation forces for optimal graph layout
      fgRef.current.d3Force('charge').strength(-400); 
      fgRef.current.d3Force('link').distance(70); 
    }
  }, []);

  const getNodeColor = React.useCallback((node: AgentNode) => {
    return STATUS_COLOR_MAP[node.status] || TYPE_COLOR_MAP[node.type] || '#A1A1AA';
  }, []);

  const getNodeSize = React.useCallback((node: AgentNode) => {
    return NODE_SIZE_FACTOR + (node.val * 5 || 0);
  }, []);

  const handleNodeClick = React.useCallback((node: AgentNode) => {
    assertExists(fgRef.current, 'ForceGraph reference must be defined.');
    
    // Zoom in on click
    fgRef.current.centerAndZoom(node.x, node.y, 1.5 * node.val);
  }, []);

  const handleNodeHover = React.useCallback((node: AgentNode | null) => {
    setHoverNode(node);
  }, []);

  const renderNodeCanvas = (node: AgentNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const size = getNodeSize(node) / globalScale;
    ctx.fillStyle = getNodeColor(node);
    ctx.beginPath();
    ctx.arc(node.x, node.y, size / 2, 0, 2 * Math.PI, false);
    ctx.fill();

    // Draw border on hover
    if (hoverNode && hoverNode.id === node.id) {
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 1 / globalScale;
        ctx.stroke();
    }
    
    // Draw label
    const fontSize = 12 / globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#1F2937';
    ctx.fillText(node.name, node.x, node.y + (size / 2) + (fontSize * 0.8));
  };

  const getLinkWidth = React.useCallback((link: AgentLink) => {
    return LINK_WIDTH_FACTOR + (link.value * 0.5 || 0);
  }, []);
  
  const motionProps = canRunAnimation() ? {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    transition: { duration: 0.5 },
  } : {
    initial: false,
    animate: { opacity: 1 },
    transition: { duration: 0.1 },
  };

  if (graphData.nodes.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500 border border-dashed rounded-xl bg-gray-50 h-full min-h-[300px]">
        No agent interactions recorded to build the graph.
      </div>
    );
  }

  return (
    <motion.div className="p-6 bg-white rounded-xl shadow-2xl ring-1 ring-gray-100" {...motionProps}>
      <h3 className="mb-4 text-xl font-bold text-gray-800 border-b pb-2">{contextLabel}</h3>
      <ForceGraph2D
        ref={fgRef}
        height={height}
        graphData={graphData}
        nodeLabel={(node: AgentNode) => `${node.name} (${node.type}) - ${node.status}`}
        linkWidth={getLinkWidth}
        linkColor={(link: AgentLink) => STATUS_COLOR_MAP[graphData.nodes.find(n => n.id === link.source)?.status || 'idle']}
        nodeCanvasObject={renderNodeCanvas}
        nodeCanvasObjectMode={() => 'after'}
        onNodeClick={handleNodeClick}
        onNodeHover={handleNodeHover}
        backgroundColor="#F9FAFB"
        enableNodeDrag={true}
        enableZoomPanInteraction={true}
        d3AlphaDecay={0.04} 
        d3VelocityDecay={0.2} 
        cooldownTicks={100}
      />
      {hoverNode && (
        <motion.div
          className="absolute top-2 right-2 p-2 bg-gray-800 text-white text-xs rounded shadow-md z-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <strong>{hoverNode.name}</strong> ({hoverNode.type})<br />
          Status: {hoverNode.status.toUpperCase()}<br />
          Value: {hoverNode.val}
        </motion.div>
      )}
    </motion.div>
  );
};

export default AgentGraph;