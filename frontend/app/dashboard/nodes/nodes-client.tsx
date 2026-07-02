"use client";

import { useEffect, useState } from "react";
import { createEnrollmentToken, getNodes, type EnrollmentToken, type Node } from "@/lib/api";
import { useAuth } from "../../auth-provider";

export default function NodesClient() {
  const { user } = useAuth();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [token, setToken] = useState<EnrollmentToken | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const canCreateToken = user?.role === "admin" || user?.role === "break_glass_admin";

  async function loadNodes() {
    try {
      setError(null);
      setNodes(await getNodes());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load nodes");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateToken() {
    setCreating(true);
    setError(null);
    try {
      setToken(await createEnrollmentToken());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create enrollment token");
    } finally {
      setCreating(false);
    }
  }

  useEffect(() => {
    void loadNodes();
  }, []);

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 className="text-3xl font-semibold">Nodes</h1>
            <p className="mt-3 max-w-2xl text-slate-300">
              Enroll Linux hosts with a one-time token, then track their agent connection status here.
            </p>
          </div>
          {canCreateToken ? (
            <button
              className="rounded-lg bg-cyan-400 px-4 py-2 text-sm font-medium text-slate-950 hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={creating}
              onClick={handleCreateToken}
            >
              {creating ? "Creating..." : "Create enrollment token"}
            </button>
          ) : null}
        </div>

        {token ? (
          <div className="mt-6 rounded-xl border border-cyan-500/40 bg-cyan-950/30 p-4">
            <p className="text-sm font-medium text-cyan-200">Enrollment token shown once</p>
            <code className="mt-3 block break-all rounded-lg bg-slate-950 p-3 text-sm text-cyan-100">{token.token}</code>
            <p className="mt-3 text-sm text-slate-300">
              Agent command: <code>command-agent enroll --server-url http://localhost:8000 --token {token.token}</code>
            </p>
          </div>
        ) : null}

        {error ? <p className="mt-4 rounded-lg bg-red-950/60 p-3 text-sm text-red-200">{error}</p> : null}
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Fleet inventory</h2>
          <button className="text-sm text-cyan-300 hover:text-cyan-200" onClick={() => void loadNodes()}>
            Refresh
          </button>
        </div>

        {loading ? <p className="mt-6 text-slate-300">Loading nodes...</p> : null}
        {!loading && nodes.length === 0 ? (
          <div className="mt-6 rounded-xl border border-dashed border-slate-700 p-8 text-center text-slate-300">
            No nodes enrolled yet. Create an enrollment token to add the first host.
          </div>
        ) : null}
        {nodes.length > 0 ? (
          <div className="mt-6 overflow-hidden rounded-xl border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950 text-slate-400">
                <tr>
                  <th className="px-4 py-3">Host</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">OS</th>
                  <th className="px-4 py-3">Arch</th>
                  <th className="px-4 py-3">Last seen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {nodes.map((node) => (
                  <tr key={node.id}>
                    <td className="px-4 py-4">
                      <div className="font-medium text-slate-100">{node.hostname}</div>
                      <div className="text-xs text-slate-500">{node.id}</div>
                    </td>
                    <td className="px-4 py-4">
                      <span className={`rounded-full px-3 py-1 text-xs ${node.online ? "bg-emerald-400 text-slate-950" : "bg-slate-800 text-slate-300"}`}>
                        {node.online ? "online" : "offline"}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-slate-300">{node.os_name || "unknown"}</td>
                    <td className="px-4 py-4 text-slate-300">{node.architecture || "unknown"}</td>
                    <td className="px-4 py-4 text-slate-300">{node.last_seen_at ? new Date(node.last_seen_at).toLocaleString() : "never"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </div>
  );
}
