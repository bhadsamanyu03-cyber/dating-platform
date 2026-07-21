import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { getMyProfile } from "../../profileApi";
import { getMatches } from "../../discoveryApi";

type Props = {
  accessToken: string;
};

export function QuickStatsScreen({ accessToken }: Props) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [stats, setStats] = useState({
    profileCompletion: 0,
    totalMatches: 0,
    profilePhotos: 0,
    interests: 0,
  });

  useEffect(() => {
    loadStats();
  }, [accessToken]);

  const loadStats = async () => {
    setLoading(true);
    setError(undefined);
    try {
      const [profile, matches] = await Promise.all([
        getMyProfile(accessToken),
        getMatches(accessToken),
      ]);

      setStats({
        profileCompletion: profile.profile_completion_percentage,
        totalMatches: matches.total_count,
        profilePhotos: profile.profile_photo_count,
        interests: profile.interests.length,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load stats");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <Text>Loading stats…</Text>
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

  const completionColor =
    stats.profileCompletion >= 100 ? "#4caf50" :
    stats.profileCompletion >= 75 ? "#8bc34a" :
    stats.profileCompletion >= 50 ? "#ff9800" :
    "#f44336";

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Your Stats</Text>
        <Text style={styles.subtitle}>Profile & engagement overview</Text>
      </View>

      <View style={styles.statsGrid}>
        <StatCard
          icon="📊"
          label="Profile Completion"
          value={`${stats.profileCompletion}%`}
          color={completionColor}
          subtext={
            stats.profileCompletion < 100
              ? `${100 - stats.profileCompletion}% to complete`
              : "Profile complete!"
          }
        />
        <StatCard
          icon="💕"
          label="Total Matches"
          value={stats.totalMatches.toString()}
          color="#e91e63"
          subtext={
            stats.totalMatches > 0
              ? "Keep discovering!"
              : "Start swiping to make matches"
          }
        />
        <StatCard
          icon="📸"
          label="Profile Photos"
          value={`${stats.profilePhotos}/12`}
          color="#2196f3"
          subtext={
            stats.profilePhotos > 0
              ? `${12 - stats.profilePhotos} more can be added`
              : "Add photos to stand out"
          }
        />
        <StatCard
          icon="✨"
          label="Interests"
          value={stats.interests.toString()}
          color="#ff9800"
          subtext={
            stats.interests > 0
              ? "Help match with like-minded people"
              : "Add interests to improve matches"
          }
        />
      </View>

      <View style={styles.tips}>
        <Text style={styles.tipsTitle}>💡 Profile Tips</Text>
        {stats.profileCompletion < 100 && (
          <TipItem text="Complete your profile to unlock more features" />
        )}
        {stats.profilePhotos < 3 && (
          <TipItem text="Add multiple photos to get more matches" />
        )}
        {stats.interests < 3 && (
          <TipItem text="Select at least 3 interests for better compatibility" />
        )}
        <TipItem text="Keep your bio engaging and authentic" />
        <TipItem text="Respond quickly to messages to build connections" />
      </View>

      <View style={styles.achievements}>
        <Text style={styles.achievementsTitle}>🏆 Milestones</Text>
        <Achievement
          completed={stats.profileCompletion === 100}
          icon="✓"
          text="Complete Profile"
        />
        <Achievement
          completed={stats.profilePhotos >= 3}
          icon="📸"
          text="Add 3+ Photos"
        />
        <Achievement
          completed={stats.totalMatches >= 1}
          icon="💕"
          text="Get Your First Match"
        />
        <Achievement
          completed={stats.interests >= 5}
          icon="✨"
          text="Add 5 Interests"
        />
      </View>
    </ScrollView>
  );
}

function StatCard(props: {
  icon: string;
  label: string;
  value: string;
  color: string;
  subtext: string;
}) {
  return (
    <View style={styles.statCard}>
      <Text style={styles.statIcon}>{props.icon}</Text>
      <Text style={styles.statLabel}>{props.label}</Text>
      <Text style={[styles.statValue, { color: props.color }]}>
        {props.value}
      </Text>
      <Text style={styles.statSubtext}>{props.subtext}</Text>
    </View>
  );
}

function TipItem({ text }: { text: string }) {
  return (
    <Text style={styles.tipText}>
      • {text}
    </Text>
  );
}

function Achievement(props: {
  completed: boolean;
  icon: string;
  text: string;
}) {
  return (
    <View
      style={[
        styles.achievement,
        !props.completed && styles.achievementIncomplete,
      ]}
    >
      <Text style={styles.achievementIcon}>{props.icon}</Text>
      <Text
        style={[
          styles.achievementText,
          !props.completed && styles.achievementTextIncomplete,
        ]}
      >
        {props.text}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 16 },
  center: { flex: 1, alignItems: "center", justifyContent: "center", gap: 8 },
  header: { gap: 4, marginBottom: 8 },
  title: { fontSize: 24, fontWeight: "700", color: "#000" },
  subtitle: { fontSize: 14, color: "#666" },
  statsGrid: {
    gap: 12,
  },
  statCard: {
    backgroundColor: "#f9f9f9",
    borderRadius: 12,
    padding: 16,
    gap: 8,
    borderWidth: 1,
    borderColor: "#f0f0f0",
  },
  statIcon: {
    fontSize: 32,
  },
  statLabel: {
    fontSize: 12,
    color: "#999",
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  statValue: {
    fontSize: 28,
    fontWeight: "700",
  },
  statSubtext: {
    fontSize: 12,
    color: "#999",
    lineHeight: 16,
  },
  tips: {
    backgroundColor: "#e3f2fd",
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: "#1976d2",
    padding: 16,
    gap: 8,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#1565c0",
    marginBottom: 4,
  },
  tipText: {
    fontSize: 13,
    color: "#1565c0",
    lineHeight: 18,
  },
  achievements: {
    gap: 12,
    paddingBottom: 16,
  },
  achievementsTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#000",
  },
  achievement: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    padding: 12,
    backgroundColor: "#e8f5e9",
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#4caf50",
  },
  achievementIncomplete: {
    backgroundColor: "#f5f5f5",
    borderColor: "#e0e0e0",
  },
  achievementIcon: {
    fontSize: 20,
  },
  achievementText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#2e7d32",
    flex: 1,
  },
  achievementTextIncomplete: {
    color: "#999",
  },
  error: {
    color: "#b00020",
  },
});
