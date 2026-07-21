import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "react-native";
import { RootNavigator } from "./src/navigation";
import { ToastProvider } from "./src/components";
import { colors } from "./src/theme";

/**
 * NOTE: `AuthGate.tsx` still holds the current working, backend-connected
 * auth + screen-switcher flow. It is intentionally left untouched.
 * `RootNavigator` is the new design-system navigation shell (Phase C);
 * real screens will be reconnected to the existing backend contracts one
 * at a time in the next phase, then this entry point will call into them.
 */
export default function App() {
  return (
    <SafeAreaProvider>
      <ToastProvider>
        <StatusBar
          barStyle="light-content"
          backgroundColor={colors.background}
        />
        <RootNavigator />
      </ToastProvider>
    </SafeAreaProvider>
  );
}
