import { useState } from "react";
import { Button, Text, TextInput, View } from "react-native";
import { apiBaseUrl as baseUrl } from "./runtimeConfig";
export function SearchScreen({ accessToken }: { accessToken: string }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<
    { user_id: string; display_name: string; username: string }[]
  >([]);
  const [error, setError] = useState<string>();
  const search = async () => {
    if (!query.trim()) return;
    try {
      const response = await fetch(
        `${baseUrl}/search/users?query=${encodeURIComponent(query)}`,
        { headers: { Authorization: `Bearer ${accessToken}` } },
      );
      if (!response.ok) throw new Error((await response.json()).detail);
      setResults(await response.json());
      setError(undefined);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to search");
    }
  };
  return (
    <View>
      <TextInput
        placeholder="Search users"
        value={query}
        onChangeText={setQuery}
      />
      <Button title="Search" onPress={search} />
      {error && <Text>{error}</Text>}
      {!error && !results.length && <Text>No results yet.</Text>}
      {results.map((value) => (
        <Text key={value.user_id}>
          {value.display_name} @{value.username}
        </Text>
      ))}
    </View>
  );
}
