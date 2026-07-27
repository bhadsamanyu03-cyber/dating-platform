export type Interest = { id: string; name: string };
export type Profile = {
  username: string;
  display_name: string;
  bio: string;
  gender: string;
  pronouns: string | null;
  date_of_birth: string;
  height_cm: number | null;
  interests: Interest[];
  profile_photo_count: number;
  profile_video_count: number;
  profile_completion_percentage: number;
  created_at: string;
  updated_at: string;
};
export type ProfilePhoto = {
  id: string;
  media_asset_id: string;
  ordering: number;
  is_primary: boolean;
  created_at: string;
};
const baseUrl =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8080/api/v1";
async function request<T>(
  path: string,
  token: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
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
export const getMyProfile = (token: string) =>
  request<Profile>("/profile/me", token);
export const getProfile = (username: string, token: string) =>
  request<Profile>(`/profile/${encodeURIComponent(username)}`, token);
export const getInterests = (token: string) =>
  request<Interest[]>("/interests", token);
export const checkUsername = (username: string, token: string) =>
  request<{ available: boolean }>(
    `/profile/check-username?username=${encodeURIComponent(username)}`,
    token,
  );
export const saveProfile = (
  profile: Omit<
    Profile,
    | "interests"
    | "profile_photo_count"
    | "profile_video_count"
    | "profile_completion_percentage"
    | "created_at"
    | "updated_at"
  > & { interest_ids: string[] },
  token: string,
) =>
  request<Profile>("/profile/me", token, {
    method: "PUT",
    body: JSON.stringify(profile),
  });

export const getMyPhotos = (token: string) =>
  request<ProfilePhoto[]>("/profile/me/photos", token);

export const addPhoto = (
  token: string,
  payload: { media_asset_id: string; ordering: number },
) =>
  request<ProfilePhoto>("/profile/me/photos", token, {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const deletePhoto = (token: string, photoId: string) =>
  request<void>(`/profile/me/photos/${photoId}`, token, {
    method: "DELETE",
  });
