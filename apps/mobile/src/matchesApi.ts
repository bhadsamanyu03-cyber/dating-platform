import { MatchResponse } from "./types";

const baseUrl =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8080/api/v1";

export async function matches(token: string, cursor?: string) {
  const response = await fetch(
    `${baseUrl}/matches${cursor ? `?cursor=${encodeURIComponent(cursor)}` : ""}`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  if (!response.ok) throw new Error((await response.json()).detail);
  return response.json() as Promise<{
    matches: MatchResponse[];
    next_cursor: string | null;
  }>;
}

export const getMatches = matches;

export async function removeMatch(token: string, matchId: string) {
  const response = await fetch(`${baseUrl}/matches/${matchId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error((await response.json()).detail);
}
