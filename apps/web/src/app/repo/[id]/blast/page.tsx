import PageHeader from '@/components/PageHeader';

export default function BlastPage() {
  return (
    <div className="flex flex-col gap-8">
      <PageHeader title="Blast radius" subtitle="Predict what breaks when you edit a file." />
      <div className="rounded-3xl border border-border bg-panel p-10 shadow-soft">
        <p className="text-sm text-muted">Upload or select changed files to simulate impact.</p>
      </div>
    </div>
  );
}
