import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "react-native";
import { RootNavigator } from "./src/navigation";
import { ToastProvider } from "./src/components";
import { colors } from "./src/theme";

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
