import Sidebar from '@/components/Sidebar';
import Topbar from '@/components/Topbar';

export default function RepoLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { id: string };
}) {
  return (
    <div className="min-h-screen bg-canvas">
      <div className="flex min-h-screen">
        <Sidebar repoId={params.id} />
        <div className="flex flex-1 flex-col">
          <Topbar title={`Repo ${params.id}`} />
          <div className="flex-1 px-10 py-8">{children}</div>
        </div>
      </div>
    </div>
  );
}
