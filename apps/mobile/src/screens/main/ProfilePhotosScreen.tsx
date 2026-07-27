import { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Button,
  FlatList,
  Image,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import {
  addPhoto,
  deletePhoto,
  getMyPhotos,
  ProfilePhoto,
} from "../../profileApi";
import { mediaDownloadUrl, uploadMediaAsset } from "../../mediaApi";

type Props = {
  accessToken: string;
};

export function ProfilePhotosScreen({ accessToken }: Props) {
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string>();
  const [photos, setPhotos] = useState<ProfilePhoto[]>([]);

  const orderedPhotos = useMemo(
    () => [...photos].sort((left, right) => left.ordering - right.ordering),
    [photos],
  );

  const load = async () => {
    try {
      setPhotos(await getMyPhotos(accessToken));
      setError(undefined);
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Unable to load photos",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void load();
  }, [accessToken]);

  const pickPhoto = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      setError("Photo library permission is required.");
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      allowsMultipleSelection: false,
      selectionLimit: 1,
      quality: 0.9,
    });
    if (result.canceled || !result.assets.length) return;

    const [asset] = result.assets;
    setUploading(true);
    setError(undefined);
    try {
      const uploaded = await uploadMediaAsset(accessToken, asset.uri);
      await addPhoto(accessToken, {
        media_asset_id: uploaded.id,
        ordering: photos.length,
      });
      await load();
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Unable to upload photo",
      );
    } finally {
      setUploading(false);
    }
  };

  const removePhoto = async (photoId: string) => {
    try {
      await deletePhoto(accessToken, photoId);
      await load();
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Unable to delete photo",
      );
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <Text>Loading photos…</Text>
      </View>
    );
  }

  return (
    <ScrollView
      contentContainerStyle={styles.container}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={() => setRefreshing(true)}
        />
      }
    >
      <Text style={styles.title}>Your Photos</Text>
      <Text style={styles.description}>
        Add up to 12 photos to your profile. The first photo is treated as your
        primary photo.
      </Text>

      {error && <Text style={styles.error}>{error}</Text>}

      <FlatList
        horizontal
        scrollEnabled={false}
        data={orderedPhotos}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.gallery}
        refreshing={refreshing}
        onRefresh={() => {
          setRefreshing(true);
          void load();
        }}
        renderItem={({ item, index }) => (
          <View style={styles.photoCard}>
            <Image
              source={{
                uri: mediaDownloadUrl(item.media_asset_id),
                headers: { Authorization: `Bearer ${accessToken}` },
              }}
              style={styles.photo}
            />
            <Text style={styles.badge}>
              {item.is_primary ? "Primary" : `Photo ${index + 1}`}
            </Text>
            <Button title="Delete" onPress={() => removePhoto(item.id)} />
          </View>
        )}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>No photos yet</Text>
            <Text style={styles.emptyText}>
              Upload a few clear photos so people can see your profile.
            </Text>
          </View>
        }
      />

      <Text style={styles.info}>
        {orderedPhotos.length} of 12 photos uploaded
      </Text>

      <Button
        title={uploading ? "Uploading…" : "Add Photo"}
        onPress={pickPhoto}
        disabled={uploading || orderedPhotos.length >= 12}
      />

      <View style={styles.tips}>
        <Text style={styles.tipsTitle}>Photo tips</Text>
        <Text style={styles.tipItem}>
          • Use a clear, well-lit face photo as your first photo.
        </Text>
        <Text style={styles.tipItem}>
          • JPEG, PNG, WebP, HEIC are supported.
        </Text>
        <Text style={styles.tipItem}>• Keep uploads under 25 MB.</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  center: { flex: 1, alignItems: "center", justifyContent: "center", gap: 8 },
  title: { fontSize: 24, fontWeight: "700", color: "#000" },
  description: { fontSize: 14, color: "#666", lineHeight: 20 },
  gallery: { gap: 12 },
  photoCard: {
    width: 180,
    gap: 8,
    borderRadius: 12,
    backgroundColor: "#f8f8f8",
    padding: 8,
  },
  photo: {
    width: "100%",
    height: 220,
    borderRadius: 10,
    backgroundColor: "#eaeaea",
  },
  badge: {
    fontSize: 12,
    color: "#444",
    fontWeight: "600",
  },
  emptyState: {
    paddingVertical: 24,
    gap: 8,
  },
  emptyTitle: { fontSize: 16, fontWeight: "700" },
  emptyText: { fontSize: 13, color: "#666" },
  info: { textAlign: "center", fontSize: 13, color: "#999" },
  error: { color: "#b00020" },
  tips: {
    backgroundColor: "#f9f9f9",
    borderRadius: 8,
    padding: 16,
    gap: 8,
  },
  tipsTitle: { fontSize: 14, fontWeight: "700", color: "#333" },
  tipItem: { fontSize: 13, color: "#666", lineHeight: 18 },
});
