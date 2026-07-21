import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { WelcomeScreen } from "./placeholders/WelcomeScreen";
import { LoginScreen } from "./placeholders/LoginScreen";
import { RegisterScreen } from "./placeholders/RegisterScreen";
import { OtpScreen } from "./placeholders/OtpScreen";
import { CreateProfileScreen } from "./placeholders/CreateProfileScreen";
import { colors } from "../theme";

export type AuthStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  Otp: { email: string };
  CreateProfile: undefined;
};

const Stack = createNativeStackNavigator<AuthStackParamList>();

export function AuthNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: colors.background },
        animation: "fade",
      }}
    >
      <Stack.Screen name="Welcome" component={WelcomeScreen} />
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
      <Stack.Screen name="Otp" component={OtpScreen} />
      <Stack.Screen name="CreateProfile" component={CreateProfileScreen} />
    </Stack.Navigator>
  );
}
