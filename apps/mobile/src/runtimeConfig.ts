import Constants from "expo-constants";

const DEFAULT_API_URL = "http://localhost:8080/api/v1";

function normalizeHost(host: string) {
  const trimmed = host.trim();
  if (!trimmed) return null;
  return trimmed.replace(/^\[|\]$/g, "");
}

function deriveApiBaseUrl() {
  const envUrl = process.env.EXPO_PUBLIC_API_URL?.trim();
  if (envUrl) return envUrl;

  const hostUri =
    Constants.expoConfig?.hostUri ??
    Constants.linkingUri ??
    Constants.manifest2?.extra?.expoClient?.hostUri ??
    "";
  const normalized = normalizeHost(hostUri);
  if (!normalized) return DEFAULT_API_URL;

  const hostOnly = normalized
    .replace(/^exp(s)?:\/\//, "")
    .replace(/^http(s)?:\/\//, "")
    .split("/")[0]
    .split(":")[0];
  if (!hostOnly) return DEFAULT_API_URL;
  return `http://${hostOnly}:8080/api/v1`;
}

export const apiBaseUrl = deriveApiBaseUrl();
