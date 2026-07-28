import { apiJson, authHeaders } from "./apiClient";

export type Notification = {
  id: string;
  recipient_id: string;
  actor_id: string | null;
  type: string;
  payload: Record<string, string>;
  is_read: boolean;
  created_at: string;
};

export function notifications(token: string, cursor?: string) {
  return apiJson<{ notifications: Notification[]; next_cursor: string | null }>(
    `/notifications${cursor ? `?cursor=${encodeURIComponent(cursor)}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export function unreadCount(token: string) {
  return apiJson<{ count: number }>("/notifications/unread-count", {
    headers: authHeaders(token),
  });
}

export function markNotificationRead(token: string, notificationId: string) {
  return apiJson<void>(`/notifications/${notificationId}/read`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export function markAllNotificationsRead(token: string) {
  return apiJson<void>("/notifications/read-all", {
    method: "POST",
    headers: authHeaders(token),
  });
}
