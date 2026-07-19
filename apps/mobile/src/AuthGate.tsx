import { useState } from "react";
import { Button, Text, TextInput, View } from "react-native";
import { ProfileScreen } from "./ProfileScreen";
import { DiscoveryScreen } from "./DiscoveryScreen";
import { MatchesScreen } from "./MatchesScreen";
import { ConversationsScreen } from "./ConversationsScreen";
import { FeedScreen } from "./FeedScreen";
import { SearchScreen } from "./SearchScreen";
const api = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8080/api/v1";
export function AuthGate() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [verificationToken, setVerificationToken] = useState("");
  const [token, setToken] = useState<string>();
  const [screen, setScreen] = useState<
    "profile" | "discovery" | "matches" | "conversations" | "feed" | "search"
  >("profile");
  const [error, setError] = useState<string>();
  const submit = async (path: "login" | "register") => {
    setError(undefined);
    const response = await fetch(`${api}/auth/${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      return setError(body.detail ?? "Unable to continue");
    }
    if (path === "register")
      return setError(
        "Check your email, enter the verification token below, then sign in.",
      );
    const body = await response.json();
    setToken(body.access_token);
  };
  const verify = async () => {
    const response = await fetch(`${api}/auth/verify-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: verificationToken }),
    });
    setError(
      response.ok
        ? "Email verified. You can now sign in."
        : "Verification failed.",
    );
  };
  if (token)
    return (
      <View style={{ flex: 1 }}>
        <Button title="Profile" onPress={() => setScreen("profile")} />
        <Button title="Discover" onPress={() => setScreen("discovery")} />
        <Button title="Matches" onPress={() => setScreen("matches")} />
        <Button
          title="Conversations"
          onPress={() => setScreen("conversations")}
        />
        <Button title="Feed" onPress={() => setScreen("feed")} />
        <Button title="Search" onPress={() => setScreen("search")} />
        {screen === "profile" ? (
          <ProfileScreen accessToken={token} />
        ) : screen === "discovery" ? (
          <DiscoveryScreen accessToken={token} />
        ) : screen === "matches" ? (
          <MatchesScreen accessToken={token} />
        ) : screen === "conversations" ? (
          <ConversationsScreen accessToken={token} />
        ) : screen === "feed" ? (
          <FeedScreen />
        ) : (
          <SearchScreen accessToken={token} />
        )}
      </View>
    );
  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 10 }}>
      <Text>Sign in to manage your profile</Text>
      {error && <Text style={{ color: "#b00020" }}>{error}</Text>}
      <TextInput
        placeholder="Email"
        autoCapitalize="none"
        keyboardType="email-address"
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        placeholder="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      <Button title="Sign in" onPress={() => submit("login")} />
      <Button title="Create account" onPress={() => submit("register")} />
      <TextInput
        placeholder="Email verification token"
        value={verificationToken}
        onChangeText={setVerificationToken}
      />
      <Button title="Verify email" onPress={verify} />
    </View>
  );
}
