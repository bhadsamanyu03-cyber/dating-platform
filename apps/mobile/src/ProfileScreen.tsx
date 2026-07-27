import DateTimePicker from "@react-native-community/datetimepicker";
import { Picker } from "@react-native-picker/picker";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Button,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import {
  checkUsername,
  getInterests,
  getMyProfile,
  getProfile,
  Interest,
  Profile,
  saveProfile,
} from "./profileApi";
import { ProfilePhotosScreen } from "./screens/main/ProfilePhotosScreen";

type Props = { accessToken: string; usernameToView?: string };
type Draft = {
  username: string;
  display_name: string;
  bio: string;
  gender: string;
  pronouns: string;
  date_of_birth: string;
  height_cm: string;
  interest_ids: string[];
};
const empty: Draft = {
  username: "",
  display_name: "",
  bio: "",
  gender: "",
  pronouns: "",
  date_of_birth: "",
  height_cm: "",
  interest_ids: [],
};
const genderOptions = [
  "Woman",
  "Man",
  "Non-binary",
  "Other",
  "Prefer not to say",
];
export function ProfileScreen({ accessToken, usernameToView }: Props) {
  const [draft, setDraft] = useState<Draft>(empty);
  const [originalUsername, setOriginalUsername] = useState("");
  const [interests, setInterests] = useState<Interest[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>();
  const [completion, setCompletion] = useState(0);
  const [publicProfile, setPublicProfile] = useState<Profile>();
  const [showDobPicker, setShowDobPicker] = useState(false);
  useEffect(() => {
    const load = usernameToView
      ? getProfile(usernameToView, accessToken).then(setPublicProfile)
      : Promise.all([
          getMyProfile(accessToken).catch(() => null),
          getInterests(accessToken),
        ]).then(([profile, catalog]) => {
          setInterests(catalog);
          if (profile) {
            setOriginalUsername(profile.username);
            setCompletion(profile.profile_completion_percentage);
            setDraft({
              username: profile.username,
              display_name: profile.display_name,
              bio: profile.bio,
              gender: profile.gender,
              pronouns: profile.pronouns ?? "",
              date_of_birth: profile.date_of_birth,
              height_cm: profile.height_cm?.toString() ?? "",
              interest_ids: profile.interests.map((i) => i.id),
            });
          }
        });
    load
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [accessToken, usernameToView]);
  const set = (key: keyof Draft, value: string | string[]) =>
    setDraft((current) => ({ ...current, [key]: value }));
  const submit = async () => {
    setError(undefined);
    if (!/^[A-Za-z0-9_]{3,30}$/.test(draft.username))
      return setError(
        "Username must be 3–30 letters, numbers, or underscores.",
      );
    if (!draft.display_name || !draft.gender || !draft.date_of_birth)
      return setError("Display name, gender, and date of birth are required.");
    setSaving(true);
    try {
      if (draft.username !== originalUsername) {
        const availability = await checkUsername(draft.username, accessToken);
        if (!availability.available) throw new Error("Username is unavailable");
      }
      const profile = await saveProfile(
        {
          ...draft,
          pronouns: draft.pronouns || null,
          height_cm: draft.height_cm ? Number(draft.height_cm) : null,
        },
        accessToken,
      );
      setOriginalUsername(profile.username);
      setCompletion(profile.profile_completion_percentage);
      Alert.alert("Saved", "Your profile has been updated.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to save profile");
    } finally {
      setSaving(false);
    }
  };
  if (loading)
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <Text>Loading profile…</Text>
      </View>
    );
  if (publicProfile)
    return (
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>{publicProfile.display_name}</Text>
        <Text>@{publicProfile.username}</Text>
        <Text>{publicProfile.bio}</Text>
        <Text>{publicProfile.gender}</Text>
        {publicProfile.pronouns && <Text>{publicProfile.pronouns}</Text>}
        {publicProfile.height_cm && <Text>{publicProfile.height_cm} cm</Text>}
        <Text>
          {publicProfile.interests
            .map((interest) => interest.name)
            .join(", ") || "No interests listed."}
        </Text>
      </ScrollView>
    );
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Your profile</Text>
      <Text>{completion}% complete</Text>
      {error && <Text style={styles.error}>{error}</Text>}
      <Field
        label="Username"
        value={draft.username}
        onChangeText={(value) => set("username", value)}
      />
      <Field
        label="Display name"
        value={draft.display_name}
        onChangeText={(value) => set("display_name", value)}
      />
      <Text>Bio ({draft.bio.length}/150)</Text>
      <TextInput
        style={styles.input}
        multiline
        maxLength={150}
        value={draft.bio}
        onChangeText={(value) => set("bio", value)}
      />
      <Text>Gender</Text>
      <Picker
        selectedValue={draft.gender}
        onValueChange={(value) => set("gender", value)}
      >
        <Picker.Item label="Select gender" value="" />
        {genderOptions.map((value) => (
          <Picker.Item key={value} label={value} value={value} />
        ))}
      </Picker>
      <Field
        label="Pronouns (optional)"
        value={draft.pronouns}
        onChangeText={(value) => set("pronouns", value)}
      />
      <Text>Date of birth</Text>
      <Button
        title={draft.date_of_birth || "Select date of birth"}
        onPress={() => setShowDobPicker(true)}
      />
      {showDobPicker && (
        <DateTimePicker
          value={
            draft.date_of_birth
              ? new Date(`${draft.date_of_birth}T12:00:00`)
              : new Date(2000, 0, 1)
          }
          maximumDate={new Date()}
          mode="date"
          onChange={(_, selected) => {
            setShowDobPicker(false);
            if (selected)
              set("date_of_birth", selected.toISOString().slice(0, 10));
          }}
        />
      )}
      <Field
        label="Height in cm (optional)"
        value={draft.height_cm}
        keyboardType="number-pad"
        onChangeText={(value) => set("height_cm", value)}
      />
      <Text style={styles.subtitle}>Interests</Text>
      {interests.length === 0 ? (
        <Text>No interests are available yet.</Text>
      ) : (
        interests.map((interest) => (
          <Pressable
            key={interest.id}
            onPress={() =>
              set(
                "interest_ids",
                draft.interest_ids.includes(interest.id)
                  ? draft.interest_ids.filter((id) => id !== interest.id)
                  : [...draft.interest_ids, interest.id],
              )
            }
          >
            <Text
              style={
                draft.interest_ids.includes(interest.id)
                  ? styles.selected
                  : styles.option
              }
            >
              {interest.name}
            </Text>
          </Pressable>
        ))
      )}
      <Button
        title={saving ? "Saving…" : "Save profile"}
        disabled={saving}
        onPress={submit}
      />
      {!usernameToView && (
        <View style={{ marginTop: 24 }}>
          <Text style={styles.subtitle}>Profile photos</Text>
          <ProfilePhotosScreen accessToken={accessToken} />
        </View>
      )}
    </ScrollView>
  );
}
function Field(props: {
  label: string;
  value: string;
  onChangeText: (value: string) => void;
  keyboardType?: "default" | "number-pad";
}) {
  return (
    <View>
      <Text>{props.label}</Text>
      <TextInput
        style={styles.input}
        value={props.value}
        keyboardType={props.keyboardType}
        onChangeText={props.onChangeText}
      />
    </View>
  );
}
const styles = StyleSheet.create({
  container: { padding: 20, gap: 10 },
  center: { flex: 1, alignItems: "center", justifyContent: "center", gap: 8 },
  title: { fontSize: 28, fontWeight: "700" },
  subtitle: { fontSize: 18, fontWeight: "600" },
  input: {
    borderWidth: 1,
    borderColor: "#777",
    borderRadius: 6,
    padding: 10,
    minHeight: 42,
  },
  error: { color: "#b00020" },
  option: { padding: 10 },
  selected: { padding: 10, backgroundColor: "#dceeff", fontWeight: "700" },
});
