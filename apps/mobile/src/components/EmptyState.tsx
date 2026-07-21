import { memo } from "react";
import { StyleSheet, Text, View } from "react-native";
import {
  IconSet,
  IconName,
  colors,
  iconNames,
  spacing,
  typography,
} from "../theme";
import { PrimaryButton } from "./PrimaryButton";

export type EmptyStateProps = {
  icon?: IconName;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
};

function EmptyStateBase({
  icon = "search",
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <View style={styles.container}>
      <IconSet name={iconNames[icon]} size={40} color={colors.text.muted} />
      <Text style={styles.title}>{title}</Text>
      {description ? (
        <Text style={styles.description}>{description}</Text>
      ) : null}
      {actionLabel && onAction ? (
        <View style={styles.action}>
          <PrimaryButton label={actionLabel} onPress={onAction} />
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: spacing.xxl,
    paddingHorizontal: spacing.lg,
    gap: spacing.xs,
  },
  title: {
    color: colors.text.primary,
    fontSize: typography.size.lg,
    fontWeight: typography.weight.semibold,
    textAlign: "center",
  },
  description: {
    color: colors.text.muted,
    fontSize: typography.size.sm,
    textAlign: "center",
  },
  action: {
    marginTop: spacing.sm,
    alignSelf: "stretch",
  },
});

export const EmptyState = memo(EmptyStateBase);
