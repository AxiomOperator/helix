"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "../auth-provider";
import type { User } from "@/lib/api";

const navItems = [
  { label: "Dashboard", href: "/dashboard", roles: ["viewer", "operator", "admin", "break_glass_admin"] },
  { label: "Nodes", href: "/dashboard/nodes", roles: ["viewer", "operator", "admin", "break_glass_admin"] },
  { label: "Jobs", href: "/dashboard/jobs", roles: ["viewer", "operator", "admin", "break_glass_admin"] },
  { label: "Approvals", href: "/dashboard/approvals", roles: ["admin", "break_glass_admin"] },
  { label: "Audit", href: "/dashboard/audit", roles: ["admin", "break_glass_admin"] },
  { label: "Settings", href: "/dashboard/settings", roles: ["admin", "break_glass_admin"] },
] satisfies Array<{ label: string; href: string; roles: User["role"][] }>;

export default function DashboardShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, loading, logout } = useAuth();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, router, user]);

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  if (loading || !user) {
    return <main className="flex min-h-screen items-center justify-center text-slate-300">Loading...</main>;
  }

  const visibleNav = navItems.filter((item) => item.roles.includes(user.role));

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-slate-800 bg-slate-900 px-5 py-6">
        <div className="text-lg font-semibold">Linux Command Center</div>
        <nav className="mt-8 space-y-2">
          {visibleNav.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                className={`block rounded-lg px-4 py-3 text-sm ${active ? "bg-cyan-400 text-slate-950" : "text-slate-300 hover:bg-slate-800"}`}
                href={item.href}
                key={item.href}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-slate-800 bg-slate-950/90 px-8 backdrop-blur">
          <div>
            <p className="text-sm text-slate-400">Signed in as</p>
            <p className="font-medium">{user.display_name || user.username}</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="rounded-full border border-slate-700 px-3 py-1 text-sm text-slate-300">{user.role}</span>
            <button className="rounded-lg bg-slate-800 px-4 py-2 text-sm hover:bg-slate-700" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </header>
        <main className="p-8">{children}</main>
      </div>
    </div>
  );
}
