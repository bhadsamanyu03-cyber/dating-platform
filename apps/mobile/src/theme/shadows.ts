import { Platform } from "react-native";

/**
 * Soft, low-contrast shadows tuned for a dark background.
 * Android uses `elevation`; iOS uses shadow* props.
 */
function shadow(elevation: number, opacity: number, radius: number) {
  return Platform.select({
    ios: {
      shadowColor: "#000000",
      shadowOpacity: opacity,
      shadowRadius: radius,
      shadowOffset: { width: 0, height: Math.round(radius / 2) },
    },
    android: { elevation },
    default: {},
  });
}

export const shadows = {
  none: {},
  sm: shadow(2, 0.18, 6),
  md: shadow(6, 0.22, 12),
  lg: shadow(12, 0.28, 20),
} as const;
