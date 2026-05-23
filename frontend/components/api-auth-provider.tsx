"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect } from "react";
import { setAuthTokenGetter } from "@/services/api";

export function ApiAuthProvider({ children }: { children: React.ReactNode }) {
  const { getToken, isLoaded } = useAuth();

  useEffect(() => {
    if (!isLoaded) {
      return;
    }

    setAuthTokenGetter(async () => getToken());
    return () => setAuthTokenGetter(null);
  }, [getToken, isLoaded]);

  return children;
}
