import { memo } from "react";
import { StyleSheet, TextInput, View } from "react-native";
import {
  colors,
  iconNames,
  IconSet,
  radii,
  spacing,
  typography,
} from "../theme";

export type SearchBarProps = {
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  onSubmit?: () => void;
};

function SearchBarBase({
  value,
  onChangeText,
  placeholder = "Search",
  onSubmit,
}: SearchBarProps) {
  return (
    <View style={styles.container}>
      <IconSet
        name={iconNames.search}
        size={18}
        color={colors.text.muted}
        style={styles.icon}
      />
      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={colors.text.muted}
        style={styles.input}
        returnKeyType="search"
        onSubmitEditing={onSubmit}
        autoCapitalize="none"
        accessibilityLabel={placeholder}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    minHeight: 48,
    borderRadius: radii.pill,
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    gap: spacing.xs,
  },
  icon: {
    marginRight: spacing.xxs,
  },
  input: {
    flex: 1,
    color: colors.text.primary,
    fontSize: typography.size.base,
  },
});

export const SearchBar = memo(SearchBarBase);
