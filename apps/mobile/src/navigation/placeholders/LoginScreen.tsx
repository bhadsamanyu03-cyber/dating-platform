import { useState } from "react";
import { Button, Text, TextInput, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useAuthSession } from "../../AuthSession";
import { login } from "../../authApi";
import { colors } from "../../theme";
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
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12, backgroundColor: colors.background }}>
      <Text style={{ color: colors.text.primary, fontSize: 28, fontWeight: "700" }}>Welcome back</Text>
      {error && <Text style={{ color: colors.error }}>{error}</Text>}
      <TextInput
        placeholder="Email"
        autoCapitalize="none"
        value={email}
        onChangeText={setEmail}
        placeholderTextColor={colors.text.muted}
        style={{ color: colors.text.primary, borderWidth: 1, borderColor: colors.border, borderRadius: 10, padding: 14 }}
      />
      <TextInput
        placeholder="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        placeholderTextColor={colors.text.muted}
        style={{ color: colors.text.primary, borderWidth: 1, borderColor: colors.border, borderRadius: 10, padding: 14 }}
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
