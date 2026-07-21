import { useState } from "react";
import { Button, Text, TextInput, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { AuthStackParamList } from "../AuthNavigator";
const api = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8080/api/v1";
type Props = NativeStackScreenProps<AuthStackParamList, "Otp">;
export function OtpScreen({ navigation, route }: Props) {
  const [token, setToken] = useState("");
  const [error, setError] = useState<string>();
  const submit = async () => {
    const response = await fetch(`${api}/auth/verify-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      return setError(body.detail ?? "Verification failed");
    }
    navigation.navigate("Login");
  };
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text>Verify {route.params.email}</Text>
      {error && <Text>{error}</Text>}
      <TextInput
        placeholder="Verification token"
        value={token}
        onChangeText={setToken}
      />
      <Button title="Verify email" onPress={submit} />
    </View>
  );
}
