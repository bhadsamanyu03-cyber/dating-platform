import { useState } from "react";
import {
  ActivityIndicator,
  Button,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";

type BlockedUser = {
  id: string;
  username: string;
  display_name: string;
  blocked_at: Date;
};

type Props = {
  accessToken: string;
};

export function BlockedUsersScreen({ accessToken }: Props) {
  const [blockedUsers, setBlockedUsers] = useState<BlockedUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [unblocking, setUnblocking] = useState<Set<string>>(new Set());

  // Placeholder - will integrate with backend when endpoint is available
  const handleLoadBlockedUsers = () => {
    setError(
      "Blocking functionality will be available when the endpoint is implemented"
    );
  };

  const handleUnblock = (userId: string) => {
    setUnblocking((prev) => new Set(prev).add(userId));
    // Simulate unblock
    setTimeout(() => {
      setBlockedUsers((prev) => prev.filter((u) => u.id !== userId));
      setUnblocking((prev) => {
        const next = new Set(prev);
        next.delete(userId);
        return next;
      });
    }, 300);
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <Text>Loading blocked users…</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>{error}</Text>
        <Button title="Retry" onPress={handleLoadBlockedUsers} />
      </View>
    );
  }

  if (!blockedUsers.length) {
    return (
      <View style={styles.center}>
        <Text style={styles.emoji}>🚫</Text>
        <Text style={styles.emptyTitle}>No blocked users</Text>
        <Text style={styles.emptyMessage}>
          Users you block won't be able to see your profile or message you.
        </Text>
      </View>
    );
  }

  return (
    <FlatList
      data={blockedUsers}
      keyExtractor={(item) => item.id}
      contentContainerStyle={styles.container}
      renderItem={({ item }) => (
        <BlockedUserCard
          user={item}
          onUnblock={() => handleUnblock(item.id)}
          isUnblocking={unblocking.has(item.id)}
        />
      )}
      ListHeaderComponent={
        <View style={styles.header}>
          <Text style={styles.title}>Blocked Users</Text>
          <Text style={styles.subtitle}>
            {blockedUsers.length} {blockedUsers.length === 1 ? "user" : "users"} blocked
          </Text>
        </View>
      }
    />
  );
}

function BlockedUserCard(props: {
  user: BlockedUser;
  onUnblock: () => void;
  isUnblocking: boolean;
}) {
  const { user, onUnblock, isUnblocking } = props;
  const blockedDate = user.blocked_at.toLocaleDateString();

  return (
    <View style={styles.card}>
      <View style={styles.cardContent}>
        <View style={styles.userInfo}>
          <Text style={styles.displayName}>{user.display_name}</Text>
          <Text style={styles.username}>@{user.username}</Text>
        </View>
        <Text style={styles.blockedDate}>Blocked {blockedDate}</Text>
      </View>
      <Button
        title={isUnblocking ? "Unblocking…" : "Unblock"}
        onPress={onUnblock}
        disabled={isUnblocking}
        color="#1976d2"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 12 },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
  },
  header: {
    marginBottom: 8,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    color: "#000",
  },
  subtitle: {
    fontSize: 14,
    color: "#666",
    marginTop: 4,
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#f0f0f0",
    padding: 16,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
  },
  cardContent: {
    flex: 1,
    gap: 8,
  },
  userInfo: {
    gap: 2,
  },
  displayName: {
    fontSize: 16,
    fontWeight: "700",
    color: "#000",
  },
  username: {
    fontSize: 13,
    color: "#666",
  },
  blockedDate: {
    fontSize: 12,
    color: "#999",
  },
  emoji: {
    fontSize: 48,
    marginBottom: 8,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#000",
  },
  emptyMessage: {
    fontSize: 14,
    color: "#666",
    textAlign: "center",
    marginHorizontal: 20,
  },
  error: {
    color: "#b00020",
    textAlign: "center",
    marginHorizontal: 20,
  },
});
