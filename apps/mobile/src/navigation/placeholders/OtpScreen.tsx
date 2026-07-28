import { useState } from "react";
import { Button, Text, TextInput, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { verifyEmail } from "../../authApi";
import type { AuthStackParamList } from "../AuthNavigator";
type Props = NativeStackScreenProps<AuthStackParamList, "Otp">;
export function OtpScreen({ navigation, route }: Props) {
  const [token, setToken] = useState("");
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);
  const submit = async () => {
    setLoading(true);
    setError(undefined);
    try {
      await verifyEmail(token);
      navigation.navigate("Login");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Verification failed");
    } finally {
      setLoading(false);
    }
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
      <Button
        title={loading ? "Verifying..." : "Verify email"}
        disabled={loading}
        onPress={submit}
      />
    </View>
  );
}
