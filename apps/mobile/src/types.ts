export type DiscoveryProfile = {
  user_id: string;
  username: string;
  display_name: string;
  bio: string;
  gender: string;
  pronouns: string | null;
  height_cm: number | null;
  interests: { id: string; name: string }[];
  profile_completion_percentage: number;
};
