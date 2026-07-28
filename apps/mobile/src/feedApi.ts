import { apiJson, authHeaders } from "./apiClient";

export type Post = {
  id: string;
  author_user_id: string;
  caption: string | null;
  visibility: string;
  media_asset_ids: string[];
  like_count: number;
  comment_count: number;
  created_at: string;
};
export type CreatePostPayload = {
  caption?: string;
  visibility?: "PUBLIC" | "PRIVATE";
  media_asset_ids?: string[];
};
export type Comment = {
  id: string;
  author_user_id: string;
  body: string;
  created_at: string;
};
export async function feed(token: string, cursor?: string) {
  return apiJson<{
    posts: Post[];
    next_cursor: string | null;
  }>(`/feed${cursor ? `?cursor=${encodeURIComponent(cursor)}` : ""}`, {
    headers: authHeaders(token),
  });
}

export async function createPost(token: string, payload: CreatePostPayload) {
  return apiJson<Post>("/feed/posts", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({
      visibility: "PUBLIC",
      ...payload,
    }),
  });
}

export function likePost(token: string, postId: string) {
  return apiJson<void>(`/feed/${postId}/likes`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export function unlikePost(token: string, postId: string) {
  return apiJson<void>(`/feed/${postId}/likes`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
}

export function comments(token: string, postId: string, cursor?: string) {
  return apiJson<{ comments: Comment[]; next_cursor: string | null }>(
    `/feed/${postId}/comments${cursor ? `?cursor=${encodeURIComponent(cursor)}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export function createComment(token: string, postId: string, body: string) {
  return apiJson<Comment>(`/feed/${postId}/comments`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ body }),
  });
}
