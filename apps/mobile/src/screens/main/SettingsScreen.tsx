import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Modal,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from "react-native";
import { Picker } from "@react-native-picker/picker";
import { deleteAccount } from "../../authApi";
import {
  DiscoveryPreferences,
  getPreferences,
  savePreferences,
} from "../../profileApi";
import { PasswordChangeScreen } from "./PasswordChangeScreen";

type Props = {
  accessToken: string;
  onLogout: () => void;
};

const defaultPreferences: Omit<
  DiscoveryPreferences,
  "created_at" | "updated_at"
> = {
  preferred_gender: "All",
  minimum_age: 18,
  maximum_age: 120,
  maximum_distance_km: 100,
  show_verified_only: false,
  show_only_with_photos: false,
};

export function SettingsScreen({ accessToken, onLogout }: Props) {
  const [preferences, setPreferences] = useState(defaultPreferences);
  const [savingPreferences, setSavingPreferences] = useState(false);
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [showDeleteAccount, setShowDeleteAccount] = useState(false);
  const [deletePassword, setDeletePassword] = useState("");
  const [error, setError] = useState<string>();

  useEffect(() => {
    getPreferences(accessToken)
      .then((value) =>
        setPreferences({
          preferred_gender: value.preferred_gender,
          minimum_age: value.minimum_age,
          maximum_age: value.maximum_age,
          maximum_distance_km: value.maximum_distance_km,
          show_verified_only: value.show_verified_only,
          show_only_with_photos: value.show_only_with_photos,
        }),
      )
      .catch((cause) =>
        setError(
          cause instanceof Error ? cause.message : "Unable to load preferences",
        ),
      );
  }, [accessToken]);

  const updatePreference = (
    key: keyof typeof defaultPreferences,
    value: string | number | boolean,
  ) => {
    setPreferences((current) => ({ ...current, [key]: value }));
  };

  const submitPreferences = async () => {
    setSavingPreferences(true);
    setError(undefined);
    try {
      const saved = await savePreferences(accessToken, preferences);
      setPreferences({
        preferred_gender: saved.preferred_gender,
        minimum_age: saved.minimum_age,
        maximum_age: saved.maximum_age,
        maximum_distance_km: saved.maximum_distance_km,
        show_verified_only: saved.show_verified_only,
        show_only_with_photos: saved.show_only_with_photos,
      });
      Alert.alert("Saved", "Discovery preferences updated.");
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Unable to save preferences",
      );
    } finally {
      setSavingPreferences(false);
    }
  };

  const submitDeleteAccount = async () => {
    try {
      await deleteAccount(accessToken, deletePassword);
      setShowDeleteAccount(false);
      await onLogout();
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Unable to delete account",
      );
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Settings</Text>
      {error && <Text style={styles.error}>{error}</Text>}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        <Button
          title="Change password"
          onPress={() => setShowPasswordChange(true)}
        />
        <Button title="Sign out" onPress={onLogout} />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Discovery preferences</Text>
        <Text>Preferred gender</Text>
        <Picker
          selectedValue={preferences.preferred_gender}
          onValueChange={(value) => updatePreference("preferred_gender", value)}
        >
          <Picker.Item label="Everyone" value="All" />
          <Picker.Item label="Women" value="Woman" />
          <Picker.Item label="Men" value="Man" />
          <Picker.Item label="Non-binary" value="Non-binary" />
          <Picker.Item label="Other" value="Other" />
          <Picker.Item label="Prefer not to say" value="Prefer not to say" />
        </Picker>
        <PreferenceNumber
          label="Minimum age"
          value={preferences.minimum_age}
          onChange={(value) => updatePreference("minimum_age", value)}
        />
        <PreferenceNumber
          label="Maximum age"
          value={preferences.maximum_age}
          onChange={(value) => updatePreference("maximum_age", value)}
        />
        <PreferenceNumber
          label="Maximum distance in km"
          value={preferences.maximum_distance_km}
          onChange={(value) => updatePreference("maximum_distance_km", value)}
        />
        <PreferenceSwitch
          label="Verified profiles only"
          value={preferences.show_verified_only}
          onValueChange={(value) =>
            updatePreference("show_verified_only", value)
          }
        />
        <PreferenceSwitch
          label="Profiles with photos only"
          value={preferences.show_only_with_photos}
          onValueChange={(value) =>
            updatePreference("show_only_with_photos", value)
          }
        />
        <Button
          title={savingPreferences ? "Saving..." : "Save preferences"}
          disabled={savingPreferences}
          onPress={submitPreferences}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Danger zone</Text>
        <Button
          title="Delete account"
          color="#b00020"
          onPress={() => setShowDeleteAccount(true)}
        />
      </View>

      <Modal visible={showPasswordChange} animationType="slide">
        <View style={styles.modalHeader}>
          <Button title="Close" onPress={() => setShowPasswordChange(false)} />
        </View>
        <PasswordChangeScreen
          accessToken={accessToken}
          onCancel={() => setShowPasswordChange(false)}
          onSuccess={() => setShowPasswordChange(false)}
        />
      </Modal>

      <Modal visible={showDeleteAccount} animationType="slide">
        <View style={styles.modalContent}>
          <Text style={styles.title}>Delete account</Text>
          <Text>Enter your password to permanently delete your account.</Text>
          <TextInput
            value={deletePassword}
            onChangeText={setDeletePassword}
            secureTextEntry
            placeholder="Password"
            style={styles.input}
          />
          <Button title="Cancel" onPress={() => setShowDeleteAccount(false)} />
          <Button
            title="Delete account"
            color="#b00020"
            disabled={!deletePassword}
            onPress={submitDeleteAccount}
          />
        </View>
      </Modal>
    </ScrollView>
  );
}

function PreferenceNumber(props: {
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <View>
      <Text>{props.label}</Text>
      <TextInput
        value={String(props.value)}
        onChangeText={(value) => props.onChange(Number(value) || 0)}
        keyboardType="number-pad"
        style={styles.input}
      />
    </View>
  );
}

function PreferenceSwitch(props: {
  label: string;
  value: boolean;
  onValueChange: (value: boolean) => void;
}) {
  return (
    <View style={styles.switchRow}>
      <Text>{props.label}</Text>
      <Switch value={props.value} onValueChange={props.onValueChange} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 20 },
  section: { gap: 12 },
  sectionTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#666",
    textTransform: "uppercase",
  },
  title: { fontSize: 24, fontWeight: "700", color: "#000" },
  error: { color: "#b00020" },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 10,
  },
  switchRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  modalHeader: { paddingHorizontal: 12, paddingVertical: 8 },
  modalContent: { padding: 20, gap: 16 },
});
