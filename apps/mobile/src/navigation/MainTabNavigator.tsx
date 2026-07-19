import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { HomeScreen } from "../screens/main/HomeScreen";
import { DiscoverScreen } from "./placeholders/DiscoverScreen";
import { FeedScreen } from "./placeholders/FeedScreen";
import { MessagesScreen } from "./placeholders/MessagesScreen";
import { ProfileScreen } from "./placeholders/ProfileScreen";
import { BottomTabBar, BottomTabItem } from "../components/BottomTabBar";
import { colors } from "../theme";

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
      <Tab.Screen name="Discover" component={DiscoverScreen} />
      <Tab.Screen name="Feed" component={FeedScreen} />
      <Tab.Screen name="Messages" component={MessagesScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}
