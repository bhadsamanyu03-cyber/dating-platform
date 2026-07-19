/**
 * Corvinth typography scale.
 * Large, rounded, minimal — spacing over decoration.
 */
export const typography = {
  fontFamily: {
    regular: "System",
    medium: "System",
    semibold: "System",
    bold: "System",
  },
  size: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 22,
    xxl: 28,
    display: 34,
  },
  lineHeight: {
    xs: 16,
    sm: 20,
    base: 22,
    lg: 24,
    xl: 28,
    xxl: 34,
    display: 40,
  },
  weight: {
    regular: "400" as const,
    medium: "500" as const,
    semibold: "600" as const,
    bold: "700" as const,
  },
} as const;

export type Typography = typeof typography;
