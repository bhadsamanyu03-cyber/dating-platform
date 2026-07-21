import { useState } from "react";
import {
  ActivityIndicator,
  Button,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

type Props = {
  accessToken: string;
};

export function ProfilePhotosScreen({ accessToken }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [photos, setPhotos] = useState<{ id: string; name: string }[]>([]);

  // Placeholder for M2 media implementation
  const handleAddPhoto = () => {
    setError(
      "Photo uploads will be available in the next update (Milestone 2: Profile & Media Foundation)"
    );
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Your Photos</Text>
      <Text style={styles.description}>
        Add up to 12 photos to your profile. Your first photo will be your primary profile picture.
      </Text>

      <View style={styles.featureBox}>
        <Text style={styles.featureTitle}>✨ Coming Soon</Text>
        <Text style={styles.featureText}>
          Photo uploads and gallery management will be available soon. You'll be able to:
        </Text>
        <View style={styles.featureList}>
          <Text style={styles.featureBullet}>• Upload JPEG, PNG, WebP, and HEIC photos</Text>
          <Text style={styles.featureBullet}>• Up to 25 MB per photo</Text>
          <Text style={styles.featureBullet}>• Automatic image optimization</Text>
          <Text style={styles.featureBullet}>• Reorder your photos by dragging</Text>
          <Text style={styles.featureBullet}>• Delete unwanted photos</Text>
        </View>
      </View>

      <View style={styles.placeholderGrid}>
        {[...Array(3)].map((_, i) => (
          <View key={i} style={styles.photoPlaceholder}>
            <Text style={styles.placeholderText}>Photo {i + 1}</Text>
            <Text style={styles.placeholderSubtext}>Tap to add</Text>
          </View>
        ))}
      </View>

      <Text style={styles.info}>
        {photos.length} of 12 photos uploaded
      </Text>

      <View style={styles.actions}>
        <Button
          title="Add Photo"
          onPress={handleAddPhoto}
          color="#1976d2"
        />
      </View>

      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorTitle}>Coming Soon</Text>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      <View style={styles.tips}>
        <Text style={styles.tipsTitle}>📸 Photo Tips</Text>
        <Text style={styles.tipItem}>
          • Use clear, well-lit photos where your face is clearly visible
        </Text>
        <Text style={styles.tipItem}>
          • Avoid photos with other people or filters
        </Text>
        <Text style={styles.tipItem}>
          • Full-body photos help show your style and personality
        </Text>
        <Text style={styles.tipItem}>
          • Your first photo is most important—make it count!
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  title: { fontSize: 24, fontWeight: "700", color: "#000" },
  description: { fontSize: 14, color: "#666", lineHeight: 20 },
  featureBox: {
    backgroundColor: "#e3f2fd",
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: "#1976d2",
    padding: 16,
    gap: 8,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#1565c0",
  },
  featureText: {
    fontSize: 14,
    color: "#1565c0",
  },
  featureList: { gap: 6, marginTop: 4 },
  featureBullet: {
    fontSize: 13,
    color: "#1565c0",
    lineHeight: 18,
  },
  placeholderGrid: {
    flexDirection: "row",
    gap: 12,
    marginVertical: 16,
  },
  photoPlaceholder: {
    flex: 1,
    aspectRatio: 3 / 4,
    backgroundColor: "#f5f5f5",
    borderRadius: 8,
    borderWidth: 2,
    borderColor: "#e0e0e0",
    borderStyle: "dashed",
    justifyContent: "center",
    alignItems: "center",
  },
  placeholderText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#999",
  },
  placeholderSubtext: {
    fontSize: 12,
    color: "#ccc",
    marginTop: 4,
  },
  info: {
    textAlign: "center",
    fontSize: 13,
    color: "#999",
    marginVertical: 8,
  },
  actions: { gap: 10 },
  errorBox: {
    backgroundColor: "#fff3e0",
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: "#ff9800",
    padding: 16,
    gap: 8,
  },
  errorTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#e65100",
  },
  errorText: {
    fontSize: 13,
    color: "#e65100",
    lineHeight: 18,
  },
  tips: {
    backgroundColor: "#f9f9f9",
    borderRadius: 8,
    padding: 16,
    gap: 8,
    marginTop: 8,
  },
  tipsTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#333",
    marginBottom: 4,
  },
  tipItem: {
    fontSize: 13,
    color: "#666",
    lineHeight: 18,
  },
});
