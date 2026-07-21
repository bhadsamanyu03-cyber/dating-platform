import { Pressable, StyleSheet, Text, View } from "react-native";
import { Avatar } from "../../components";
import { colors, iconNames, IconSet, spacing, typography } from "../../theme";

export function RecentConversationRow({
  name,
  onPress,
  showDivider,
}: {
  name: string;
  onPress: () => void;
  showDivider: boolean;
}) {
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      style={[styles.row, showDivider && styles.divider]}
    >
      <Avatar name={name} size={40} />
      <Text style={styles.name} numberOfLines={1}>
        {name}
      </Text>
      <IconSet
        name={iconNames.back}
        size={18}
        color={colors.text.muted}
        style={styles.chevron}
      />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    minHeight: 44,
  },
  divider: {
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  name: {
    flex: 1,
    color: colors.text.primary,
    fontSize: typography.size.base,
    fontWeight: typography.weight.medium,
  },
  chevron: {
    transform: [{ rotate: "180deg" }],
  },
});
