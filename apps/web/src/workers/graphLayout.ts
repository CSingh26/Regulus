import { forceCenter, forceCollide, forceLink, forceManyBody, forceSimulation } from 'd3-force';

type LayoutNode = {
  id: string;
  x?: number;
  y?: number;
};

type LayoutEdge = {
  source: string;
  target: string;
};

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

ctx.onmessage = (event: MessageEvent<LayoutRequest>) => {
  const { nodes, edges, width, height } = event.data;
  const simulation = forceSimulation(nodes)
    .force(
      'link',
      forceLink(edges)
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

  ctx.postMessage({ nodes } satisfies LayoutResponse);
};
