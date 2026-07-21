import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { HomeScreen } from "../screens/main/HomeScreen";
import { DiscoveryScreen } from "../DiscoveryScreen";
import { FeedScreen } from "../FeedScreen";
import { ConversationsScreen } from "../ConversationsScreen";
import { ProfileScreen } from "../ProfileScreen";
import { BottomTabBar, BottomTabItem } from "../components/BottomTabBar";
import { colors } from "../theme";
import { useAuthSession } from "../AuthSession";

export type MainTabParamList = {
  Home: undefined;
  Discover: undefined;
  Feed: undefined;
  Messages: undefined;
  Profile: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();

const TAB_ITEMS: BottomTabItem[] = [
  { key: "Home", label: "Home", icon: "home", activeIcon: "homeActive" },
  {
    key: "Discover",
    label: "Discover",
    icon: "discover",
    activeIcon: "discoverActive",
  },
  { key: "Feed", label: "Feed", icon: "feed", activeIcon: "feedActive" },
  {
    key: "Messages",
    label: "Messages",
    icon: "messages",
    activeIcon: "messagesActive",
  },
  {
    key: "Profile",
    label: "Profile",
    icon: "profile",
    activeIcon: "profileActive",
  },
];

export function MainTabNavigator() {
  const { session } = useAuthSession();
  if (!session) return null;
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        sceneStyle: { backgroundColor: colors.background },
      }}
      tabBar={({ state, navigation }) => (
        <BottomTabBar
          items={TAB_ITEMS}
          activeKey={state.routeNames[state.index]}
          onSelect={(key) => navigation.navigate(key)}
        />
      )}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Discover">
        {() => <DiscoveryScreen accessToken={session.accessToken} />}
      </Tab.Screen>
      <Tab.Screen name="Feed">{() => <FeedScreen />}</Tab.Screen>
      <Tab.Screen name="Messages">
        {() => <ConversationsScreen accessToken={session.accessToken} />}
      </Tab.Screen>
      <Tab.Screen name="Profile">
        {() => <ProfileScreen accessToken={session.accessToken} />}
      </Tab.Screen>
    </Tab.Navigator>
  );
}
