import { useState } from "react";
import { DarkTheme, NavigationContainer, Theme } from "@react-navigation/native";
import { AuthNavigator } from "./AuthNavigator";
import { MainTabNavigator } from "./MainTabNavigator";
import { colors } from "../theme";

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
export function RootNavigator() {
  const [isAuthenticated] = useState(false);

  return (
    <NavigationContainer theme={navigationTheme}>
      {isAuthenticated ? <MainTabNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
}
