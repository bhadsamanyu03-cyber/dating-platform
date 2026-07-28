import { Button, Text, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { AuthStackParamList } from "../AuthNavigator";

type Props = NativeStackScreenProps<AuthStackParamList, "CreateProfile">;

export function CreateProfileScreen({ navigation }: Props) {
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: "700" }}>Create profile</Text>
      <Text>
        Finish sign-in, then open the Profile tab to complete your profile and
        photos.
      </Text>
      <Button title="Back" onPress={() => navigation.goBack()} />
    </View>
  );
}
