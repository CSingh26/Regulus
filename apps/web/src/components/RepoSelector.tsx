'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

import { registerRepo } from '@/lib/apiClient';

type RepoEntry = {
  id: number;
  name: string;
  path: string;
};

const STORAGE_KEY = 'regulus:recent-repos';

function loadRecent(): RepoEntry[] {
  if (typeof window === 'undefined') {
    return [];
  }
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return [];
  }
  try {
    return JSON.parse(raw) as RepoEntry[];
  } catch {
    return [];
  }
}

function saveRecent(repos: RepoEntry[]) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(repos));
}

export default function RepoSelector() {
  const [name, setName] = useState('Regulus');
  const [path, setPath] = useState('');
  const [recent, setRecent] = useState<RepoEntry[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    setRecent(loadRecent());
  }, []);

  async function handleRegister(event: React.FormEvent) {
    event.preventDefault();
    setStatus('Registering...');
    try {
      const repo = await registerRepo({ name, path });
      const updated = [repo, ...recent.filter((item) => item.id !== repo.id)].slice(0, 6);
      setRecent(updated);
      saveRecent(updated);
      setStatus(`Registered ${repo.name}`);
      setPath('');
    } catch (error) {
      setStatus(`Failed to register: ${(error as Error).message}`);
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
      <div className="rounded-3xl border border-border bg-panel p-8 shadow-soft">
        <h2 className="text-2xl font-semibold text-text">Register a repo</h2>
        <p className="mt-2 text-sm text-muted">
          Point Regulus at a local path to start indexing and mapping the architecture.
        </p>
        <form className="mt-6 flex flex-col gap-4" onSubmit={handleRegister}>
          <label className="text-xs uppercase tracking-[0.2em] text-muted">Name</label>
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="rounded-2xl border border-border bg-white px-4 py-3 text-sm"
            placeholder="My Service"
          />
          <label className="text-xs uppercase tracking-[0.2em] text-muted">Path</label>
          <input
            value={path}
            onChange={(event) => setPath(event.target.value)}
            className="rounded-2xl border border-border bg-white px-4 py-3 text-sm"
            placeholder="/Users/you/project"
            required
          />
          <button
            type="submit"
            className="rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-white shadow-glow"
          >
            Register & Index
          </button>
          {status ? <p className="text-xs text-muted">{status}</p> : null}
        </form>
      </div>
      <div className="rounded-3xl border border-border bg-panel p-8 shadow-soft">
        <h2 className="text-2xl font-semibold text-text">Recent repos</h2>
        <p className="mt-2 text-sm text-muted">Jump back into a previously indexed codebase.</p>
        <div className="mt-6 flex flex-col gap-3">
          {recent.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-border bg-white px-4 py-6 text-sm text-muted">
              No repos yet.
            </div>
          ) : (
            recent.map((repo) => (
              <Link
                key={repo.id}
                href={`/repo/${repo.id}/map`}
                className="flex items-center justify-between rounded-2xl border border-border bg-white px-4 py-4 text-sm transition hover:border-accent"
              >
                <div>
                  <p className="font-semibold text-text">{repo.name}</p>
                  <p className="text-xs text-muted">{repo.path}</p>
                </div>
                <span className="text-xs text-muted">Open</span>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
