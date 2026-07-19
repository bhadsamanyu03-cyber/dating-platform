const baseUrl =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8080/api/v1";
export type Post = {
  id: string;
  author_user_id: string;
  caption: string | null;
  visibility: string;
  media_asset_ids: string[];
  created_at: string;
};
export async function feed() {
  const response = await fetch(`${baseUrl}/feed`);
  if (!response.ok) throw new Error((await response.json()).detail);
  return response.json() as Promise<{
    posts: Post[];
    next_cursor: string | null;
  }>;
}
