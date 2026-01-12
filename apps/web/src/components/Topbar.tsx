export default function Topbar({ title }: { title: string }) {
  return (
    <div className="flex items-center justify-between border-b border-border bg-panel/70 px-8 py-4 backdrop-blur">
      <div>
        <h2 className="text-lg font-semibold text-text">{title}</h2>
        <p className="text-xs uppercase tracking-[0.25em] text-muted">Talk to your codebase</p>
      </div>
      <div className="text-xs text-muted">Local mode</div>
    </div>
  );
}
