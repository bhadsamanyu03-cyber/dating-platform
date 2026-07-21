import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Button,
  FlatList,
  Modal,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { DiscoveryProfile } from "../../types";

type Props = {
  accessToken: string;
};

export function YourLikesScreen({ accessToken }: Props) {
  const [likes, setLikes] = useState<DiscoveryProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [refreshing, setRefreshing] = useState(false);
  const [viewingProfile, setViewingProfile] = useState<DiscoveryProfile | null>(
    null,
  );

  const load = async () => {
    setLoading(true);
    setError(undefined);
    try {
      // TODO: Call GET /api/v1/discovery/likes-received when endpoint is available
      // For now, show empty state with helpful message
      setLikes([]);
      setError(
        'The "Likes You" feature is coming soon! Complete your profile to enable this feature.',
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load likes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [accessToken]);

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      // TODO: Implement when endpoint available
      setLikes([]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to refresh");
    } finally {
      setRefreshing(false);
    }
  };

  if (loading && !likes.length) {
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
        <Text style={styles.message}>{error}</Text>
        <Button title="Retry" onPress={load} />
      </View>
    );
  }

  if (!likes.length) {
    return (
      <View style={styles.center}>
        <Text style={styles.message}>
          No one has liked you yet. Keep discovering!
        </Text>
        <Button title="Go to Discovery" color="#1976d2" onPress={() => {}} />
      </View>
    );
  }

  return (
    <>
      <FlatList
        data={likes}
        keyExtractor={(item) => item.user_id}
        contentContainerStyle={styles.container}
        onRefresh={onRefresh}
        refreshing={refreshing}
        renderItem={({ item }) => (
          <LikeCard
            profile={item}
            onViewProfile={() => setViewingProfile(item)}
            onLike={() => {}}
            onPass={() => {}}
          />
        )}
      />
      <Modal
        visible={!!viewingProfile}
        onRequestClose={() => setViewingProfile(null)}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <View style={styles.modalHeader}>
          <Button title="Close" onPress={() => setViewingProfile(null)} />
        </View>
        {viewingProfile && <LikeDetailView profile={viewingProfile} />}
      </Modal>
    </>
  );
}

function LikeCard(props: {
  profile: DiscoveryProfile;
  onViewProfile: () => void;
  onLike: () => void;
  onPass: () => void;
}) {
  const { profile, onViewProfile, onLike, onPass } = props;

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.title}>
          <Text style={styles.displayName}>{profile.display_name}</Text>
          <Text style={styles.username}>@{profile.username}</Text>
          {profile.age && (
            <Text style={styles.age}>{profile.age} years old</Text>
          )}
        </View>
      </View>

      <Text style={styles.bio}>{profile.bio}</Text>

      {profile.interests.length > 0 && (
        <View style={styles.interests}>
          <View style={styles.interestsList}>
            {profile.interests.slice(0, 3).map((interest) => (
              <View key={interest.id} style={styles.interestTag}>
                <Text style={styles.interestText}>{interest.name}</Text>
              </View>
            ))}
            {profile.interests.length > 3 && (
              <Text style={styles.moreInterests}>
                +{profile.interests.length - 3} more
              </Text>
            )}
          </View>
        </View>
      )}

      <View style={styles.actions}>
        <Button title="View Profile" onPress={onViewProfile} color="#1976d2" />
        <Button title="Like Back" onPress={onLike} color="#4caf50" />
        <Button title="Pass" onPress={onPass} color="#ccc" />
      </View>
    </View>
  );
}

function LikeDetailView({ profile }: { profile: DiscoveryProfile }) {
  return (
    <View style={styles.detailContainer}>
      <Text style={styles.detailTitle}>{profile.display_name}</Text>
      <Text style={styles.detailUsername}>@{profile.username}</Text>

      {profile.age && (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{profile.age} years old</Text>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Bio</Text>
        <Text style={styles.bio}>{profile.bio || "No bio provided"}</Text>
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
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: "center", justifyContent: "center", gap: 12 },
  container: { padding: 12, gap: 12 },
  message: {
    fontSize: 16,
    color: "#666",
    textAlign: "center",
    marginHorizontal: 20,
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#f0c020",
    padding: 16,
    gap: 12,
    marginBottom: 4,
    borderLeftWidth: 4,
    borderLeftColor: "#f0c020",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  title: { flex: 1, gap: 4 },
  displayName: {
    fontSize: 18,
    fontWeight: "700",
    color: "#000",
  },
  username: {
    fontSize: 14,
    color: "#666",
  },
  age: {
    fontSize: 13,
    color: "#999",
    marginTop: 2,
  },
  bio: {
    fontSize: 14,
    color: "#333",
    lineHeight: 20,
  },
  interests: { gap: 8 },
  interestsList: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
  },
  interestTag: {
    backgroundColor: "#fff8e1",
    borderRadius: 16,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderWidth: 1,
    borderColor: "#f0c020",
  },
  interestText: {
    fontSize: 12,
    color: "#f57f17",
    fontWeight: "500",
  },
  moreInterests: {
    fontSize: 12,
    color: "#999",
    fontStyle: "italic",
    alignSelf: "center",
  },
  actions: {
    gap: 8,
    marginTop: 8,
  },
  modalHeader: { paddingHorizontal: 12, paddingVertical: 8 },
  detailContainer: { padding: 16, gap: 16 },
  detailTitle: {
    fontSize: 28,
    fontWeight: "700",
    color: "#000",
  },
  detailUsername: {
    fontSize: 16,
    color: "#666",
  },
  badge: {
    alignSelf: "flex-start",
    backgroundColor: "#fff8e1",
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: "#f0c020",
  },
  badgeText: {
    color: "#f57f17",
    fontWeight: "600",
    fontSize: 13,
  },
  section: { gap: 8 },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#000",
  },
});
