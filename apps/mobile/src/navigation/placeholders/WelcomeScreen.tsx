import { Button, Text, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { AuthStackParamList } from "../AuthNavigator";
type Props = NativeStackScreenProps<AuthStackParamList, "Welcome">;
export function WelcomeScreen({ navigation }: Props) {
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text>Corvinth</Text>
      <Text>Meet people with intention.</Text>
      <Button title="Sign in" onPress={() => navigation.navigate("Login")} />
      <Button
        title="Create account"
        onPress={() => navigation.navigate("Register")}
      />
    </View>
  );
}
