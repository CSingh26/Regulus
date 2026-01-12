import PageHeader from '@/components/PageHeader';

export default function SecurityPage() {
  return (
    <div className="flex flex-col gap-8">
      <PageHeader title="Security findings" subtitle="Semgrep, pip-audit, and npm audit results." />
      <div className="rounded-3xl border border-border bg-panel p-10 shadow-soft">
        <p className="text-sm text-muted">Security findings placeholder.</p>
      </div>
    </div>
  );
}
