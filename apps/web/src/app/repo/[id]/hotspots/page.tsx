import PageHeader from '@/components/PageHeader';

export default function HotspotsPage() {
  return (
    <div className="flex flex-col gap-8">
      <PageHeader
        title="Hotspots"
        subtitle="Churn, ownership, and centrality signals in one view."
      />
      <div className="rounded-3xl border border-border bg-panel p-10 shadow-soft">
        <p className="text-sm text-muted">Hotspot table placeholder.</p>
      </div>
    </div>
  );
}
