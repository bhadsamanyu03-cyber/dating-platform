import AsyncStorage from "@react-native-async-storage/async-storage";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { logout, refreshSession } from "./authApi";

type Session = { accessToken: string; refreshToken: string };
type AuthSessionValue = {
  session: Session | null;
  restoring: boolean;
  signIn: (session: Session) => Promise<void>;
  signOut: () => Promise<void>;
};

const STORAGE_KEY = "dating-platform:session";

const AuthSessionContext = createContext<AuthSessionValue | undefined>(
  undefined,
);

export function AuthSessionProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [session, setSession] = useState<Session | null>(null);
  const [restoring, setRestoring] = useState(true);

  useEffect(() => {
    const restore = async () => {
      try {
        const raw = await AsyncStorage.getItem(STORAGE_KEY);
        if (!raw) return;
        const stored = JSON.parse(raw) as Session;
        const refreshed = await refreshSession(stored.refreshToken);
        const next = {
          accessToken: refreshed.access_token,
          refreshToken: refreshed.refresh_token,
        };
        setSession(next);
        await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {
        await AsyncStorage.removeItem(STORAGE_KEY);
      } finally {
        setRestoring(false);
      }
    };
    void restore();
  }, []);

  const value = useMemo(
    () => ({
      session,
      restoring,
      signIn: async (next: Session) => {
        setSession(next);
        await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      },
      signOut: async () => {
        const current = session;
        setSession(null);
        await AsyncStorage.removeItem(STORAGE_KEY);
        if (current?.refreshToken) {
          await logout(current.refreshToken).catch(() => undefined);
        }
      },
    }),
    [session, restoring],
  );
  return (
    <AuthSessionContext.Provider value={value}>
      {children}
    </AuthSessionContext.Provider>
  );
}

export function useAuthSession() {
  const value = useContext(AuthSessionContext);
  if (!value)
    throw new Error("useAuthSession must be used inside AuthSessionProvider");
  return value;
}
