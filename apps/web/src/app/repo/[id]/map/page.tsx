import PageHeader from '@/components/PageHeader';

export default function MapPage() {
  return (
    <div className="flex flex-col gap-8">
      <PageHeader
        title="Architecture map"
        subtitle="Graph view of modules, ownership, and dependency flows."
      />
      <div className="rounded-3xl border border-border bg-panel p-10 text-center shadow-soft">
        <p className="text-sm text-muted">Graph canvas placeholder.</p>
      </div>
    </div>
  );
}
