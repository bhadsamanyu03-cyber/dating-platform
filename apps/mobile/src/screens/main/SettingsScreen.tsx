import { useState } from "react";
import {
  Alert,
  Button,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { PasswordChangeScreen } from "./PasswordChangeScreen";

type Props = {
  accessToken: string;
  onLogout: () => void;
};

export function SettingsScreen({ accessToken, onLogout }: Props) {
  const [actionInProgress, setActionInProgress] = useState(false);
  const [showPasswordChange, setShowPasswordChange] = useState(false);

  const handleLogout = () => {
    Alert.alert("Sign out", "Are you sure you want to sign out?", [
      { text: "Cancel", onPress: () => {}, style: "cancel" },
      {
        text: "Sign out",
        onPress: () => {
          setActionInProgress(true);
          // In a real app, you would call a logout API and clear tokens
          // For now, just call the callback to clear the app state
          onLogout();
        },
        style: "destructive",
      },
    ]);
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      "Delete Account",
      "This action cannot be undone. All your data will be permanently deleted.",
      [
        { text: "Cancel", onPress: () => {}, style: "cancel" },
        {
          text: "Delete",
          onPress: () => {
            Alert.alert(
              "Confirm",
              "Type DELETE to confirm account deletion.",
              [
                {
                  text: "Cancel",
                  onPress: () => {},
                  style: "cancel",
                },
                {
                  text: "Confirm",
                  onPress: async () => {
                    setActionInProgress(true);
                    try {
                      // TODO: Call DELETE /api/v1/auth/account endpoint
                      // For now, just logout
                      onLogout();
                    } catch (e) {
                      Alert.alert(
                        "Error",
                        e instanceof Error ? e.message : "Unable to delete account"
                      );
                    } finally {
                      setActionInProgress(false);
                    }
                  },
                  style: "destructive",
                },
              ]
            );
          },
          style: "destructive",
        },
      ]
    );
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        <SettingItem
          label="Email & Password"
          description="Manage your login credentials"
          onPress={() => setShowPasswordChange(true)}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Privacy & Safety</Text>
        <SettingItem
          label="Who can see my profile"
          description="Public or matches only"
          onPress={() =>
            Alert.alert("Coming soon", "Privacy settings are not yet available")
          }
        />
        <SettingItem
          label="Blocked users"
          description="View and manage blocked accounts"
          onPress={() =>
            Alert.alert(
              "Coming soon",
              "Blocking functionality is not yet available"
            )
          }
        />
        <SettingItem
          label="Report abuse"
          description="Report inappropriate behavior"
          onPress={() =>
            Alert.alert("Coming soon", "Reporting is not yet available")
          }
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notifications</Text>
        <SettingItem
          label="Push notifications"
          description="Receive alerts for matches and messages"
          onPress={() =>
            Alert.alert(
              "Coming soon",
              "Notification settings are not yet available"
            )
          }
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <SettingItem
          label="App version"
          description="0.1.0"
          disabled
        />
        <SettingItem
          label="Terms of Service"
          description="View our terms"
          onPress={() =>
            Alert.alert(
              "Coming soon",
              "Terms of Service link not yet available"
            )
          }
        />
        <SettingItem
          label="Privacy Policy"
          description="View our privacy policy"
          onPress={() =>
            Alert.alert(
              "Coming soon",
              "Privacy Policy link not yet available"
            )
          }
        />
      </View>

      <View style={styles.section}>
        <View style={styles.dangerZone}>
          <Button
            title={actionInProgress ? "Signing out…" : "Sign out"}
            disabled={actionInProgress}
            onPress={handleLogout}
            color="#1976d2"
          />
          <Button
            title="Delete Account"
            disabled={actionInProgress}
            onPress={handleDeleteAccount}
            color="#b00020"
          />
        </View>
      </View>

      <Text style={styles.footer}>
        Need help? Contact support@dating-platform.local
      </Text>
      <Modal
        visible={showPasswordChange}
        onRequestClose={() => setShowPasswordChange(false)}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <View style={styles.modalHeader}>
          <Button
            title="Close"
            onPress={() => setShowPasswordChange(false)}
          />
        </View>
        <PasswordChangeScreen
          accessToken={accessToken}
          onCancel={() => setShowPasswordChange(false)}
          onSuccess={() => {
            setShowPasswordChange(false);
            Alert.alert(
              "Password Changed",
              "Your password has been successfully updated."
            );
          }}
        />
      </Modal>
    </ScrollView>
  );
}

function SettingItem(props: {
  label: string;
  description: string;
  onPress?: () => void;
  disabled?: boolean;
}) {
  return (
    <Pressable
      style={({ pressed }) => [
        styles.settingItem,
        pressed && !props.disabled && styles.settingItemPressed,
      ]}
      onPress={props.onPress}
      disabled={props.disabled}
    >
      <View style={styles.settingContent}>
        <Text style={styles.settingLabel}>{props.label}</Text>
        <Text style={styles.settingDescription}>{props.description}</Text>
      </View>
      {!props.disabled && <Text style={styles.settingArrow}>›</Text>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: { paddingVertical: 12 },
  section: { marginBottom: 16 },
  sectionTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#666",
    textTransform: "uppercase",
    marginHorizontal: 16,
    marginBottom: 8,
    letterSpacing: 0.5,
  },
  settingItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  settingItemPressed: {
    backgroundColor: "#f5f5f5",
  },
  settingContent: { flex: 1, gap: 4 },
  settingLabel: { fontSize: 16, fontWeight: "600", color: "#000" },
  settingDescription: { fontSize: 13, color: "#999" },
  settingArrow: { fontSize: 20, color: "#ccc", marginLeft: 8 },
  dangerZone: {
    paddingHorizontal: 16,
    gap: 8,
    paddingTop: 8,
  },
  footer: {
    textAlign: "center",
    fontSize: 12,
    color: "#999",
    marginTop: 24,
    marginBottom: 24,
  },
  modalHeader: { paddingHorizontal: 12, paddingVertical: 8 },
});
