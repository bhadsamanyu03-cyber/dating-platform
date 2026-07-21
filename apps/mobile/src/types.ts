export type DiscoveryProfile = {
  user_id: string;
  username: string;
  display_name: string;
  bio: string;
  gender: string;
  pronouns: string | null;
  age: number;
  height_cm: number | null;
  interests: { id: string; name: string }[];
  profile_completion_percentage: number;
};

export type MatchResponse = {
  id: string;
  created_at: string;
  updated_at: string;
  match: { user_id: string; username: string; display_name: string };
};
