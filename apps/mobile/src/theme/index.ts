import { colors } from "./colors";
import { typography } from "./typography";
import { spacing } from "./spacing";
import { radii } from "./radii";
import { shadows } from "./shadows";
import { animation } from "./animation";

export const theme = {
  colors,
  typography,
  spacing,
  radii,
  shadows,
  animation,
} as const;

export type Theme = typeof theme;

export { colors, typography, spacing, radii, shadows, animation };
export { iconNames, IconSet } from "./icons";
export type { IconName } from "./icons";

// A ThemeProvider/useTheme hook is intentionally kept trivial for now:
// dark mode is the only supported mode. This indirection exists so a
// future light theme can be added without touching every consumer.
export function useTheme(): Theme {
  return theme;
}
