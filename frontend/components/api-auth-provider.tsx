"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect } from "react";
import { setAuthTokenGetter, syncCurrentUser } from "@/services/api";

export function ApiAuthProvider({ children }: { children: React.ReactNode }) {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  useEffect(() => {
    if (!isLoaded) {
      return;
    }

    setAuthTokenGetter(async () => getToken());
    return () => setAuthTokenGetter(null);
  }, [getToken, isLoaded]);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) {
      return;
    }

    syncCurrentUser().catch((error) => {
      console.error("Could not sync authenticated user", error);
    });
  }, [isLoaded, isSignedIn]);

  return children;
}
