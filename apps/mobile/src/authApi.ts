import { apiJson, authHeaders } from "./apiClient";

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

export type UserResponse = {
  id: string;
  email: string;
  is_email_verified: boolean;
  created_at: string;
};

export function login(email: string, password: string) {
  return apiJson<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function register(email: string, password: string) {
  return apiJson<UserResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function verifyEmail(token: string) {
  return apiJson<void>("/auth/verify-email", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

export function refreshSession(refreshToken: string) {
  return apiJson<TokenResponse>("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

export function logout(refreshToken: string) {
  return apiJson<void>("/auth/logout", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

export function me(token: string) {
  return apiJson<UserResponse>("/auth/me", {
    headers: authHeaders(token),
  });
}

export function changePassword(
  token: string,
  currentPassword: string,
  newPassword: string,
) {
  return apiJson<void>("/auth/change-password", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });
}

export function deleteAccount(token: string, password: string) {
  return apiJson<void>("/auth/account", {
    method: "DELETE",
    headers: authHeaders(token),
    body: JSON.stringify({ password }),
  });
}
