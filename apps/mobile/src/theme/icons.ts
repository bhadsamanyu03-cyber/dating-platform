import type { ComponentProps } from "react";
import { Ionicons } from "@expo/vector-icons";

/**
 * Central icon name map so screens/components never hardcode a raw
 * icon-set name. `@expo/vector-icons` ships with Expo, no extra install.
 */
export const iconNames = {
  home: "home-outline",
  homeActive: "home",
  discover: "compass-outline",
  discoverActive: "compass",
  feed: "grid-outline",
  feedActive: "grid",
  messages: "chatbubble-outline",
  messagesActive: "chatbubble",
  profile: "person-outline",
  profileActive: "person",
  back: "chevron-back",
  close: "close",
  search: "search-outline",
  filter: "options-outline",
  send: "arrow-up-circle",
  check: "checkmark-circle",
  checkDouble: "checkmark-done",
  error: "alert-circle-outline",
  image: "image-outline",
  camera: "camera-outline",
} satisfies Record<string, ComponentProps<typeof Ionicons>["name"]>;

export type IconName = keyof typeof iconNames;
export { Ionicons as IconSet };
