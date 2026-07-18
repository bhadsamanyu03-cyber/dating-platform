import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Animated,
  Button,
  PanResponder,
  Text,
  View,
} from "react-native";
import { act, discovery } from "./discoveryApi";
import { DiscoveryProfile } from "./types";
export function DiscoveryScreen({ accessToken }: { accessToken: string }) {
  const [cards, setCards] = useState<DiscoveryProfile[]>([]);
  const [cursor, setCursor] = useState<string | null>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const translateX = useState(new Animated.Value(0))[0];
  const load = async (retry = false) => {
    setLoading(true);
    setError(undefined);
    try {
      const page = await discovery(
        accessToken,
        retry ? undefined : (cursor ?? undefined),
      );
      setCards((current) =>
        retry ? page.candidates : [...current, ...page.candidates],
      );
      setCursor(page.next_cursor);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load discovery");
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    load(true);
  }, [accessToken]);
  const swipe = async (type: "like" | "pass") => {
    const card = cards[0];
    if (!card) return;
    try {
      await act(accessToken, type, card.user_id);
      setCards((current) => current.slice(1));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to save action");
    }
  };
  const panResponder = PanResponder.create({
    onMoveShouldSetPanResponder: (_, gesture) => Math.abs(gesture.dx) > 8,
    onPanResponderMove: (_, gesture) => translateX.setValue(gesture.dx),
    onPanResponderRelease: (_, gesture) => {
      if (Math.abs(gesture.dx) > 100) {
        swipe(gesture.dx > 0 ? "like" : "pass");
      }
      translateX.setValue(0);
    },
  });
  if (loading && !cards.length)
    return (
      <View>
        <ActivityIndicator />
        <Text>Loading discovery…</Text>
      </View>
    );
  if (error)
    return (
      <View>
        <Text>{error}</Text>
        <Button title="Retry" onPress={() => load(true)} />
      </View>
    );
  const card = cards[0];
  if (!card)
    return (
      <View>
        <Text>
          {cursor
            ? "Loading more profiles…"
            : "You’ve reached the end of discovery."}
        </Text>
        {cursor && <Button title="Load more" onPress={() => load()} />}
      </View>
    );
  return (
    <Animated.View
      {...panResponder.panHandlers}
      style={{ transform: [{ translateX }] }}
    >
      <Text>{card.display_name}</Text>
      <Text>@{card.username}</Text>
      <Text>{card.bio}</Text>
      <Text>{card.interests.map((interest) => interest.name).join(", ")}</Text>
      <Button title="Pass" onPress={() => swipe("pass")} />
      <Button title="Like" onPress={() => swipe("like")} />
    </Animated.View>
  );
}
