import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Button,
  RefreshControl,
  ScrollView,
  Text,
  View,
} from "react-native";
import { feed, Post } from "./feedApi";
export function FeedScreen() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string>();
  const load = async (refresh = false) => {
    refresh ? setRefreshing(true) : setLoading(true);
    try {
      setPosts((await feed()).posts);
      setError(undefined);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load feed");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  useEffect(() => {
    load();
  }, []);
  if (loading)
    return (
      <View>
        <ActivityIndicator />
        <Text>Loading feed…</Text>
      </View>
    );
  if (error)
    return (
      <View>
        <Text>{error}</Text>
        <Button title="Retry" onPress={() => load(true)} />
      </View>
    );
  return (
    <ScrollView
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={() => load(true)} />
      }
    >
      {!posts.length ? (
        <Text>No posts yet.</Text>
      ) : (
        posts.map((post) => (
          <View key={post.id}>
            <Text>{post.caption}</Text>
            {post.media_asset_ids.map((asset, index) => (
              <Text key={asset}>
                {index === 0 ? "Media attachment" : "Carousel item"}
              </Text>
            ))}
          </View>
        ))
      )}
    </ScrollView>
  );
}
