function getStorage(
  storageType: "localStorage" | "sessionStorage",
): Storage | null {
  if (typeof window === "undefined") return null;

  try {
    return window[storageType];
  } catch {
    return null;
  }
}

export function safeGetLocalStorage(key: string): string | null {
  try {
    return getStorage("localStorage")?.getItem(key) ?? null;
  } catch {
    return null;
  }
}

export function safeSetLocalStorage(key: string, value: string): void {
  try {
    getStorage("localStorage")?.setItem(key, value);
  } catch {
    // Ignore browsers that block embedded storage access.
  }
}

export function safeRemoveLocalStorage(key: string): void {
  try {
    getStorage("localStorage")?.removeItem(key);
  } catch {
    // Ignore browsers that block embedded storage access.
  }
}

export function safeGetSessionStorage(key: string): string | null {
  try {
    return getStorage("sessionStorage")?.getItem(key) ?? null;
  } catch {
    return null;
  }
}

export function safeSetSessionStorage(key: string, value: string): void {
  try {
    getStorage("sessionStorage")?.setItem(key, value);
  } catch {
    // Ignore browsers that block embedded storage access.
  }
}

export function safeRemoveSessionStorage(key: string): void {
  try {
    getStorage("sessionStorage")?.removeItem(key);
  } catch {
    // Ignore browsers that block embedded storage access.
  }
}

export function safeNavigatorLanguage(): string {
  if (typeof navigator === "undefined") return "en";

  try {
    return navigator.language?.split("-")[0] || "en";
  } catch {
    return "en";
  }
}

export function safeMatchMedia(query: string): MediaQueryList | null {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return null;
  }

  try {
    return window.matchMedia(query);
  } catch {
    return null;
  }
}

export function safeMatchesMediaQuery(
  query: string,
  fallback = false,
): boolean {
  return safeMatchMedia(query)?.matches ?? fallback;
}

export function subscribeToMediaQuery(
  mediaQuery: MediaQueryList | null,
  listener: (event?: MediaQueryListEvent) => void,
): () => void {
  if (!mediaQuery) return () => {};

  if (typeof mediaQuery.addEventListener === "function") {
    mediaQuery.addEventListener("change", listener);
    return () => {
      mediaQuery.removeEventListener("change", listener);
    };
  }

  if (typeof mediaQuery.addListener === "function") {
    mediaQuery.addListener(listener);
    return () => {
      mediaQuery.removeListener(listener);
    };
  }

  return () => {};
}
