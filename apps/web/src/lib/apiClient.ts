const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
const API_V1 = `${API_BASE}/v1`;

type RequestOptions = RequestInit & {
  json?: unknown;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_V1}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
    body: options.json ? JSON.stringify(options.json) : options.body,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export type RepoResponse = {
  id: number;
  name: string;
  path: string;
};

export async function registerRepo(payload: { name: string; path: string }) {
  return request<RepoResponse>('/repos/register', {
    method: 'POST',
    json: payload,
  });
}

export async function getRepoStatus(repoId: number) {
  return request<RepoResponse>(`/repos/${repoId}/status`);
}
