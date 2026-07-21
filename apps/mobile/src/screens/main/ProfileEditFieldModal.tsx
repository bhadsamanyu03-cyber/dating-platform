import { useState } from "react";
import {
  Button,
  Modal,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { Picker } from "@react-native-picker/picker";

type FieldType = "text" | "textarea" | "number" | "select";

export type EditFieldModalProps = {
  visible: boolean;
  title: string;
  fieldType: FieldType;
  value: string;
  options?: { label: string; value: string }[];
  placeholder?: string;
  helpText?: string;
  minLength?: number;
  maxLength?: number;
  onSave: (value: string) => void;
  onCancel: () => void;
  onClose: () => void;
};

export function ProfileEditFieldModal({
  visible,
  title,
  fieldType,
  value,
  options,
  placeholder,
  helpText,
  minLength,
  maxLength,
  onSave,
  onCancel,
  onClose,
}: EditFieldModalProps) {
  const [editValue, setEditValue] = useState(value);
  const [error, setError] = useState<string>();
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setError(undefined);

    // Validation
    if (fieldType !== "select" && !editValue.trim()) {
      setError("This field cannot be empty");
      return;
    }

    if (minLength && editValue.length < minLength) {
      setError(`Minimum ${minLength} characters required`);
      return;
    }

    if (maxLength && editValue.length > maxLength) {
      setError(`Maximum ${maxLength} characters allowed`);
      return;
    }

    setSaving(true);
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));
      onSave(editValue);
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditValue(value);
    setError(undefined);
    onCancel();
    onClose();
  };

  return (
    <Modal
      visible={visible}
      onRequestClose={handleCancel}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Button title="Cancel" onPress={handleCancel} />
          <Text style={styles.title}>{title}</Text>
          <View style={styles.placeholder} />
        </View>

        <View style={styles.content}>
          {helpText && <Text style={styles.helpText}>{helpText}</Text>}

          {fieldType === "text" && (
            <TextInput
              style={styles.input}
              placeholder={placeholder}
              value={editValue}
              onChangeText={setEditValue}
              maxLength={maxLength}
              editable={!saving}
            />
          )}

          {fieldType === "textarea" && (
            <TextInput
              style={[styles.input, styles.textareaInput]}
              placeholder={placeholder}
              value={editValue}
              onChangeText={setEditValue}
              maxLength={maxLength}
              multiline
              numberOfLines={5}
              editable={!saving}
              textAlignVertical="top"
            />
          )}

          {fieldType === "number" && (
            <TextInput
              style={styles.input}
              placeholder={placeholder}
              value={editValue}
              onChangeText={setEditValue}
              keyboardType="number-pad"
              maxLength={maxLength}
              editable={!saving}
            />
          )}

          {fieldType === "select" && options && (
            <View style={styles.pickerContainer}>
              <Picker
                selectedValue={editValue}
                onValueChange={setEditValue}
                enabled={!saving}
              >
                {options.map((opt) => (
                  <Picker.Item
                    key={opt.value}
                    label={opt.label}
                    value={opt.value}
                  />
                ))}
              </Picker>
            </View>
          )}

          {maxLength && fieldType !== "select" && (
            <Text style={styles.charCount}>
              {editValue.length} / {maxLength}
            </Text>
          )}

          {error && <Text style={styles.error}>{error}</Text>}

          <View style={styles.actions}>
            <Button
              title={saving ? "Saving…" : "Save"}
              onPress={handleSave}
              disabled={saving || editValue === value}
            />
            <Button
              title="Cancel"
              onPress={handleCancel}
              color="#666"
              disabled={saving}
            />
          </View>
        </View>
      </ScrollView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: { paddingBottom: 32 },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  title: {
    fontSize: 16,
    fontWeight: "700",
    color: "#000",
  },
  placeholder: { width: 50 },
  content: {
    padding: 20,
    gap: 16,
  },
  helpText: {
    fontSize: 13,
    color: "#666",
    lineHeight: 18,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    color: "#000",
  },
  textareaInput: {
    minHeight: 120,
    paddingTop: 12,
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    overflow: "hidden",
  },
  charCount: {
    fontSize: 12,
    color: "#999",
    textAlign: "right",
  },
  error: {
    color: "#b00020",
    fontSize: 13,
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: "#ffebee",
    borderRadius: 6,
  },
  actions: {
    gap: 10,
    marginTop: 8,
  },
});
