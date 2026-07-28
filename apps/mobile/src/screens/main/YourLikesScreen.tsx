import { Button, Text, View } from "react-native";

type Props = {
  accessToken: string;
};

export function YourLikesScreen({ accessToken: _accessToken }: Props) {
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: "700" }}>Likes you</Text>
      <Text>
        This app version does not expose a backend endpoint for the incoming
        likes list yet. Discovery, matches, feed, messaging, notifications, and
        profile screens are connected.
      </Text>
      <Button title="Back" onPress={() => {}} />
    </View>
  );
}
