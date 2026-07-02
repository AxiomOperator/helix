export default function NodesPage() {
  return <Placeholder title="Nodes" description="Node inventory will be implemented in a later phase." />;
}

function Placeholder({ title, description }: { title: string; description: string }) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
      <h1 className="text-3xl font-semibold">{title}</h1>
      <p className="mt-4 text-slate-300">{description}</p>
    </section>
  );
}
