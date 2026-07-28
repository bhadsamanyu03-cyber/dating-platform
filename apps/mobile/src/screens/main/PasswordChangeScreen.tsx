import { useState } from "react";
import {
  Alert,
  Button,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { changePassword } from "../../authApi";

type Props = {
  accessToken: string;
  onSuccess?: () => void;
  onCancel?: () => void;
};

export function PasswordChangeScreen({
  accessToken,
  onSuccess,
  onCancel,
}: Props) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const validatePasswords = (): boolean => {
    setError(undefined);

    if (!currentPassword) {
      setError("Current password is required");
      return false;
    }

    if (!newPassword) {
      setError("New password is required");
      return false;
    }

    if (newPassword.length < 12) {
      setError("Password must be at least 12 characters");
      return false;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return false;
    }

    if (newPassword === currentPassword) {
      setError("New password must be different from current password");
      return false;
    }

    return true;
  };

  const handleChangePassword = async () => {
    if (!validatePasswords()) {
      return;
    }

    setLoading(true);
    try {
      await changePassword(accessToken, currentPassword, newPassword);

      Alert.alert("Success", "Your password has been changed", [
        {
          text: "OK",
          onPress: () => {
            setCurrentPassword("");
            setNewPassword("");
            setConfirmPassword("");
            onSuccess?.();
          },
        },
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to change password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Change Password</Text>
      <Text style={styles.description}>
        For your security, please enter your current password and a new
        password.
      </Text>

      {error && <Text style={styles.error}>{error}</Text>}

      <View style={styles.section}>
        <Text style={styles.label}>Current Password</Text>
        <View style={styles.passwordInputContainer}>
          <TextInput
            style={styles.passwordInput}
            placeholder="Enter current password"
            secureTextEntry={!showCurrentPassword}
            value={currentPassword}
            onChangeText={setCurrentPassword}
            editable={!loading}
          />
          <Button
            title={showCurrentPassword ? "Hide" : "Show"}
            onPress={() => setShowCurrentPassword(!showCurrentPassword)}
            color="#666"
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>New Password</Text>
        <Text style={styles.hint}>At least 12 characters</Text>
        <View style={styles.passwordInputContainer}>
          <TextInput
            style={styles.passwordInput}
            placeholder="Enter new password"
            secureTextEntry={!showNewPassword}
            value={newPassword}
            onChangeText={setNewPassword}
            editable={!loading}
          />
          <Button
            title={showNewPassword ? "Hide" : "Show"}
            onPress={() => setShowNewPassword(!showNewPassword)}
            color="#666"
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Confirm Password</Text>
        <View style={styles.passwordInputContainer}>
          <TextInput
            style={styles.passwordInput}
            placeholder="Confirm new password"
            secureTextEntry={!showConfirmPassword}
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            editable={!loading}
          />
          <Button
            title={showConfirmPassword ? "Hide" : "Show"}
            onPress={() => setShowConfirmPassword(!showConfirmPassword)}
            color="#666"
          />
        </View>
      </View>

      <View style={styles.actions}>
        <Button
          title={loading ? "Changing…" : "Change Password"}
          onPress={handleChangePassword}
          disabled={loading}
          color="#1976d2"
        />
        {onCancel && (
          <Button
            title="Cancel"
            onPress={onCancel}
            color="#666"
            disabled={loading}
          />
        )}
      </View>

      <View style={styles.info}>
        <Text style={styles.infoTitle}>Password Requirements</Text>
        <Text style={styles.infoBullet}>• At least 12 characters long</Text>
        <Text style={styles.infoBullet}>
          • Must be different from your current password
        </Text>
        <Text style={styles.infoBullet}>
          • We recommend using a mix of uppercase, lowercase, numbers, and
          symbols
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, gap: 16 },
  title: { fontSize: 24, fontWeight: "700", color: "#000" },
  description: { fontSize: 14, color: "#666", lineHeight: 20 },
  error: {
    backgroundColor: "#ffebee",
    color: "#b00020",
    padding: 12,
    borderRadius: 6,
    fontSize: 14,
  },
  section: { gap: 8 },
  label: { fontSize: 14, fontWeight: "600", color: "#333" },
  hint: { fontSize: 12, color: "#999" },
  passwordInputContainer: {
    flexDirection: "row",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 6,
    paddingHorizontal: 12,
    backgroundColor: "#fff",
  },
  passwordInput: {
    flex: 1,
    paddingVertical: 12,
    fontSize: 14,
    color: "#000",
  },
  actions: { gap: 10, marginTop: 16 },
  info: {
    backgroundColor: "#f5f5f5",
    padding: 16,
    borderRadius: 6,
    gap: 8,
    marginTop: 16,
  },
  infoTitle: { fontSize: 14, fontWeight: "600", color: "#333" },
  infoBullet: { fontSize: 13, color: "#666", lineHeight: 18 },
});
