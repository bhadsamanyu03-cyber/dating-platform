import {
  DarkTheme,
  NavigationContainer,
  Theme,
} from "@react-navigation/native";
import { AuthNavigator } from "./AuthNavigator";
import { MainTabNavigator } from "./MainTabNavigator";
import { colors } from "../theme";
import { AuthSessionProvider, useAuthSession } from "../AuthSession";

const navigationTheme: Theme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    background: colors.background,
    card: colors.card,
    primary: colors.primary,
    text: colors.text.primary,
    border: colors.border,
    notification: colors.error,
  },
};

/**
 * Temporary local auth-state switch. Phase C wires navigation shape only —
 * real session state will replace this once the auth screens are built
 * against the existing backend contracts (see AuthGate.tsx for the
 * current working auth flow, left untouched).
 */
function NavigatorContent() {
  const { session } = useAuthSession();
  return (
    <NavigationContainer theme={navigationTheme}>
      {session ? <MainTabNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
}

export function RootNavigator() {
  return (
    <AuthSessionProvider>
      <NavigatorContent />
    </AuthSessionProvider>
  );
}
