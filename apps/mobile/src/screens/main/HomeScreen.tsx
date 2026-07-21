import { useCallback, useEffect, useState } from "react";
import {
  FlatList,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import type { BottomTabScreenProps } from "@react-navigation/bottom-tabs";
import type { MainTabParamList } from "../../navigation/MainTabNavigator";
import {
  EmptyState,
  ErrorState,
  FeedCard,
  GlassCard,
  ProfileCard,
  ProfileCardSkeleton,
  Skeleton,
} from "../../components";
import { colors, spacing, typography } from "../../theme";
import { useAuthSession } from "../../AuthSession";
import { discovery } from "../../discoveryApi";
import { conversations, Conversation } from "../../conversationsApi";
import { matches } from "../../matchesApi";
import { feed, Post } from "../../feedApi";
import type { DiscoveryProfile, MatchResponse } from "../../types";
import { RecentConversationRow } from "./RecentConversationRow";

type Props = BottomTabScreenProps<MainTabParamList, "Home">;

type LoadState<T> =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; data: T };

function useLoadState<T>() {
  const [state, setState] = useState<LoadState<T>>({ status: "loading" });
  return [state, setState] as const;
}

export function HomeScreen({ navigation }: Props) {
  const { session } = useAuthSession();
  const token = session?.accessToken;

  const [suggestions, setSuggestions] = useLoadState<DiscoveryProfile[]>();
  const [recentConvos, setRecentConvos] =
    useLoadState<
      { conversation: Conversation; match: MatchResponse["match"] | null }[]
    >();
  const [feedPreview, setFeedPreview] = useLoadState<Post[]>();
  const [refreshing, setRefreshing] = useState(false);

  const loadAll = useCallback(async () => {
    if (!token) return;

    setSuggestions({ status: "loading" });
    discovery(token)
      .then((res) =>
        setSuggestions({ status: "ready", data: res.candidates.slice(0, 6) }),
      )
      .catch((err) =>
        setSuggestions({
          status: "error",
          message: err.message ?? "Couldn't load suggestions",
        }),
      );

    setRecentConvos({ status: "loading" });
    Promise.all([conversations(token), matches(token)])
      .then(([convoRes, matchRes]) => {
        const matchById = new Map(matchRes.matches.map((m) => [m.id, m.match]));
        const rows = convoRes.conversations.slice(0, 4).map((c) => ({
          conversation: c,
          match: matchById.get(c.match_id) ?? null,
        }));
        setRecentConvos({ status: "ready", data: rows });
      })
      .catch((err) =>
        setRecentConvos({
          status: "error",
          message: err.message ?? "Couldn't load conversations",
        }),
      );

    setFeedPreview({ status: "loading" });
    feed()
      .then((res) =>
        setFeedPreview({ status: "ready", data: res.posts.slice(0, 2) }),
      )
      .catch((err) =>
        setFeedPreview({
          status: "error",
          message: err.message ?? "Couldn't load feed",
        }),
      );
  }, [token, setSuggestions, setRecentConvos, setFeedPreview]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAll();
    setRefreshing(false);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.text.secondary}
          />
        }
      >
        <Text style={styles.heading}>Home</Text>

        {/* Daily suggestions — reuses /discovery, since there is no
            dedicated "daily suggestions" endpoint yet. */}
        <Section title="Daily suggestions">
          {suggestions.status === "loading" ? (
            <View style={styles.suggestionRow}>
              <ProfileCardSkeleton />
              <ProfileCardSkeleton />
            </View>
          ) : suggestions.status === "error" ? (
            <ErrorState description={suggestions.message} onRetry={loadAll} />
          ) : suggestions.data.length === 0 ? (
            <EmptyState
              icon="search"
              title="No suggestions yet"
              description="Check back soon for new people to meet."
            />
          ) : (
            <FlatList
              data={suggestions.data}
              horizontal
              showsHorizontalScrollIndicator={false}
              keyExtractor={(item) => item.user_id}
              contentContainerStyle={styles.suggestionList}
              renderItem={({ item }) => (
                <View style={styles.suggestionCard}>
                  <ProfileCard
                    name={item.display_name}
                    interests={item.interests.map((i) => i.name)}
                    onPress={() => navigation.navigate("Discover")}
                  />
                </View>
              )}
            />
          )}
        </Section>

        {/* Recent conversations */}
        <Section title="Recent conversations">
          {recentConvos.status === "loading" ? (
            <GlassCard>
              <Skeleton height={44} style={styles.gapSm} />
              <Skeleton height={44} style={styles.gapSm} />
            </GlassCard>
          ) : recentConvos.status === "error" ? (
            <ErrorState description={recentConvos.message} onRetry={loadAll} />
          ) : recentConvos.data.length === 0 ? (
            <EmptyState
              icon="messages"
              title="No conversations yet"
              description="Matches you message will show up here."
            />
          ) : (
            <GlassCard padded={false}>
              {recentConvos.data.map((row, index) => (
                <RecentConversationRow
                  key={row.conversation.id}
                  name={row.match?.display_name ?? "Corvinth member"}
                  onPress={() => navigation.navigate("Messages")}
                  showDivider={index < recentConvos.data.length - 1}
                />
              ))}
            </GlassCard>
          )}
        </Section>

        {/* Feed preview */}
        <Section title="Feed preview">
          {feedPreview.status === "loading" ? (
            <Skeleton height={220} />
          ) : feedPreview.status === "error" ? (
            <ErrorState description={feedPreview.message} onRetry={loadAll} />
          ) : feedPreview.data.length === 0 ? (
            <EmptyState
              icon="image"
              title="Nothing in your feed yet"
              description="Posts from people you follow will appear here."
            />
          ) : (
            <View style={styles.feedList}>
              {feedPreview.data.map((post) => (
                <FeedCard
                  key={post.id}
                  authorName="Corvinth member"
                  caption={post.caption ?? undefined}
                  onPressComment={() => navigation.navigate("Feed")}
                />
              ))}
            </View>
          )}
        </Section>

        {/* AI recommendations — TODO: no backend endpoint exists yet for
            AI-generated recommendations. Wire this up once one is added;
            do not invent the API in the meantime. */}
        <Section title="AI recommendations">
          <EmptyState
            icon="search"
            title="Coming soon"
            description="Personalized AI recommendations will appear here once the backend supports it."
          />
        </Section>
      </ScrollView>
    </SafeAreaView>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.lg,
    paddingBottom: spacing.xxl,
    gap: spacing.xl,
  },
  heading: {
    color: colors.text.primary,
    fontSize: typography.size.display,
    fontWeight: typography.weight.bold,
  },
  section: {
    gap: spacing.sm,
  },
  sectionTitle: {
    color: colors.text.secondary,
    fontSize: typography.size.sm,
    fontWeight: typography.weight.semibold,
    textTransform: "uppercase",
    letterSpacing: 0.4,
  },
  suggestionRow: {
    flexDirection: "row",
    gap: spacing.sm,
  },
  suggestionList: {
    gap: spacing.sm,
  },
  suggestionCard: {
    width: 160,
  },
  gapSm: {
    marginTop: spacing.xs,
  },
  feedList: {
    gap: spacing.lg,
  },
});
