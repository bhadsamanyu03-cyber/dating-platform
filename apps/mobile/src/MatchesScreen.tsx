import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Button,
  RefreshControl,
  ScrollView,
  Text,
  View,
} from "react-native";
import { matches, removeMatch } from "./matchesApi";
import { MatchResponse } from "./types";

export function MatchesScreen({ accessToken }: { accessToken: string }) {
  const [items, setItems] = useState<MatchResponse[]>([]);
  const [cursor, setCursor] = useState<string | null>();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string>();
  const [selected, setSelected] = useState<MatchResponse>();
  const load = useCallback(
    async (refresh = false) => {
      refresh ? setRefreshing(true) : setLoading(true);
      setError(undefined);
      try {
        const page = await matches(
          accessToken,
          refresh ? undefined : (cursor ?? undefined),
        );
        setItems((current) =>
          refresh ? page.matches : [...current, ...page.matches],
        );
        setCursor(page.next_cursor);
      } catch (cause) {
        setError(
          cause instanceof Error ? cause.message : "Unable to load matches",
        );
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [accessToken, cursor],
  );
  useEffect(() => {
    load(true);
  }, [accessToken]);
  const unmatch = async (item: MatchResponse) => {
    try {
      await removeMatch(accessToken, item.id);
      setItems((current) => current.filter((value) => value.id !== item.id));
      setSelected(undefined);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to unmatch");
    }
  };
  if (loading && !items.length)
    return (
      <View>
        <ActivityIndicator />
        <Text>Loading matches…</Text>
      </View>
    );
  if (error)
    return (
      <View>
        <Text>{error}</Text>
        <Button title="Retry" onPress={() => load(true)} />
      </View>
    );
  if (selected)
    return (
      <View>
        <Text>{selected.match.display_name}</Text>
        <Text>@{selected.match.username}</Text>
        <Text>Match detail</Text>
        <Button title="Unmatch" onPress={() => unmatch(selected)} />
        <Button title="Back" onPress={() => setSelected(undefined)} />
      </View>
    );
  return (
    <ScrollView
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={() => load(true)} />
      }
    >
      <Text>Matches</Text>
      {!items.length ? (
        <Text>You do not have any matches yet.</Text>
      ) : (
        items.map((item) => (
          <View key={item.id}>
            <Text>{item.match.display_name}</Text>
            <Text>@{item.match.username}</Text>
            <Button title="View match" onPress={() => setSelected(item)} />
          </View>
        ))
      )}
      {cursor && <Button title="Load more" onPress={() => load()} />}
    </ScrollView>
  );
}
