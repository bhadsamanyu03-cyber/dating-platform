import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Button,
  RefreshControl,
  Image,
  ScrollView,
  TextInput,
  Text,
  View,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import { createPost, feed, Post } from "./feedApi";
import { mediaDownloadUrl, uploadMediaAsset } from "./mediaApi";
import { useAuthSession } from "./AuthSession";
export function FeedScreen() {
  const { session } = useAuthSession();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string>();
  const [caption, setCaption] = useState("");
  const [draftUris, setDraftUris] = useState<string[]>([]);
  const [posting, setPosting] = useState(false);
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
  const pickMedia = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      setError("Photo library permission is required.");
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images", "videos"],
      allowsMultipleSelection: true,
      selectionLimit: 12,
      quality: 0.9,
    });
    if (!result.canceled) {
      setDraftUris(result.assets.map((asset) => asset.uri));
    }
  };
  const submit = async () => {
    if (!session) return;
    if (!caption.trim() && !draftUris.length) return;
    setPosting(true);
    setError(undefined);
    try {
      const assets = await Promise.all(
        draftUris.map(
          async (uri) => (await uploadMediaAsset(session.accessToken, uri)).id,
        ),
      );
      const created = await createPost(session.accessToken, {
        caption: caption.trim() || undefined,
        media_asset_ids: assets,
      });
      setPosts((current) => [created, ...current]);
      setCaption("");
      setDraftUris([]);
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Unable to create post",
      );
    } finally {
      setPosting(false);
    }
  };
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
      <View style={{ gap: 12, padding: 16 }}>
        <Text style={{ fontSize: 18, fontWeight: "700" }}>Create post</Text>
        <TextInput
          placeholder="Say something..."
          value={caption}
          onChangeText={setCaption}
          style={{
            borderWidth: 1,
            borderColor: "#ddd",
            borderRadius: 10,
            padding: 12,
            minHeight: 80,
            textAlignVertical: "top",
          }}
          multiline
          maxLength={500}
        />
        <Button title="Add media" onPress={pickMedia} />
        {!!draftUris.length && (
          <ScrollView horizontal contentContainerStyle={{ gap: 8 }}>
            {draftUris.map((uri) => (
              <Image
                key={uri}
                source={{ uri }}
                style={{ width: 96, height: 96, borderRadius: 8 }}
              />
            ))}
          </ScrollView>
        )}
        <Button
          title={posting ? "Posting…" : "Post"}
          disabled={posting}
          onPress={submit}
        />
      </View>
      {!posts.length ? (
        <Text>No posts yet.</Text>
      ) : (
        posts.map((post) => (
          <View key={post.id} style={{ padding: 16, gap: 8 }}>
            <Text>{post.caption}</Text>
            {post.media_asset_ids.map((asset, index) => (
              <Image
                key={asset}
                source={{
                  uri: mediaDownloadUrl(asset),
                  headers: session
                    ? { Authorization: `Bearer ${session.accessToken}` }
                    : undefined,
                }}
                style={{
                  width: "100%",
                  height: 220,
                  borderRadius: 12,
                  backgroundColor: "#eee",
                }}
                accessibilityLabel={
                  index === 0 ? "Feed media" : "Carousel item"
                }
              />
            ))}
          </View>
        ))
      )}
    </ScrollView>
  );
}
