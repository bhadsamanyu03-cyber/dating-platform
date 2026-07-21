import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { getProfile } from "../../profileApi";
import { DiscoveryProfile } from "../../types";

type Props = {
  accessToken: string;
  username: string;
  onClose?: () => void;
};

export function PublicProfileScreen({
  accessToken,
  username,
  onClose,
}: Props) {
  const [profile, setProfile] = useState<DiscoveryProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(undefined);
      try {
        const data = await getProfile(username, accessToken);
        // Map Profile type to DiscoveryProfile
        const discoveryProfile: DiscoveryProfile = {
          user_id: data.id ?? "", // Extract from response or generate
          username: data.username,
          display_name: data.display_name,
          bio: data.bio,
          gender: data.gender,
          pronouns: data.pronouns,
          height_cm: data.height_cm,
          interests: data.interests,
          profile_completion_percentage: data.profile_completion_percentage,
          age: new Date().getFullYear() -
            new Date(data.date_of_birth).getFullYear() -
            (new Date() < new Date(data.date_of_birth.replace(/\d{4}/, String(new Date().getFullYear()))) ? 1 : 0),
        };
        setProfile(discoveryProfile);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Unable to load profile");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [accessToken, username]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <Text>Loading profile…</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>{error}</Text>
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={styles.center}>
        <Text>Profile not found</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{profile.display_name}</Text>
        <Text style={styles.username}>@{profile.username}</Text>
      </View>

      {profile.age && (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{profile.age} years old</Text>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Bio</Text>
        <Text style={styles.bio}>{profile.bio || "No bio provided"}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Details</Text>
        <View style={styles.detailRow}>
          <Text style={styles.label}>Gender</Text>
          <Text>{profile.gender}</Text>
        </View>
        {profile.pronouns && (
          <View style={styles.detailRow}>
            <Text style={styles.label}>Pronouns</Text>
            <Text>{profile.pronouns}</Text>
          </View>
        )}
        {profile.height_cm && (
          <View style={styles.detailRow}>
            <Text style={styles.label}>Height</Text>
            <Text>{profile.height_cm} cm</Text>
          </View>
        )}
      </View>

      {profile.interests.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Interests</Text>
          <View style={styles.interestsList}>
            {profile.interests.map((interest) => (
              <View key={interest.id} style={styles.interestTag}>
                <Text style={styles.interestText}>{interest.name}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Profile Completion</Text>
        <View style={styles.progressBar}>
          <View
            style={[
              styles.progressFill,
              { width: `${profile.profile_completion_percentage}%` },
            ]}
          />
        </View>
        <Text style={styles.percentage}>
          {profile.profile_completion_percentage}%
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16, paddingBottom: 32 },
  center: { flex: 1, alignItems: "center", justifyContent: "center", gap: 8 },
  header: { gap: 4, marginBottom: 8 },
  title: { fontSize: 28, fontWeight: "700", color: "#000" },
  username: { fontSize: 16, color: "#666" },
  badge: {
    alignSelf: "flex-start",
    backgroundColor: "#e3f2fd",
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginBottom: 8,
  },
  badgeText: { color: "#1976d2", fontWeight: "600", fontSize: 13 },
  section: { gap: 8, paddingBottom: 12 },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: "#000" },
  bio: { fontSize: 14, color: "#333", lineHeight: 20 },
  detailRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  label: { fontWeight: "600", color: "#666", flex: 1 },
  interestsList: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  interestTag: {
    backgroundColor: "#e3f2fd",
    borderRadius: 16,
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  interestText: { color: "#1976d2", fontSize: 12, fontWeight: "500" },
  progressBar: {
    height: 8,
    backgroundColor: "#e0e0e0",
    borderRadius: 4,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: "#4caf50",
  },
  percentage: {
    fontSize: 12,
    color: "#666",
    marginTop: 4,
  },
  error: { color: "#b00020", fontSize: 16 },
});
