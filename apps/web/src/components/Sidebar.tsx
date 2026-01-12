'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { label: 'Architecture Map', href: 'map' },
  { label: 'Explain', href: 'explain' },
  { label: 'Blast Radius', href: 'blast' },
  { label: 'Hotspots', href: 'hotspots' },
  { label: 'Security', href: 'security' },
];

export default function Sidebar({ repoId }: { repoId: string }) {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-64 flex-col gap-6 border-r border-border bg-panel/80 px-6 py-8">
      <Link href="/" className="text-sm font-semibold uppercase tracking-[0.35em] text-muted">
        Regulus
      </Link>
      <div className="flex flex-col gap-2">
        <p className="text-xs uppercase tracking-[0.2em] text-muted">Repo {repoId}</p>
        <div className="flex flex-col gap-2">
          {navItems.map((item) => {
            const href = `/repo/${repoId}/${item.href}`;
            const active = pathname === href;
            return (
              <Link
                key={item.href}
                href={href}
                className={`rounded-xl px-3 py-2 text-sm transition ${
                  active
                    ? 'bg-accent text-white shadow-glow'
                    : 'text-muted hover:bg-white/70 hover:text-text'
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
