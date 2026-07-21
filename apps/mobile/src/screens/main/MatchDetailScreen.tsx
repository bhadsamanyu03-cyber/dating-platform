import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Button,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { getMatches } from "../../matchesApi";
import { MatchResponse } from "../../types";

type Props = {
  accessToken: string;
  matchId: string;
  onClose: () => void;
  onMessage?: () => void;
};

export function MatchDetailScreen({
  accessToken,
  matchId,
  onClose,
  onMessage,
}: Props) {
  const [match, setMatch] = useState<MatchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(undefined);
      try {
        const data = await getMatches(accessToken);
        const found = data.matches.find((m) => m.id === matchId);
        if (!found) {
          setError("Match not found");
        } else {
          setMatch(found);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Unable to load match");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [accessToken, matchId]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <Text>Loading…</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>{error}</Text>
        <Button title="Close" onPress={onClose} />
      </View>
    );
  }

  if (!match) {
    return (
      <View style={styles.center}>
        <Text>Match not found</Text>
        <Button title="Close" onPress={onClose} />
      </View>
    );
  }

  const { match: profile, created_at } = match;
  const matchedDate = new Date(created_at);
  const daysSinceMatch = Math.floor(
    (Date.now() - matchedDate.getTime()) / (1000 * 60 * 60 * 24),
  );

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{profile.display_name}</Text>
        <Text style={styles.username}>@{profile.username}</Text>
      </View>

      <View style={styles.matchInfo}>
        <Text style={styles.matchInfoText}>
          Matched{" "}
          {daysSinceMatch === 0 ? "today" : `${daysSinceMatch} days ago`}
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <Text style={styles.bio}>
          Open their public profile to learn more about your match.
        </Text>
      </View>

      <View style={styles.actions}>
        <Button title="Message" onPress={onMessage} color="#1976d2" />
        <Button title="Close" onPress={onClose} color="#666" />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, paddingBottom: 32, gap: 16 },
  center: { flex: 1, alignItems: "center", justifyContent: "center", gap: 8 },
  header: { gap: 6, marginBottom: 8 },
  title: { fontSize: 32, fontWeight: "700", color: "#000" },
  username: { fontSize: 18, color: "#666" },
  matchInfo: {
    backgroundColor: "#e3f2fd",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  matchInfoText: {
    fontSize: 13,
    color: "#1976d2",
    fontWeight: "500",
  },
  badge: {
    alignSelf: "flex-start",
    backgroundColor: "#f5f5f5",
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  badgeText: { color: "#333", fontWeight: "600", fontSize: 13 },
  section: { gap: 12, paddingBottom: 4 },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: "#000" },
  bio: { fontSize: 15, color: "#333", lineHeight: 22 },
  infoGrid: { gap: 12 },
  infoItem: {
    backgroundColor: "#f9f9f9",
    borderRadius: 8,
    padding: 12,
  },
  infoLabel: {
    fontSize: 12,
    color: "#999",
    fontWeight: "600",
    marginBottom: 4,
  },
  infoValue: { fontSize: 15, color: "#000", fontWeight: "500" },
  interestsList: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  interestTag: {
    backgroundColor: "#e3f2fd",
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 7,
  },
  interestText: { color: "#1976d2", fontSize: 13, fontWeight: "500" },
  actions: {
    gap: 10,
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: "#f0f0f0",
  },
  error: { color: "#b00020" },
});
