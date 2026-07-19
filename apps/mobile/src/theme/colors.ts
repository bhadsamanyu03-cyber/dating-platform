/**
 * Corvinth color tokens.
 * Dark mode is the primary (and currently only) design target.
 */
export const colors = {
  background: "#0B0F14",
  card: "#121821",
  cardElevated: "#171F2A",
  border: "rgba(255,255,255,0.08)",

  primary: "#4F8CFF",
  primaryMuted: "rgba(79,140,255,0.16)",
  accent: "#8B5CF6",
  accentMuted: "rgba(139,92,246,0.16)",

  success: "#34D399",
  warning: "#FBBF24",
  error: "#EF4444",

  text: {
    primary: "#FFFFFF",
    secondary: "rgba(255,255,255,0.70)",
    muted: "rgba(255,255,255,0.45)",
    inverse: "#0B0F14",
  },

  overlay: "rgba(0,0,0,0.55)",
  skeleton: "rgba(255,255,255,0.06)",
  skeletonHighlight: "rgba(255,255,255,0.12)",
} as const;

export type ThemeColors = typeof colors;
