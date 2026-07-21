import { memo } from "react";
import { Image, Pressable, StyleSheet, Text, View } from "react-native";
import {
  colors,
  iconNames,
  IconSet,
  radii,
  spacing,
  typography,
} from "../theme";
import { Avatar } from "./Avatar";

export type FeedCardProps = {
  authorName: string;
  authorAvatarUri?: string;
  mediaUri?: string;
  caption?: string;
  likeCount?: number;
  commentCount?: number;
  liked?: boolean;
  onPressLike?: () => void;
  onPressComment?: () => void;
};

function FeedCardBase({
  authorName,
  authorAvatarUri,
  mediaUri,
  caption,
  likeCount = 0,
  commentCount = 0,
  liked,
  onPressLike,
  onPressComment,
}: FeedCardProps) {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Avatar uri={authorAvatarUri} name={authorName} size={36} />
        <Text style={styles.authorName}>{authorName}</Text>
      </View>

      {mediaUri ? (
        <Image source={{ uri: mediaUri }} style={styles.media} />
      ) : null}

      <View style={styles.actions}>
        <Pressable
          onPress={onPressLike}
          accessibilityRole="button"
          accessibilityLabel="Like"
          hitSlop={8}
          style={styles.actionButton}
        >
          <IconSet
            name={liked ? "heart" : "heart-outline"}
            size={22}
            color={liked ? colors.error : colors.text.secondary}
          />
          <Text style={styles.actionCount}>{likeCount}</Text>
        </Pressable>
        <Pressable
          onPress={onPressComment}
          accessibilityRole="button"
          accessibilityLabel="Comment"
          hitSlop={8}
          style={styles.actionButton}
        >
          <IconSet
            name={iconNames.messages}
            size={20}
            color={colors.text.secondary}
          />
          <Text style={styles.actionCount}>{commentCount}</Text>
        </Pressable>
      </View>

      {caption ? (
        <Text style={styles.caption} numberOfLines={3}>
          <Text style={styles.authorNameInline}>{authorName} </Text>
          {caption}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: spacing.xs,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    paddingHorizontal: spacing.md,
  },
  authorName: {
    color: colors.text.primary,
    fontWeight: typography.weight.semibold,
    fontSize: typography.size.sm,
  },
  authorNameInline: {
    fontWeight: typography.weight.semibold,
  },
  media: {
    width: "100%",
    aspectRatio: 1,
    borderRadius: radii.md,
    backgroundColor: colors.cardElevated,
  },
  actions: {
    flexDirection: "row",
    gap: spacing.md,
    paddingHorizontal: spacing.md,
  },
  actionButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xxs,
  },
  actionCount: {
    color: colors.text.secondary,
    fontSize: typography.size.sm,
  },
  caption: {
    color: colors.text.secondary,
    fontSize: typography.size.sm,
    paddingHorizontal: spacing.md,
  },
});

export const FeedCard = memo(FeedCardBase);
