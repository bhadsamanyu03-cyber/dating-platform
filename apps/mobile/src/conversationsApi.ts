const baseUrl =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8080/api/v1";

export type Conversation = { id: string; match_id: string; created_at: string };
export type Message = {
  id: string;
  sender_user_id: string;
  message_type: "TEXT" | "IMAGE" | "SYSTEM";
  text_content: string | null;
  media_asset_ids: string[];
  created_at: string;
  delivered_at: string | null;
  read_at: string | null;
  deleted_at: string | null;
  client_message_id: string | null;
  pending?: boolean;
  failed?: boolean;
};

async function checked(response: Response) {
  if (!response.ok)
    throw new Error(
      (await response.json().catch(() => ({}))).detail ?? "Request failed",
    );
  return response;
}

export async function conversations(token: string) {
  return (
    await checked(
      await fetch(`${baseUrl}/conversations`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
    )
  ).json() as Promise<{ conversations: Conversation[] }>;
}

export async function messages(token: string, id: string, cursor?: string) {
  const suffix = cursor ? `?cursor=${encodeURIComponent(cursor)}` : "";
  return (
    await checked(
      await fetch(`${baseUrl}/conversations/${id}/messages${suffix}`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
    )
  ).json() as Promise<{ messages: Message[]; next_cursor: string | null }>;
}

export async function sendMessage(
  token: string,
  id: string,
  payload: {
    text_content?: string;
    media_asset_ids?: string[];
    client_message_id: string;
  },
) {
  return (
    await checked(
      await fetch(`${baseUrl}/conversations/${id}/messages`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message_type: payload.media_asset_ids?.length ? "IMAGE" : "TEXT",
          ...payload,
        }),
      }),
    )
  ).json() as Promise<Message>;
}

export async function uploadImage(token: string, uri: string) {
  const { uploadMediaAsset } = await import("./mediaApi");
  return uploadMediaAsset(token, uri);
}

export async function uploadMedia(token: string, uri: string) {
  const { uploadMediaAsset } = await import("./mediaApi");
  return uploadMediaAsset(token, uri);
}

export function attachmentUrl(messageId: string, assetId: string) {
  return `${baseUrl}/messages/${messageId}/media/${assetId}`;
}
