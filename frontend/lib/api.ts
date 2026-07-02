const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const unsafeMethods = new Set(["POST", "PUT", "PATCH", "DELETE"]);
let cachedCsrfToken: string | null = null;

export type HealthResponse = {
  status: string;
  service: string;
};

export type User = {
  id: string;
  username: string;
  email: string;
  display_name: string | null;
  role: "viewer" | "operator" | "admin" | "break_glass_admin";
};

export async function getHealth(): Promise<HealthResponse> {
  const response = await apiFetch("/health");

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }

  return response.json() as Promise<HealthResponse>;
}

export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const method = (init.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");

  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (unsafeMethods.has(method) && path !== "/auth/login") {
    const token = cachedCsrfToken ?? (await getCsrfToken());
    headers.set("X-CSRF-Token", token);
  }

  return fetch(`${API_BASE_URL}${path}`, {
    ...init,
    method,
    headers,
    credentials: "include",
  });
}

export async function getCsrfToken(): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/auth/csrf`, {
    method: "GET",
    credentials: "include",
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    cachedCsrfToken = null;
    throw new Error("Unable to fetch CSRF token");
  }

  const data = (await response.json()) as { csrf_token: string };
  cachedCsrfToken = data.csrf_token;
  return data.csrf_token;
}

export async function login(usernameOrEmail: string, password: string): Promise<User> {
  cachedCsrfToken = null;
  const response = await apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username_or_email: usernameOrEmail, password }),
  });

  if (!response.ok) {
    throw new Error("Invalid username or password");
  }

  const data = (await response.json()) as { user: User };
  return data.user;
}

export async function getMe(): Promise<User> {
  const response = await apiFetch("/me");
  if (!response.ok) {
    throw new Error("Not authenticated");
  }
  return response.json() as Promise<User>;
}

export async function logout(): Promise<void> {
  const response = await apiFetch("/auth/logout", { method: "POST" });
  cachedCsrfToken = null;
  if (!response.ok) {
    throw new Error("Logout failed");
  }
}
