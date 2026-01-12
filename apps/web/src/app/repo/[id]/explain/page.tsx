import PageHeader from '@/components/PageHeader';

export default function ExplainPage() {
  return (
    <div className="flex flex-col gap-8">
      <PageHeader
        title="Explain"
        subtitle="Ask questions about modules, symbols, and architectural intent."
      />
      <div className="rounded-3xl border border-border bg-panel p-10 shadow-soft">
        <p className="text-sm text-muted">
          RAG chat and citations will appear here once the embeddings job completes.
        </p>
      </div>
    </div>
  );
}
