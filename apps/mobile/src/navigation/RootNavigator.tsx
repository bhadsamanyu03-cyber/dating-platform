import { ActivityIndicator, View } from "react-native";
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

function NavigatorContent() {
  const { session, restoring } = useAuthSession();
  if (restoring) {
    return (
      <View
        style={{
          flex: 1,
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: colors.background,
        }}
      >
        <ActivityIndicator />
      </View>
    );
  }
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
