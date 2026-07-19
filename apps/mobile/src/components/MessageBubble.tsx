import { memo, useEffect, useRef } from "react";
import { Animated, Image, StyleSheet, Text, View } from "react-native";
import { colors, iconNames, IconSet, radii, spacing, typography } from "../theme";

export type MessageStatus = "sending" | "sent" | "delivered" | "read" | "failed";

export type MessageBubbleProps = {
  text?: string;
  imageUri?: string;
  isOwn: boolean;
  status?: MessageStatus;
  timeLabel?: string;
  onRetry?: () => void;
};

function StatusIcon({ status }: { status?: MessageStatus }) {
  if (!status || status === "sending") return null;
  if (status === "failed") {
    return <IconSet name={iconNames.error} size={14} color={colors.error} />;
  }
  if (status === "read") {
    return (
      <IconSet name={iconNames.checkDouble} size={14} color={colors.primary} />
    );
  }
  if (status === "delivered") {
    return (
      <IconSet
        name={iconNames.checkDouble}
        size={14}
        color={colors.text.muted}
      />
    );
  }
  return (
    <IconSet name={iconNames.check} size={14} color={colors.text.muted} />
  );
}

function MessageBubbleBase({
  text,
  imageUri,
  isOwn,
  status,
  timeLabel,
  onRetry,
}: MessageBubbleProps) {
  const translateY = useRef(new Animated.Value(6)).current;
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(translateY, {
        toValue: 0,
        duration: 220,
        useNativeDriver: true,
      }),
      Animated.timing(opacity, {
        toValue: 1,
        duration: 220,
        useNativeDriver: true,
      }),
    ]).start();
  }, [opacity, translateY]);

  const isFailed = status === "failed";
  const isSending = status === "sending";

  return (
    <Animated.View
      style={[
        styles.row,
        isOwn ? styles.rowOwn : styles.rowOther,
        { opacity, transform: [{ translateY }] },
      ]}
    >
      <View
        style={[
          styles.bubble,
          isOwn ? styles.bubbleOwn : styles.bubbleOther,
          isFailed && styles.bubbleFailed,
          isSending && styles.bubbleSending,
        ]}
      >
        {imageUri ? (
          <Image source={{ uri: imageUri }} style={styles.image} />
        ) : null}
        {text ? (
          <Text style={isOwn ? styles.textOwn : styles.textOther}>
            {text}
          </Text>
        ) : null}
        <View style={styles.meta}>
          {timeLabel ? <Text style={styles.time}>{timeLabel}</Text> : null}
          {isOwn ? <StatusIcon status={status} /> : null}
        </View>
      </View>
      {isFailed && onRetry ? (
        <Text onPress={onRetry} style={styles.retry}>
          Tap to retry
        </Text>
      ) : null}
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  row: {
    marginVertical: spacing.xxs,
    maxWidth: "78%",
  },
  rowOwn: {
    alignSelf: "flex-end",
    alignItems: "flex-end",
  },
  rowOther: {
    alignSelf: "flex-start",
    alignItems: "flex-start",
  },
  bubble: {
    borderRadius: radii.lg,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    gap: spacing.xxs,
  },
  bubbleOwn: {
    backgroundColor: colors.primary,
    borderBottomRightRadius: radii.sm,
  },
  bubbleOther: {
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.border,
    borderBottomLeftRadius: radii.sm,
  },
  bubbleSending: {
    opacity: 0.6,
  },
  bubbleFailed: {
    borderWidth: 1,
    borderColor: colors.error,
  },
  image: {
    width: 200,
    height: 200,
    borderRadius: radii.sm,
    marginBottom: spacing.xxs,
  },
  textOwn: {
    color: colors.text.primary,
    fontSize: typography.size.base,
  },
  textOther: {
    color: colors.text.primary,
    fontSize: typography.size.base,
  },
  meta: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "flex-end",
    gap: 4,
  },
  time: {
    color: "rgba(255,255,255,0.6)",
    fontSize: typography.size.xs,
  },
  retry: {
    color: colors.error,
    fontSize: typography.size.xs,
    marginTop: 2,
  },
});

export const MessageBubble = memo(MessageBubbleBase);
