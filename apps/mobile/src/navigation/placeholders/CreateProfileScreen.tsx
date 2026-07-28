import { Button, Text, View } from "react-native";

export function CreateProfileScreen() {
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: "700" }}>Create profile</Text>
      <Text>
        Finish sign-in, then open the Profile tab to complete your profile and
        photos.
      </Text>
      <Button title="Back" onPress={() => {}} />
    </View>
  );
}
