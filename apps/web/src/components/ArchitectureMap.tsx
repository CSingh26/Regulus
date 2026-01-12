'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import ReactFlow, { Background, Controls, MiniMap, type Edge, type Node } from 'reactflow';
import 'reactflow/dist/style.css';

import { getGraph, type GraphResponse } from '@/lib/apiClient';
import NodeDrawer, { type NodeDetails } from '@/components/NodeDrawer';

type LayoutNode = { id: string };

type LayoutEdge = { source: string; target: string };

export default function ArchitectureMap({ repoId }: { repoId: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const workerRef = useRef<Worker | null>(null);
  const layoutKeyRef = useRef<string | null>(null);
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selected, setSelected] = useState<NodeDetails | null>(null);
  const [dimensions, setDimensions] = useState({ width: 1200, height: 700 });

  useEffect(() => {
    workerRef.current = new Worker(new URL('../workers/graphLayout.ts', import.meta.url));
    return () => workerRef.current?.terminate();
  }, []);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        setDimensions({ width, height });
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    let active = true;
    getGraph(Number(repoId))
      .then((response) => {
        if (active) {
          setGraph(response);
        }
      })
      .catch(() => {
        if (active) {
          setGraph({ nodes: [], edges: [] });
        }
      });
    return () => {
      active = false;
    };
  }, [repoId]);

  useEffect(() => {
    if (!graph) {
      return;
    }
    const mappedNodes: Node[] = graph.nodes.map((node) => ({
      id: String(node.id),
      data: node,
      position: { x: 0, y: 0 },
      type: 'default',
    }));
    const mappedEdges: Edge[] = graph.edges.map((edge) => ({
      id: String(edge.id),
      source: String(edge.from_node_id),
      target: String(edge.to_node_id),
      type: 'smoothstep',
      animated: true,
    }));
    setNodes(mappedNodes);
    setEdges(mappedEdges);
  }, [graph]);

  useEffect(() => {
    if (!workerRef.current || nodes.length === 0) {
      return;
    }
    const layoutKey = `${nodes.length}:${edges.length}:${dimensions.width}:${dimensions.height}`;
    if (layoutKeyRef.current === layoutKey) {
      return;
    }
    layoutKeyRef.current = layoutKey;

    const layoutNodes: LayoutNode[] = nodes.map((node) => ({ id: node.id }));
    const layoutEdges: LayoutEdge[] = edges.map((edge) => ({
      source: edge.source,
      target: edge.target,
    }));

    workerRef.current.postMessage({
      nodes: layoutNodes,
      edges: layoutEdges,
      width: dimensions.width,
      height: dimensions.height,
    });

    workerRef.current.onmessage = (event: MessageEvent<{ nodes: LayoutNode[] }>) => {
      const positions = new Map(
        event.data.nodes.map((node: LayoutNode & { x?: number; y?: number }) => [
          node.id,
          {
            x: node.x ?? 0,
            y: node.y ?? 0,
          },
        ]),
      );
      setNodes((prev) =>
        prev.map((node) => ({
          ...node,
          position: positions.get(node.id) ?? node.position,
        })),
      );
    };
  }, [nodes, edges, dimensions]);

  const minimapStyle = useMemo(
    () => ({
      height: 120,
      width: 180,
    }),
    [],
  );

  return (
    <div className="relative h-[70vh] w-full overflow-hidden rounded-3xl border border-border bg-panel shadow-soft">
      <div ref={containerRef} className="h-full w-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodeClick={(_, node) => setSelected(node.data as NodeDetails)}
          fitView
        >
          <Background gap={18} color="rgba(15, 23, 42, 0.08)" />
          <MiniMap style={minimapStyle} pannable zoomable />
          <Controls />
        </ReactFlow>
      </div>
      <NodeDrawer node={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
