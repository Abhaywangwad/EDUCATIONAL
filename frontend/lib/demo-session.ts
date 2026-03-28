"use client";

import { useEffect, useState } from "react";
import type { PortalUser, Role } from "./api";

const STORAGE_KEY = "hlgs-demo-session";

export type DemoSession = {
  role: Role;
  userId: string;
  displayName: string;
  gradeLevel?: string | null;
};

export function saveDemoSession(user: PortalUser) {
  if (typeof window === "undefined") {
    return;
  }

  const session: DemoSession = {
    role: user.role,
    userId: user.id,
    displayName: user.full_name,
    gradeLevel: user.grade_level
  };
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  window.dispatchEvent(new Event("hlgs-session-change"));
}

export function clearDemoSession() {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(STORAGE_KEY);
  window.dispatchEvent(new Event("hlgs-session-change"));
}

export function readDemoSession(): DemoSession | null {
  if (typeof window === "undefined") {
    return null;
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as DemoSession;
  } catch {
    return null;
  }
}

export function useDemoSession(requiredRole?: Role) {
  const [session, setSession] = useState<DemoSession | null>(null);

  useEffect(() => {
    function syncSession() {
      setSession(readDemoSession());
    }

    syncSession();
    window.addEventListener("hlgs-session-change", syncSession);
    window.addEventListener("storage", syncSession);
    return () => {
      window.removeEventListener("hlgs-session-change", syncSession);
      window.removeEventListener("storage", syncSession);
    };
  }, []);

  const isAllowed = !requiredRole || session?.role === requiredRole;
  return { session, isAllowed };
}
