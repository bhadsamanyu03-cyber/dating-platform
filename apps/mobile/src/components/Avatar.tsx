import { memo } from "react";
import { Image, StyleSheet, Text, View } from "react-native";
import { colors, typography } from "../theme";

export type AvatarProps = {
  uri?: string;
  name?: string;
  size?: number;
  online?: boolean;
};

function initialsFor(name?: string) {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/).slice(0, 2);
  return parts.map((p) => p[0]?.toUpperCase() ?? "").join("");
}

function AvatarBase({ uri, name, size = 44, online }: AvatarProps) {
  const dimension = { width: size, height: size, borderRadius: size / 2 };

  return (
    <View style={[styles.container, dimension]}>
      {uri ? (
        <Image
          source={{ uri }}
          style={[styles.image, dimension]}
          accessibilityLabel={name ? `${name}'s avatar` : "Avatar"}
        />
      ) : (
        <View style={[styles.fallback, dimension]}>
          <Text style={[styles.initials, { fontSize: size * 0.38 }]}>
            {initialsFor(name)}
          </Text>
        </View>
      )}
      {online ? (
        <View
          style={[
            styles.onlineDot,
            {
              width: size * 0.26,
              height: size * 0.26,
              borderRadius: size * 0.13,
            },
          ]}
        />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "relative",
  },
  image: {
    backgroundColor: colors.card,
  },
  fallback: {
    backgroundColor: colors.cardElevated,
    alignItems: "center",
    justifyContent: "center",
  },
  initials: {
    color: colors.text.secondary,
    fontWeight: typography.weight.semibold,
  },
  onlineDot: {
    position: "absolute",
    right: 0,
    bottom: 0,
    backgroundColor: colors.success,
    borderWidth: 2,
    borderColor: colors.background,
  },
});

export const Avatar = memo(AvatarBase);
