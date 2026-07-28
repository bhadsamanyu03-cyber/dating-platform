import { Button, Text, View } from "react-native";

export function PlaceholderScreen({
  title,
  description = "Open the signed-in app to continue.",
}: {
  title: string;
  description?: string;
}) {
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: "700" }}>{title}</Text>
      <Text>{description}</Text>
      <Button title="Back" onPress={() => {}} />
    </View>
  );
}
