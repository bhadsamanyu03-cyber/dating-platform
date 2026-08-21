import { Button, Text, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { AuthStackParamList } from "../AuthNavigator";
import { colors } from "../../theme";
type Props = NativeStackScreenProps<AuthStackParamList, "Welcome">;
export function WelcomeScreen({ navigation }: Props) {
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12, backgroundColor: colors.background }}>
      <Text style={{ color: colors.text.primary, fontSize: 28, fontWeight: "700" }}>Corvinth</Text>
      <Text style={{ color: colors.text.secondary, fontSize: 18 }}>Meet people with intention.</Text>
      <Button title="Sign in" onPress={() => navigation.navigate("Login")} />
      <Button
        title="Create account"
        onPress={() => navigation.navigate("Register")}
      />
    </View>
  );
}
