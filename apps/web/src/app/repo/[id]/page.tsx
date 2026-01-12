import PageHeader from '@/components/PageHeader';

export default function RepoOverviewPage() {
  return (
    <div className="flex flex-col gap-8">
      <PageHeader
        title="Overview"
        subtitle="Kick off indexing jobs and get a quick pulse on this repo."
      />
      <div className="grid gap-6 md:grid-cols-3">
        {['Index repo', 'Build graph', 'Generate embeddings'].map((label) => (
          <div key={label} className="rounded-3xl border border-border bg-panel p-6 shadow-soft">
            <p className="text-xs uppercase tracking-[0.2em] text-muted">Action</p>
            <h3 className="mt-3 text-lg font-semibold text-text">{label}</h3>
            <p className="mt-2 text-sm text-muted">
              Trigger background jobs from the API to refresh this dataset.
            </p>
            <button className="mt-4 rounded-2xl border border-border px-3 py-2 text-xs text-muted">
              Coming soon
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
