import { useState } from "react";
import { Button, Text, TextInput, View } from "react-native";
import { colors } from "../../theme";
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
      navigation.navigate("Login");
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Unable to create account",
      );
    } finally {
      setLoading(false);
    }
  };
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12, backgroundColor: colors.background }}>
      <Text style={{ color: colors.text.primary, fontSize: 28, fontWeight: "700" }}>Create account</Text>
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
        title={loading ? "Creating..." : "Create account"}
        onPress={submit}
        disabled={loading}
      />
      <Text style={{ color: colors.text.secondary }}>
        Your account is ready right away. Use the same email and password to sign in.
      </Text>
      <Button
        title="Back to sign in"
        onPress={() => navigation.navigate("Login")}
      />
    </View>
  );
}
