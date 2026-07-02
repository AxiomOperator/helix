"use client";

import { useAuth } from "../auth-provider";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
      <h1 className="text-3xl font-semibold">Dashboard</h1>
      <p className="mt-4 text-lg text-slate-300">Welcome, {user?.display_name || user?.username}</p>
      <p className="mt-2 text-slate-400">Role: {user?.role}</p>
      <p className="mt-8 text-slate-300">Fleet overview will be implemented in a later phase.</p>
    </section>
  );
}
