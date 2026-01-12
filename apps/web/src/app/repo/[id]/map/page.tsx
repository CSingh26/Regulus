import ArchitectureMap from '@/components/ArchitectureMap';
import PageHeader from '@/components/PageHeader';

export default function MapPage({ params }: { params: { id: string } }) {
  return (
    <div className="flex flex-col gap-8">
      <PageHeader
        title="Architecture map"
        subtitle="Graph view of modules, ownership, and dependency flows."
      />
      <ArchitectureMap repoId={params.id} />
    </div>
  );
}
