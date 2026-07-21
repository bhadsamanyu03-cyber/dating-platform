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

type Notification = {
  id: string;
  type: "match" | "like" | "message" | "system";
  title: string;
  message: string;
  user?: { name: string; username: string };
  timestamp: Date;
  read: boolean;
  action?: { label: string; callback: () => void };
};

type Props = {
  accessToken: string;
};

export function NotificationFeedScreen({ accessToken }: Props) {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: "1",
      type: "system",
      title: "Welcome to Corvinth!",
      message: "Complete your profile to start discovering matches.",
      timestamp: new Date(),
      read: false,
      action: {
        label: "Complete Profile",
        callback: () => {},
      },
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();

  const handleMarkAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const handleDismiss = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const handleMarkAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <Text>Loading notifications…</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>{error}</Text>
        <Button title="Retry" onPress={() => {}} />
      </View>
    );
  }

  if (!notifications.length) {
    return (
      <View style={styles.center}>
        <Text style={styles.emoji}>🔔</Text>
        <Text style={styles.emptyTitle}>No notifications</Text>
        <Text style={styles.emptyMessage}>
          You're all caught up! Matches and activity will appear here.
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>Notifications</Text>
          {unreadCount > 0 && (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{unreadCount}</Text>
            </View>
          )}
        </View>
        {unreadCount > 0 && (
          <Pressable onPress={handleMarkAllAsRead}>
            <Text style={styles.markAllLink}>Mark all as read</Text>
          </Pressable>
        )}
      </View>

      <FlatList
        data={notifications}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        renderItem={({ item }) => (
          <NotificationItem
            notification={item}
            onPress={() => {
              handleMarkAsRead(item.id);
              item.action?.callback();
            }}
            onDismiss={() => handleDismiss(item.id)}
          />
        )}
      />
    </View>
  );
}

function NotificationItem(props: {
  notification: Notification;
  onPress: () => void;
  onDismiss: () => void;
}) {
  const { notification, onPress, onDismiss } = props;

  const getIcon = (): string => {
    switch (notification.type) {
      case "match":
        return "💕";
      case "like":
        return "❤️";
      case "message":
        return "💬";
      case "system":
        return "ℹ️";
      default:
        return "📢";
    }
  };

  const getBackgroundColor = (): string => {
    if (notification.read) return "#f9f9f9";
    switch (notification.type) {
      case "match":
        return "#fce4ec";
      case "like":
        return "#ffebee";
      case "message":
        return "#e3f2fd";
      case "system":
        return "#f5f5f5";
      default:
        return "#f5f5f5";
    }
  };

  const getLeftBorderColor = (): string => {
    if (notification.read) return "#e0e0e0";
    switch (notification.type) {
      case "match":
        return "#c2185b";
      case "like":
        return "#d32f2f";
      case "message":
        return "#1976d2";
      case "system":
        return "#757575";
      default:
        return "#999";
    }
  };

  const timeAgo = getTimeAgo(notification.timestamp);

  return (
    <Pressable
      style={({ pressed }) => [
        styles.notification,
        {
          backgroundColor: getBackgroundColor(),
          borderLeftColor: getLeftBorderColor(),
        },
        pressed && styles.notificationPressed,
      ]}
      onPress={onPress}
    >
      <View style={styles.notificationContent}>
        <View style={styles.notificationHeader}>
          <Text style={styles.icon}>{getIcon()}</Text>
          <View style={styles.textContent}>
            <Text style={styles.title}>{notification.title}</Text>
            <Text style={styles.message}>{notification.message}</Text>
            {notification.user && (
              <Text style={styles.user}>
                @{notification.user.username}
              </Text>
            )}
          </View>
        </View>
        <Text style={styles.timestamp}>{timeAgo}</Text>
      </View>

      {!notification.read && (
        <View style={styles.unreadIndicator} />
      )}

      <View style={styles.actions}>
        <Pressable onPress={onDismiss} style={styles.dismissButton}>
          <Text style={styles.dismissText}>✕</Text>
        </Pressable>
      </View>
    </Pressable>
  );
}

function getTimeAgo(date: Date): string {
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;

  return date.toLocaleDateString();
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  headerContent: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#000",
  },
  badge: {
    backgroundColor: "#d32f2f",
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  badgeText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "700",
  },
  markAllLink: {
    color: "#1976d2",
    fontSize: 13,
    fontWeight: "600",
  },
  listContent: {
    padding: 12,
    gap: 8,
  },
  notification: {
    flexDirection: "row",
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    gap: 12,
    alignItems: "center",
  },
  notificationPressed: {
    opacity: 0.7,
  },
  notificationContent: {
    flex: 1,
    gap: 8,
  },
  notificationHeader: {
    flexDirection: "row",
    gap: 10,
  },
  icon: {
    fontSize: 24,
  },
  textContent: {
    flex: 1,
    gap: 2,
  },
  title: {
    fontSize: 15,
    fontWeight: "700",
    color: "#000",
  },
  message: {
    fontSize: 13,
    color: "#666",
    lineHeight: 18,
  },
  user: {
    fontSize: 12,
    color: "#999",
    fontStyle: "italic",
  },
  timestamp: {
    fontSize: 12,
    color: "#999",
  },
  unreadIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#d32f2f",
    marginRight: 8,
  },
  actions: {
    justifyContent: "flex-end",
  },
  dismissButton: {
    padding: 8,
  },
  dismissText: {
    fontSize: 16,
    color: "#ccc",
  },
  error: {
    color: "#b00020",
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
});
