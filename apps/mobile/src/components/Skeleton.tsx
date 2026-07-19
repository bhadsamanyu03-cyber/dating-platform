import { memo, useEffect, useRef } from "react";
import { Animated, StyleProp, StyleSheet, View, ViewStyle } from "react-native";
import { colors, radii } from "../theme";

export type SkeletonProps = {
  width?: number | `${number}%`;
  height?: number;
  borderRadius?: number;
  style?: StyleProp<ViewStyle>;
};

function SkeletonBase({
  width = "100%",
  height = 16,
  borderRadius = radii.sm,
  style,
}: SkeletonProps) {
  const opacity = useRef(new Animated.Value(0.5)).current;

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 1,
          duration: 700,
          useNativeDriver: true,
        }),
        Animated.timing(opacity, {
          toValue: 0.5,
          duration: 700,
          useNativeDriver: true,
        }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [opacity]);

  return (
    <Animated.View
      style={[
        { width, height, borderRadius, backgroundColor: colors.skeleton, opacity },
        style,
      ]}
    />
  );
}

export const Skeleton = memo(SkeletonBase);

/** Convenience skeleton matching ProfileCard's shape. */
export const ProfileCardSkeleton = memo(function ProfileCardSkeleton() {
  return (
    <View style={styles.cardSkeleton}>
      <Skeleton height={220} borderRadius={radii.lg} />
      <Skeleton width="60%" height={16} style={styles.gap} />
      <Skeleton width="40%" height={12} style={styles.gap} />
    </View>
  );
});

/** Convenience skeleton matching MessageBubble list rows. */
export const MessageRowSkeleton = memo(function MessageRowSkeleton() {
  return (
    <View style={styles.row}>
      <Skeleton width={36} height={36} borderRadius={18} />
      <View style={styles.rowText}>
        <Skeleton width="70%" height={12} />
        <Skeleton width="40%" height={12} style={styles.gap} />
      </View>
    </View>
  );
});

const styles = StyleSheet.create({
  cardSkeleton: {
    gap: 8,
  },
  gap: {
    marginTop: 4,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    paddingVertical: 8,
  },
  rowText: {
    flex: 1,
    gap: 4,
  },
});
