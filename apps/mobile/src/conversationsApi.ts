const baseUrl =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8080/api/v1";
export type Conversation = { id: string; match_id: string; created_at: string };
export type Message = {
  id: string;
  sender_user_id: string;
  message_type: "TEXT" | "IMAGE" | "VIDEO";
  text_content: string | null;
  media_asset_id: string | null;
  created_at: string;
};
export async function conversations(token: string) {
  const response = await fetch(`${baseUrl}/conversations`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error((await response.json()).detail);
  return response.json() as Promise<{ conversations: Conversation[] }>;
}
export async function messages(token: string, id: string) {
  const response = await fetch(`${baseUrl}/conversations/${id}/messages`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error((await response.json()).detail);
  return response.json() as Promise<{ messages: Message[] }>;
}
export async function sendText(
  token: string,
  id: string,
  text_content: string,
) {
  const response = await fetch(`${baseUrl}/conversations/${id}/messages`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message_type: "TEXT", text_content }),
  });
  if (!response.ok) throw new Error((await response.json()).detail);
  return response.json() as Promise<Message>;
}
