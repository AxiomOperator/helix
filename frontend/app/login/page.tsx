"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../auth-provider";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const { setUser } = useAuth();
  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const user = await login(usernameOrEmail, password);
      setUser(user);
      router.push("/dashboard");
    } catch {
      setError("Invalid username or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <section className="w-full max-w-md rounded-2xl border border-slate-700 bg-slate-900/70 p-10">
        <h1 className="text-3xl font-semibold">Login</h1>
        <p className="mt-4 text-slate-300">Sign in with your local Linux Command Center account.</p>
        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <label className="block">
            <span className="text-sm text-slate-300">Username or email</span>
            <input
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none ring-cyan-400 focus:ring-2"
              value={usernameOrEmail}
              onChange={(event) => setUsernameOrEmail(event.target.value)}
              autoComplete="username"
              required
            />
          </label>
          <label className="block">
            <span className="text-sm text-slate-300">Password</span>
            <input
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none ring-cyan-400 focus:ring-2"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
          {error ? <p className="rounded-lg bg-red-950 px-4 py-3 text-sm text-red-200">{error}</p> : null}
          <button
            className="w-full rounded-lg bg-cyan-400 px-4 py-3 font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}
