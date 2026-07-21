import {
  Linking,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

const APP_VERSION = "0.1.0";
const BUILD_NUMBER = "1";
const APP_NAME = "Corvinth";

type Props = {
  accessToken: string;
};

export function AboutAppScreen({ accessToken }: Props) {
  const handleOpenLink = (url: string) => {
    Linking.openURL(url).catch(() => {
      alert(`Unable to open ${url}`);
    });
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.header}>
        <Text style={styles.appName}>{APP_NAME}</Text>
        <Text style={styles.tagline}>Find your match</Text>
      </View>

      <View style={styles.versionBox}>
        <Text style={styles.versionLabel}>Version</Text>
        <Text style={styles.version}>{APP_VERSION}</Text>
        <Text style={styles.buildNumber}>Build {BUILD_NUMBER}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <Text style={styles.aboutText}>
          Corvinth is a modern dating platform designed to help you find
          meaningful connections. We're committed to creating a safe,
          respectful, and inclusive community for all users.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Legal & Policy</Text>
        <LinkItem
          icon="📋"
          title="Terms of Service"
          onPress={() => handleOpenLink("https://example.com/terms")}
        />
        <LinkItem
          icon="🔐"
          title="Privacy Policy"
          onPress={() => handleOpenLink("https://example.com/privacy")}
        />
        <LinkItem
          icon="❤️"
          title="Community Guidelines"
          onPress={() => handleOpenLink("https://example.com/community")}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Contact & Support</Text>
        <LinkItem
          icon="💌"
          title="Contact Support"
          onPress={() =>
            Linking.openURL(
              "mailto:support@corvinth.local?subject=Support Request",
            )
          }
        />
        <LinkItem
          icon="🐛"
          title="Report a Bug"
          onPress={() =>
            Linking.openURL("mailto:bugs@corvinth.local?subject=Bug Report")
          }
        />
        <LinkItem
          icon="💡"
          title="Send Feedback"
          onPress={() =>
            Linking.openURL(
              "mailto:feedback@corvinth.local?subject=Feature Feedback",
            )
          }
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Connect With Us</Text>
        <LinkItem
          icon="🔗"
          title="Website"
          onPress={() => handleOpenLink("https://corvinth.local")}
        />
        <LinkItem
          icon="📱"
          title="Twitter"
          onPress={() => handleOpenLink("https://twitter.com/corvinth")}
        />
        <LinkItem
          icon="📷"
          title="Instagram"
          onPress={() => handleOpenLink("https://instagram.com/corvinth")}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Credits</Text>
        <Text style={styles.creditsText}>
          Built with React Native, Expo, and TypeScript.
        </Text>
        <Text style={styles.creditsText}>
          Powered by FastAPI and PostgreSQL.
        </Text>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          © 2026 Corvinth. All rights reserved.
        </Text>
        <Text style={styles.madeWith}>
          Made with ❤️ for meaningful connections
        </Text>
      </View>
    </ScrollView>
  );
}

function LinkItem(props: { icon: string; title: string; onPress: () => void }) {
  return (
    <Pressable
      style={({ pressed }) => [
        styles.linkItem,
        pressed && styles.linkItemPressed,
      ]}
      onPress={props.onPress}
    >
      <Text style={styles.linkIcon}>{props.icon}</Text>
      <View style={styles.linkContent}>
        <Text style={styles.linkTitle}>{props.title}</Text>
        <Text style={styles.linkArrow}>›</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: { paddingVertical: 24, paddingHorizontal: 16, gap: 24 },
  header: {
    alignItems: "center",
    gap: 8,
    paddingBottom: 16,
  },
  appName: {
    fontSize: 32,
    fontWeight: "700",
    color: "#1976d2",
  },
  tagline: {
    fontSize: 16,
    color: "#666",
    fontStyle: "italic",
  },
  versionBox: {
    backgroundColor: "#f5f5f5",
    borderRadius: 12,
    padding: 16,
    alignItems: "center",
    gap: 6,
  },
  versionLabel: {
    fontSize: 12,
    color: "#999",
    textTransform: "uppercase",
    fontWeight: "600",
    letterSpacing: 0.5,
  },
  version: {
    fontSize: 24,
    fontWeight: "700",
    color: "#000",
  },
  buildNumber: {
    fontSize: 12,
    color: "#999",
  },
  section: {
    gap: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#000",
    marginBottom: 4,
  },
  aboutText: {
    fontSize: 14,
    color: "#666",
    lineHeight: 20,
  },
  linkItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderRadius: 8,
    gap: 12,
  },
  linkItemPressed: {
    backgroundColor: "#f5f5f5",
  },
  linkIcon: {
    fontSize: 20,
  },
  linkContent: {
    flex: 1,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  linkTitle: {
    fontSize: 15,
    fontWeight: "500",
    color: "#000",
  },
  linkArrow: {
    fontSize: 18,
    color: "#ccc",
  },
  creditsText: {
    fontSize: 13,
    color: "#999",
    lineHeight: 18,
  },
  footer: {
    alignItems: "center",
    gap: 8,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: "#f0f0f0",
  },
  footerText: {
    fontSize: 12,
    color: "#999",
  },
  madeWith: {
    fontSize: 13,
    color: "#1976d2",
    fontWeight: "600",
  },
});
