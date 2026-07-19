import { memo, useState } from "react";
import {
  FlatList,
  Image,
  NativeScrollEvent,
  NativeSyntheticEvent,
  StyleSheet,
  View,
  useWindowDimensions,
} from "react-native";
import { colors, radii, spacing } from "../theme";

export type ImageCarouselProps = {
  uris: string[];
  height?: number;
};

function ImageCarouselBase({ uris, height = 320 }: ImageCarouselProps) {
  const { width } = useWindowDimensions();
  const itemWidth = width - spacing.md * 2;
  const [activeIndex, setActiveIndex] = useState(0);

  const onScroll = (e: NativeSyntheticEvent<NativeScrollEvent>) => {
    const index = Math.round(e.nativeEvent.contentOffset.x / itemWidth);
    if (index !== activeIndex) setActiveIndex(index);
  };

  if (!uris.length) {
    return <View style={[styles.empty, { height, width: itemWidth }]} />;
  }

  return (
    <View>
      <FlatList
        data={uris}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        keyExtractor={(uri, index) => `${uri}-${index}`}
        onScroll={onScroll}
        scrollEventThrottle={16}
        renderItem={({ item }) => (
          <Image
            source={{ uri: item }}
            style={{ width: itemWidth, height, borderRadius: radii.lg }}
          />
        )}
      />
      {uris.length > 1 ? (
        <View style={styles.dots}>
          {uris.map((_, i) => (
            <View
              key={i}
              style={[styles.dot, i === activeIndex && styles.dotActive]}
            />
          ))}
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  empty: {
    backgroundColor: colors.cardElevated,
    borderRadius: radii.lg,
  },
  dots: {
    flexDirection: "row",
    justifyContent: "center",
    gap: spacing.xxs,
    marginTop: spacing.xs,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.border,
  },
  dotActive: {
    backgroundColor: colors.primary,
    width: 16,
  },
});

export const ImageCarousel = memo(ImageCarouselBase);
