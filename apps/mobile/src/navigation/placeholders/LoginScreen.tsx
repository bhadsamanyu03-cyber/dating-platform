import { useState } from "react";
import { Button, Text, TextInput, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useAuthSession } from "../../AuthSession";
import { login } from "../../authApi";
import type { AuthStackParamList } from "../AuthNavigator";

type Props = NativeStackScreenProps<AuthStackParamList, "Login">;

export function LoginScreen({ navigation }: Props) {
  const { signIn } = useAuthSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);
  const submit = async () => {
    setError(undefined);
    setLoading(true);
    try {
      const body = await login(email, password);
      await signIn({
        accessToken: body.access_token,
        refreshToken: body.refresh_token,
      });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to sign in");
    } finally {
      setLoading(false);
    }
  };
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text>Welcome back</Text>
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
        title={loading ? "Signing in..." : "Sign in"}
        onPress={submit}
        disabled={loading}
      />
      <Button
        title="Create account"
        onPress={() => navigation.navigate("Register")}
      />
    </View>
  );
}
