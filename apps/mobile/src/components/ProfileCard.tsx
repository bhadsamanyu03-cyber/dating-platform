import { memo } from "react";
import { Image, StyleSheet, Text, View } from "react-native";
import {
  colors,
  iconNames,
  IconSet,
  radii,
  spacing,
  typography,
} from "../theme";
import { GlassCard } from "./GlassCard";
import { Chip } from "./Chip";

export type ProfileCardProps = {
  name: string;
  age?: number;
  photoUri?: string;
  distanceLabel?: string;
  interests?: string[];
  verified?: boolean;
  onPress?: () => void;
};

function ProfileCardBase({
  name,
  age,
  photoUri,
  distanceLabel,
  interests = [],
  verified,
  onPress,
}: ProfileCardProps) {
  return (
    <GlassCard onPress={onPress} padded={false} style={styles.card}>
      <View style={styles.photoWrap}>
        {photoUri ? (
          <Image source={{ uri: photoUri }} style={styles.photo} />
        ) : (
          <View style={[styles.photo, styles.photoFallback]} />
        )}
        {verified ? (
          <View style={styles.verifiedBadge}>
            <IconSet name={iconNames.check} size={14} color={colors.success} />
          </View>
        ) : null}
      </View>
      <View style={styles.info}>
        <Text style={styles.name} numberOfLines={1}>
          {name}
          {age ? `, ${age}` : ""}
        </Text>
        {distanceLabel ? (
          <Text style={styles.distance}>{distanceLabel}</Text>
        ) : null}
        {interests.length ? (
          <View style={styles.chips}>
            {interests.slice(0, 3).map((interest) => (
              <Chip key={interest} label={interest} />
            ))}
          </View>
        ) : null}
      </View>
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  card: {
    overflow: "hidden",
  },
  photoWrap: {
    position: "relative",
    aspectRatio: 3 / 4,
  },
  photo: {
    width: "100%",
    height: "100%",
  },
  photoFallback: {
    backgroundColor: colors.cardElevated,
  },
  verifiedBadge: {
    position: "absolute",
    top: spacing.xs,
    right: spacing.xs,
    backgroundColor: colors.overlay,
    borderRadius: radii.pill,
    padding: 4,
  },
  info: {
    padding: spacing.sm,
    gap: spacing.xxs,
  },
  name: {
    color: colors.text.primary,
    fontSize: typography.size.lg,
    fontWeight: typography.weight.semibold,
  },
  distance: {
    color: colors.text.muted,
    fontSize: typography.size.xs,
  },
  chips: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xxs,
    marginTop: spacing.xxs,
  },
});

export const ProfileCard = memo(ProfileCardBase);
