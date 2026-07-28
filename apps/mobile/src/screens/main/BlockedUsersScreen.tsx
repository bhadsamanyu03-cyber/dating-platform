import { Button, Text, View } from "react-native";

type Props = {
  accessToken: string;
};

export function BlockedUsersScreen({ accessToken: _accessToken }: Props) {
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: "700" }}>Blocked users</Text>
      <Text>
        The backend currently enforces blocking in discovery and interactions,
        but it does not expose a block-list management endpoint yet.
      </Text>
      <Button title="Back" onPress={() => {}} />
    </View>
  );
}
