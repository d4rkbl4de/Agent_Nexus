import * as React from 'react';
import { motion } from 'framer-motion';
import { useScheduler } from '../../motion/performance/scheduler';
import { assertExists } from '../../utils/assert';
import * as dagre from 'dagre';

interface Node {
  id: string;
  label: string;
  type: 'module' | 'service' | 'data_source' | 'task';
  status: 'resolved' | 'unresolved' | 'cyclic';
  width: number;
  height: number;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

interface DependencyGraphData {
  nodes: Node[];
  edges: Edge[];
}

interface DependencyGraphProps {
  graphData: DependencyGraphData;
  contextLabel?: string;
  width?: number;
  height?: number;
  nodePadding?: number; 
}

const TYPE_COLOR_MAP: { [key: string]: string } = {
  module: '#3B82F6', 
  service: '#10B981', 
  data_source: '#F59E0B', 
  task: '#8B5CF6', 
};

const STATUS_BORDER_MAP: { [key: string]: string } = {
  resolved: 'ring-2 ring-green-500/80',
  unresolved: 'ring-2 ring-red-500/80',
  cyclic: 'ring-2 ring-yellow-500/80',
};

const DEFAULT_NODE_SIZE = { width: 120, height: 40 };

const useDagreLayout = (
  graphData: DependencyGraphData,
  nodePadding: number
) => {
  return React.useMemo(() => {
    const g = new dagre.graphlib.Graph();
    g.setGraph({ rankdir: 'LR', nodesep: 50, ranksep: 50, marginx: nodePadding, marginy: nodePadding });
    g.setDefaultNodeLabel(() => ({}));

    graphData.nodes.forEach(node => {
      g.setNode(node.id, { 
        ...node, 
        width: node.width || DEFAULT_NODE_SIZE.width, 
        height: node.height || DEFAULT_NODE_SIZE.height 
      });
    });

    graphData.edges.forEach(edge => {
      g.setEdge(edge.source, edge.target, {});
    });

    dagre.layout(g);

    const layoutNodes = graphData.nodes.map(node => {
      const gNode = g.node(node.id);
      return {
        ...node,
        x: gNode.x,
        y: gNode.y,
        width: gNode.width,
        height: gNode.height,
      };
    });

    const layoutEdges = graphData.edges.map(edge => {
      const gEdge = g.edge(edge.source, edge.target);
      return {
        ...edge,
        points: gEdge.points,
      };
    });

    return {
      nodes: layoutNodes,
      edges: layoutEdges,
      width: g.graph().width || 0,
      height: g.graph().height || 0,
    };
  }, [graphData.nodes, graphData.edges, nodePadding]);
};

const DependencyGraph: React.FC<DependencyGraphProps> = ({
  graphData,
  contextLabel = 'Module Dependency Graph',
  width = 800,
  height = 500,
  nodePadding = 40,
}) => {
  const { nodes, edges, width: graphWidth, height: graphHeight } = useDagreLayout(graphData, nodePadding);
  const { canRunAnimation } = useScheduler();

  const svgRef = React.useRef<SVGSVGElement>(null);

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
        No dependency nodes available to render the graph.
      </div>
    );
  }

  const viewBoxWidth = graphWidth + 2 * nodePadding;
  const viewBoxHeight = graphHeight + 2 * nodePadding;

  return (
    <motion.div className="p-6 bg-white rounded-xl shadow-2xl ring-1 ring-gray-100" {...motionProps}>
      <h3 className="mb-4 text-xl font-bold text-gray-800 border-b pb-2">{contextLabel}</h3>
      <div className="overflow-auto" style={{ width, height }}>
        <svg
          ref={svgRef}
          width={viewBoxWidth}
          height={viewBoxHeight}
          viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
          className="bg-gray-50"
        >
          {/* Edges */}
          {edges.map((edge) => {
            assertExists(edge.points, `Edge points must exist for edge ${edge.source}->${edge.target}`);
            const d = edge.points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

            const markerId = `arrowhead-${edge.source}-${edge.target}`;

            return (
              <g key={edge.id} className="transition-opacity duration-300 hover:opacity-100 opacity-70">
                <defs>
                  <marker
                    id={markerId}
                    viewBox="0 0 10 10"
                    refX="9"
                    refY="5"
                    markerUnits="strokeWidth"
                    markerWidth="4"
                    markerHeight="3"
                    orient="auto"
                  >
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#9CA3AF" />
                  </marker>
                </defs>
                <path
                  d={d}
                  fill="none"
                  stroke="#9CA3AF"
                  strokeWidth="2"
                  markerEnd={`url(#${markerId})`}
                  className="transition-all duration-300"
                />
              </g>
            );
          })}

          {/* Nodes */}
          {nodes.map((node) => {
            assertExists(node.x, `Node X coordinate must exist for node ${node.id}`);
            assertExists(node.y, `Node Y coordinate must exist for node ${node.id}`);

            const x = node.x - node.width / 2;
            const y = node.y - node.height / 2;
            const nodeColor = TYPE_COLOR_MAP[node.type] || TYPE_COLOR_MAP.module;
            const statusClass = STATUS_BORDER_MAP[node.status] || STATUS_BORDER_MAP.resolved;

            return (
              <motion.g
                key={node.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                transform={`translate(${x}, ${y})`}
                className="cursor-pointer"
              >
                <rect
                  width={node.width}
                  height={node.height}
                  rx="6"
                  ry="6"
                  fill="#FFFFFF"
                  stroke={nodeColor}
                  strokeWidth="2"
                  className={`${statusClass} transition-all duration-300 hover:shadow-lg`}
                />
                <text
                  x={node.width / 2}
                  y={node.height / 2}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize="12"
                  fontWeight="500"
                  fill="#1F2937"
                  className="pointer-events-none select-none"
                >
                  {node.label}
                </text>
              </motion.g>
            );
          })}
        </svg>
      </div>
    </motion.div>
  );
};

export default DependencyGraph;