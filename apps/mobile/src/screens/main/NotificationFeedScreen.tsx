import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Button,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import {
  markAllNotificationsRead,
  markNotificationRead,
  Notification,
  notifications,
  unreadCount,
} from "../../notificationsApi";

type Props = {
  accessToken: string;
};

export function NotificationFeedScreen({ accessToken }: Props) {
  const [items, setItems] = useState<Notification[]>([]);
  const [cursor, setCursor] = useState<string | null>();
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string>();

  const load = async (refresh = false) => {
    refresh ? setRefreshing(true) : setLoading(true);
    setError(undefined);
    try {
      const [page, count] = await Promise.all([
        notifications(accessToken, refresh ? undefined : (cursor ?? undefined)),
        unreadCount(accessToken),
      ]);
      setItems((current) =>
        refresh ? page.notifications : [...current, ...page.notifications],
      );
      setCursor(page.next_cursor);
      setUnread(count.count);
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Unable to load notifications",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void load(true);
  }, [accessToken]);

  const markRead = async (notification: Notification) => {
    if (notification.is_read) return;
    try {
      await markNotificationRead(accessToken, notification.id);
      setItems((current) =>
        current.map((item) =>
          item.id === notification.id ? { ...item, is_read: true } : item,
        ),
      );
      setUnread((current) => Math.max(0, current - 1));
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Unable to update notification",
      );
    }
  };

  const markAllRead = async () => {
    try {
      await markAllNotificationsRead(accessToken);
      setItems((current) =>
        current.map((item) => ({ ...item, is_read: true })),
      );
      setUnread(0);
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Unable to update notifications",
      );
    }
  };

  if (loading && !items.length) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <Text>Loading notifications...</Text>
      </View>
    );
  }

  if (error && !items.length) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>{error}</Text>
        <Button title="Retry" onPress={() => load(true)} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Notifications</Text>
        {unread > 0 && <Text style={styles.badge}>{unread}</Text>}
        {unread > 0 && <Button title="Mark all read" onPress={markAllRead} />}
      </View>

      <FlatList
        data={items}
        keyExtractor={(item) => item.id}
        refreshing={refreshing}
        onRefresh={() => load(true)}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.center}>
            <Text style={styles.emptyTitle}>No notifications</Text>
            <Text style={styles.emptyMessage}>
              Matches, likes, messages, and moderation updates will appear here.
            </Text>
          </View>
        }
        renderItem={({ item }) => (
          <NotificationItem
            notification={item}
            onPress={() => markRead(item)}
          />
        )}
        ListFooterComponent={
          cursor ? <Button title="Load more" onPress={() => load()} /> : null
        }
      />
    </View>
  );
}

function NotificationItem(props: {
  notification: Notification;
  onPress: () => void;
}) {
  const { notification, onPress } = props;
  return (
    <Pressable
      style={[styles.notification, !notification.is_read && styles.unread]}
      onPress={onPress}
    >
      <Text style={styles.title}>{notification.type.replace(/_/g, " ")}</Text>
      <Text style={styles.message}>{notificationMessage(notification)}</Text>
      <Text style={styles.timestamp}>
        {new Date(notification.created_at).toLocaleString()}
      </Text>
    </Pressable>
  );
}

function notificationMessage(notification: Notification) {
  const payload = notification.payload;
  if (payload.message) return payload.message;
  if (payload.conversation_id) return "You have a new message.";
  if (payload.match_id) return "You have a new match.";
  if (payload.post_id) return "There is new activity on your post.";
  return "You have a new update.";
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    padding: 24,
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  headerTitle: { fontSize: 18, fontWeight: "700", color: "#000", flex: 1 },
  badge: {
    backgroundColor: "#d32f2f",
    color: "#fff",
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    overflow: "hidden",
    fontWeight: "700",
  },
  listContent: { padding: 12, gap: 8, flexGrow: 1 },
  notification: {
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: "#e0e0e0",
    backgroundColor: "#f9f9f9",
    gap: 6,
  },
  unread: {
    borderLeftColor: "#1976d2",
    backgroundColor: "#e3f2fd",
  },
  title: { fontSize: 15, fontWeight: "700", color: "#000" },
  message: { fontSize: 13, color: "#666", lineHeight: 18 },
  timestamp: { fontSize: 12, color: "#999" },
  emptyTitle: { fontSize: 18, fontWeight: "700", color: "#000" },
  emptyMessage: { fontSize: 14, color: "#666", textAlign: "center" },
  error: { color: "#b00020", textAlign: "center" },
});
