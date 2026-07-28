export const apiBaseUrl =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8080/api/v1";

export async function apiJson<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "Request failed");
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export function authHeaders(token: string) {
  return { Authorization: `Bearer ${token}` };
}
