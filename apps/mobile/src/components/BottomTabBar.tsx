import { memo } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import {
  colors,
  iconNames,
  IconName,
  IconSet,
  spacing,
  typography,
} from "../theme";

export type BottomTabItem = {
  key: string;
  label: string;
  icon: Extract<
    IconName,
    "home" | "discover" | "feed" | "messages" | "profile"
  >;
  activeIcon: Extract<
    IconName,
    | "homeActive"
    | "discoverActive"
    | "feedActive"
    | "messagesActive"
    | "profileActive"
  >;
  badgeCount?: number;
};

export type BottomTabBarProps = {
  items: BottomTabItem[];
  activeKey: string;
  onSelect: (key: string) => void;
};

function BottomTabBarBase({ items, activeKey, onSelect }: BottomTabBarProps) {
  const insets = useSafeAreaInsets();

  return (
    <View
      style={[
        styles.container,
        { paddingBottom: Math.max(insets.bottom, spacing.xs) },
      ]}
    >
      {items.map((item) => {
        const active = item.key === activeKey;
        return (
          <Pressable
            key={item.key}
            onPress={() => onSelect(item.key)}
            accessibilityRole="tab"
            accessibilityState={{ selected: active }}
            accessibilityLabel={item.label}
            hitSlop={8}
            style={styles.tab}
          >
            <View>
              <IconSet
                name={iconNames[active ? item.activeIcon : item.icon]}
                size={24}
                color={active ? colors.primary : colors.text.muted}
              />
              {item.badgeCount ? (
                <View style={styles.badge}>
                  <Text style={styles.badgeText}>
                    {item.badgeCount > 9 ? "9+" : item.badgeCount}
                  </Text>
                </View>
              ) : null}
            </View>
            <Text style={[styles.label, active && styles.labelActive]}>
              {item.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    backgroundColor: colors.card,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.xs,
  },
  tab: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 2,
    minHeight: 44,
  },
  label: {
    fontSize: typography.size.xs,
    color: colors.text.muted,
  },
  labelActive: {
    color: colors.primary,
    fontWeight: typography.weight.semibold,
  },
  badge: {
    position: "absolute",
    top: -4,
    right: -8,
    minWidth: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: colors.error,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 3,
  },
  badgeText: {
    color: colors.text.primary,
    fontSize: 10,
    fontWeight: typography.weight.bold,
  },
});

export const BottomTabBar = memo(BottomTabBarBase);
