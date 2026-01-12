import { X } from 'lucide-react';

export type NodeDetails = {
  id: string;
  name: string;
  path: string;
  kind: string;
  loc: number;
  in_degree: number;
  out_degree: number;
};

export default function NodeDrawer({
  node,
  onClose,
}: {
  node: NodeDetails | null;
  onClose: () => void;
}) {
  if (!node) {
    return null;
  }

  return (
    <div className="absolute right-6 top-6 w-80 rounded-3xl border border-border bg-white p-6 shadow-soft">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-muted">Module</p>
          <h3 className="mt-2 text-lg font-semibold text-text">{node.name}</h3>
          <p className="text-xs text-muted">{node.path}</p>
        </div>
        <button
          onClick={onClose}
          className="rounded-full border border-border p-2 text-muted hover:text-text"
          aria-label="Close"
        >
          <X size={16} />
        </button>
      </div>
      <div className="mt-6 grid gap-3 text-xs text-muted">
        <div className="flex items-center justify-between">
          <span>Kind</span>
          <span className="font-semibold text-text">{node.kind}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Lines</span>
          <span className="font-semibold text-text">{node.loc}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Inbound</span>
          <span className="font-semibold text-text">{node.in_degree}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Outbound</span>
          <span className="font-semibold text-text">{node.out_degree}</span>
        </div>
      </div>
      <button className="mt-6 w-full rounded-2xl bg-accent px-4 py-3 text-xs font-semibold text-white">
        Explain this module
      </button>
    </div>
  );
}
