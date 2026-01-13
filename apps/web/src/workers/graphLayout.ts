/// <reference lib="webworker" />
import {
  forceCenter,
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  type SimulationLinkDatum,
  type SimulationNodeDatum,
} from 'd3-force';

type LayoutNode = SimulationNodeDatum & {
  id: string;
  x?: number;
  y?: number;
};

type LayoutEdge = SimulationLinkDatum<LayoutNode>;

type LayoutRequest = {
  nodes: LayoutNode[];
  edges: LayoutEdge[];
  width: number;
  height: number;
};

type LayoutResponse = {
  nodes: Array<LayoutNode & { x: number; y: number }>;
};

const ctx: DedicatedWorkerGlobalScope = self as unknown as DedicatedWorkerGlobalScope;

ctx.addEventListener('message', (event: MessageEvent<LayoutRequest>) => {
  const { nodes, edges, width, height } = event.data;
  const simulation = forceSimulation<LayoutNode>(nodes)
    .force(
      'link',
      forceLink<LayoutNode, LayoutEdge>(edges)
        .id((node) => node.id)
        .distance(120)
        .strength(0.12),
    )
    .force('charge', forceManyBody().strength(-240))
    .force('center', forceCenter(width / 2, height / 2))
    .force('collide', forceCollide().radius(36));

  for (let i = 0; i < 300; i += 1) {
    simulation.tick();
  }
  simulation.stop();

  const resolvedNodes: LayoutResponse['nodes'] = nodes.map((node) => ({
    ...node,
    x: node.x ?? 0,
    y: node.y ?? 0,
  }));

  ctx.postMessage({ nodes: resolvedNodes } satisfies LayoutResponse);
});
