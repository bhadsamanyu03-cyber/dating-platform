import * as FileSystem from "expo-file-system";
import { apiBaseUrl as baseUrl } from "./runtimeConfig";

export type MediaAssetResponse = {
  id: string;
  original_filename: string;
  mime_type: string;
  media_type: string;
  file_size_bytes: number;
  checksum_sha256: string;
  upload_status: string;
  processing_state: string;
  width: number | null;
  height: number | null;
  duration_ms: number | null;
  aspect_ratio: string | null;
  orientation: number | null;
  codec: string | null;
  created_at: string;
};

type PresignedUploadResponse = {
  url: string;
  method: "PUT";
  storage_key: string;
  expires_in: number;
};

type PresignedFinalizePayload = {
  storage_key: string;
  filename: string;
  mime_type: string;
};

const MIME_BY_EXTENSION: Record<string, string> = {
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  png: "image/png",
  webp: "image/webp",
  heic: "image/heic",
  heif: "image/heic",
  mp4: "video/mp4",
  mov: "video/quicktime",
  m4v: "video/mp4",
};

function assertOk(response: Response) {
  if (!response.ok) {
    throw new Error("Request failed");
  }
}

export function mediaFilename(uri: string, fallback = "upload"): string {
  const value = uri.split("?")[0].split("#")[0].split("/").pop() ?? fallback;
  return value || fallback;
}

export function mediaMimeType(uri: string, fallback = "image/jpeg"): string {
  const extension = mediaFilename(uri).split(".").pop()?.toLowerCase();
  return (extension && MIME_BY_EXTENSION[extension]) || fallback;
}

export function mediaDownloadUrl(assetId: string) {
  return `${baseUrl}/media/${assetId}`;
}

async function checkedJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "Request failed");
  }
  return response.json() as Promise<T>;
}

async function requestPresignedUpload(
  token: string,
  filename: string,
  mimeType: string,
): Promise<PresignedUploadResponse> {
  return checkedJson<PresignedUploadResponse>(
    await fetch(`${baseUrl}/media/presigned-upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ filename, mime_type: mimeType }),
    }),
  );
}

async function finalizeUpload(
  token: string,
  payload: PresignedFinalizePayload,
): Promise<MediaAssetResponse> {
  return checkedJson<MediaAssetResponse>(
    await fetch(`${baseUrl}/media/finalize-upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }),
  );
}

async function uploadToPresignedUrl(
  url: string,
  uri: string,
  mimeType: string,
) {
  const response = await FileSystem.uploadAsync(url, uri, {
    httpMethod: "PUT",
    uploadType: FileSystem.FileSystemUploadType.BINARY_CONTENT,
    headers: { "Content-Type": mimeType },
  });
  if (response.status < 200 || response.status >= 300) {
    throw new Error("Upload failed");
  }
}

export async function uploadMediaAsset(token: string, uri: string) {
  const filename = mediaFilename(uri);
  const mimeType = mediaMimeType(uri);
  const presigned = await requestPresignedUpload(token, filename, mimeType);
  await uploadToPresignedUrl(presigned.url, uri, mimeType);
  return finalizeUpload(token, {
    storage_key: presigned.storage_key,
    filename,
    mime_type: mimeType,
  });
}

export async function fetchMediaBytes(
  token: string,
  assetId: string,
): Promise<string> {
  const response = await fetch(mediaDownloadUrl(assetId), {
    headers: { Authorization: `Bearer ${token}` },
  });
  assertOk(response);
  return response.url;
}
