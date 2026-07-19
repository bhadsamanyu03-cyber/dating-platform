import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Button,
  Image,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import {
  attachmentUrl,
  Conversation,
  conversations,
  Message,
  messages,
  sendMessage,
  uploadImage,
} from "./conversationsApi";

const temporaryId = () => `local-${Date.now()}-${Math.random()}`;

export function ConversationsScreen({ accessToken }: { accessToken: string }) {
  const [items, setItems] = useState<Conversation[]>([]);
  const [selected, setSelected] = useState<Conversation>();
  const [itemsMessages, setItemsMessages] = useState<Message[]>([]);
  const [cursor, setCursor] = useState<string | null>();
  const [text, setText] = useState("");
  const [attachmentUris, setAttachmentUris] = useState<string[]>([]);
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(true);
  const load = async () => {
    setLoading(true);
    try {
      setItems((await conversations(accessToken)).conversations);
      setError(undefined);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load conversations");
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    load();
  }, [accessToken]);
  const open = async (value: Conversation, next?: string) => {
    setSelected(value);
    try {
      const page = await messages(accessToken, value.id, next);
      setItemsMessages((current) =>
        next ? [...current, ...page.messages] : page.messages,
      );
      setCursor(page.next_cursor);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load messages");
    }
  };
  const submit = async (draft: Message) => {
    if (!selected) return;
    try {
      const message = await sendMessage(accessToken, selected.id, {
        text_content: draft.text_content ?? undefined,
        media_asset_ids: draft.media_asset_ids,
        client_message_id: draft.client_message_id!,
      });
      setItemsMessages((current) =>
        current.map((value) => (value.id === draft.id ? message : value)),
      );
    } catch {
      setItemsMessages((current) =>
        current.map((value) =>
          value.id === draft.id
            ? { ...value, pending: false, failed: true }
            : value,
        ),
      );
    }
  };
  const pickImages = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted)
      return setError("Photo library permission is required.");
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      allowsMultipleSelection: true,
      selectionLimit: 10,
      quality: 0.9,
    });
    if (!result.canceled)
      setAttachmentUris(
        result.assets.map((asset: ImagePicker.ImagePickerAsset) => asset.uri),
      );
  };
  const send = async () => {
    const value = text.trim();
    if (!value && !attachmentUris.length) return;
    let assets: string[] = [];
    try {
      assets = await Promise.all(
        attachmentUris.map(
          async (uri) => (await uploadImage(accessToken, uri)).id,
        ),
      );
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Unable to upload image",
      );
      return;
    }
    const clientMessageId = globalThis.crypto?.randomUUID?.() ?? temporaryId();
    const draft: Message = {
      id: temporaryId(),
      sender_user_id: "me",
      message_type: assets.length ? "IMAGE" : "TEXT",
      text_content: value || null,
      media_asset_ids: assets,
      created_at: new Date().toISOString(),
      delivered_at: null,
      read_at: null,
      deleted_at: null,
      client_message_id: clientMessageId,
      pending: true,
    };
    setItemsMessages((current) => [draft, ...current]);
    setText("");
    setAttachmentUris([]);
    void submit(draft);
  };
  if (loading)
    return (
      <View>
        <ActivityIndicator />
        <Text>Loading conversations…</Text>
      </View>
    );
  if (error && !selected)
    return (
      <View>
        <Text>{error}</Text>
        <Button title="Retry" onPress={load} />
      </View>
    );
  if (selected)
    return (
      <View style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={{ flexDirection: "column" }}>
          {!itemsMessages.length && <Text>No messages yet.</Text>}
          {itemsMessages.map((value) => (
            <View key={value.id}>
              <Text>{value.text_content}</Text>
              {value.media_asset_ids.map((asset) => (
                <Image
                  key={asset}
                  source={{
                    uri: value.id.startsWith("local-")
                      ? asset
                      : attachmentUrl(value.id, asset),
                    headers: { Authorization: `Bearer ${accessToken}` },
                  }}
                  style={{ width: 120, height: 120 }}
                  accessibilityLabel="Message image"
                />
              ))}
              <Text>
                {value.failed
                  ? "Failed"
                  : value.pending
                    ? "Sending…"
                    : value.read_at
                      ? "Read"
                      : value.delivered_at
                        ? "Delivered"
                        : "Sent"}
              </Text>
              {value.failed && (
                <Button
                  title="Retry send"
                  onPress={() =>
                    submit({ ...value, failed: false, pending: true })
                  }
                />
              )}
            </View>
          ))}
          {cursor && (
            <Button
              title="Load older messages"
              onPress={() => open(selected, cursor)}
            />
          )}
        </ScrollView>
        {attachmentUris.map((uri) => (
          <Image
            key={uri}
            source={{ uri }}
            style={{ width: 80, height: 80 }}
            accessibilityLabel="Image preview"
          />
        ))}
        {error && <Text>{error}</Text>}
        <TextInput
          value={text}
          onChangeText={setText}
          placeholder="Message"
          maxLength={4000}
        />
        <Button title="Add images" onPress={pickImages} />
        <Button title="Send" onPress={send} />
        <Button title="Back" onPress={() => setSelected(undefined)} />
      </View>
    );
  return (
    <View>
      {!items.length ? (
        <Text>No conversations yet.</Text>
      ) : (
        items.map((value) => (
          <Button
            key={value.id}
            title={`Conversation ${value.id.slice(0, 8)}`}
            onPress={() => open(value)}
          />
        ))
      )}
    </View>
  );
}
