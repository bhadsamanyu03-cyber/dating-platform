import { useEffect, useState } from "react";
import { ActivityIndicator, Button, Text, TextInput, View } from "react-native";
import {
  Conversation,
  conversations,
  Message,
  messages,
  sendText,
} from "./conversationsApi";
export function ConversationsScreen({ accessToken }: { accessToken: string }) {
  const [items, setItems] = useState<Conversation[]>([]);
  const [selected, setSelected] = useState<Conversation>();
  const [itemsMessages, setItemsMessages] = useState<Message[]>([]);
  const [text, setText] = useState("");
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
  const open = async (value: Conversation) => {
    setSelected(value);
    try {
      setItemsMessages((await messages(accessToken, value.id)).messages);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load messages");
    }
  };
  const send = async () => {
    if (!selected || !text.trim()) return;
    try {
      const message = await sendText(accessToken, selected.id, text.trim());
      setItemsMessages((current) => [...current, message]);
      setText("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to send message");
    }
  };
  if (loading)
    return (
      <View>
        <ActivityIndicator />
        <Text>Loading conversations…</Text>
      </View>
    );
  if (error)
    return (
      <View>
        <Text>{error}</Text>
        <Button title="Retry" onPress={load} />
      </View>
    );
  if (selected)
    return (
      <View>
        {!itemsMessages.length ? (
          <Text>No messages yet.</Text>
        ) : (
          itemsMessages.map((value) => (
            <Text key={value.id}>
              {value.message_type === "TEXT"
                ? value.text_content
                : `${value.message_type} attachment`}
            </Text>
          ))
        )}
        <TextInput value={text} onChangeText={setText} placeholder="Message" />
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
