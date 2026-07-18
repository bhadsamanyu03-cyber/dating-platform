import { DiscoveryProfile } from "./types";
const baseUrl =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8080/api/v1";
export async function discovery(token: string, cursor?: string) {
  const response = await fetch(
    `${baseUrl}/discovery${cursor ? `?cursor=${encodeURIComponent(cursor)}` : ""}`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  if (!response.ok) throw new Error((await response.json()).detail);
  return response.json() as Promise<{
    candidates: DiscoveryProfile[];
    next_cursor: string | null;
  }>;
}
export async function act(
  token: string,
  type: "like" | "pass",
  target_user_id: string,
) {
  const response = await fetch(`${baseUrl}/discovery/${type}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ target_user_id }),
  });
  if (!response.ok) throw new Error((await response.json()).detail);
}
