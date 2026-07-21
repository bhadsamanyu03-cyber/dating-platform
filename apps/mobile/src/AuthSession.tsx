import { createContext, useContext, useMemo, useState } from "react";

type Session = { accessToken: string; refreshToken: string };
type AuthSessionValue = {
  session: Session | null;
  signIn: (session: Session) => void;
  signOut: () => void;
};

const AuthSessionContext = createContext<AuthSessionValue | undefined>(
  undefined,
);

export function AuthSessionProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [session, setSession] = useState<Session | null>(null);
  const value = useMemo(
    () => ({ session, signIn: setSession, signOut: () => setSession(null) }),
    [session],
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
