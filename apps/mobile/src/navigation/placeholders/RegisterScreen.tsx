import { useState } from "react";
import { Button, Text, TextInput, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { register } from "../../authApi";
import type { AuthStackParamList } from "../AuthNavigator";
type Props = NativeStackScreenProps<AuthStackParamList, "Register">;
export function RegisterScreen({ navigation }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);
  const submit = async () => {
    setError(undefined);
    setLoading(true);
    try {
      await register(email, password);
      navigation.navigate("Otp", { email });
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Unable to create account",
      );
    } finally {
      setLoading(false);
    }
  };
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text>Create account</Text>
      {error && <Text>{error}</Text>}
      <TextInput
        placeholder="Email"
        autoCapitalize="none"
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        placeholder="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      <Button
        title={loading ? "Creating..." : "Create account"}
        onPress={submit}
        disabled={loading}
      />
      <Button
        title="Back to sign in"
        onPress={() => navigation.navigate("Login")}
      />
    </View>
  );
}
