from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


@dataclass(frozen=True)
class GraphNode:
    name: str
    handler: Callable


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    condition: Optional[Callable] = None


def build_graph(
    nodes: List[GraphNode],
    edges: List[GraphEdge],
) -> Dict[str, object]:
    return {
        "nodes": {node.name: node.handler for node in nodes},
        "edges": [
            {
                "from": edge.source,
                "to": edge.target,
                "condition": edge.condition,
            }
            for edge in edges
        ],
    }
