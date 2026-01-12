import RepoSelector from '@/components/RepoSelector';

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-6 py-16">
      <section className="flex flex-col gap-6">
        <p className="text-xs uppercase tracking-[0.4em] text-muted">Regulus</p>
        <h1 className="text-5xl font-semibold text-text">
          Talk to your codebase with architecture intelligence.
        </h1>
        <p className="max-w-2xl text-lg text-muted">
          Index a repository, explore its dependency graph, and ask questions with RAG. Predict
          blast radius, surface hotspots, and ship safer changes.
        </p>
      </section>
      <RepoSelector />
    </main>
  );
}
