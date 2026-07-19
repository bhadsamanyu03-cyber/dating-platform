import { memo } from "react";
import { StyleSheet, Text, View } from "react-native";
import { IconSet, colors, iconNames, spacing, typography } from "../theme";
import { SecondaryButton } from "./SecondaryButton";

export type ErrorStateProps = {
  title?: string;
  description?: string;
  retryLabel?: string;
  onRetry?: () => void;
};

function ErrorStateBase({
  title = "Something went wrong",
  description = "Please try again.",
  retryLabel = "Retry",
  onRetry,
}: ErrorStateProps) {
  return (
    <View style={styles.container}>
      <IconSet name={iconNames.error} size={40} color={colors.error} />
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.description}>{description}</Text>
      {onRetry ? (
        <View style={styles.action}>
          <SecondaryButton label={retryLabel} onPress={onRetry} />
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

export const ErrorState = memo(ErrorStateBase);
