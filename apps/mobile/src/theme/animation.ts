/**
 * Shared animation timing/spring constants.
 * Navigation transitions target ~300ms; interactive elements use springs.
 */
export const animation = {
  duration: {
    fast: 150,
    base: 300,
    slow: 450,
  },
  spring: {
    button: { damping: 14, stiffness: 220, mass: 0.6 },
    card: { damping: 16, stiffness: 180, mass: 0.8 },
  },
  easing: {
    standard: [0.4, 0.0, 0.2, 1] as const,
  },
} as const;
