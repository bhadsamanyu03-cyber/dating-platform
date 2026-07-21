import { useState } from "react";
import { Button, Text, TextInput, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { AuthStackParamList } from "../AuthNavigator";
const api = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8080/api/v1";
type Props = NativeStackScreenProps<AuthStackParamList, "Register">;
export function RegisterScreen({ navigation }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string>();
  const submit = async () => {
    setError(undefined);
    const response = await fetch(`${api}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok)
      return setError(body.detail ?? "Unable to create account");
    navigation.navigate("Otp", { email });
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
      <Button title="Create account" onPress={submit} />
      <Button
        title="Back to sign in"
        onPress={() => navigation.navigate("Login")}
      />
    </View>
  );
}
