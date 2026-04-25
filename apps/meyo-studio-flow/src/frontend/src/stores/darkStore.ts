import { create } from "zustand";
import { getDiscordCount, getRepoStars } from "../controllers/API";
import type { DarkStoreType } from "../types/zustand/dark";
import {
  safeGetLocalStorage,
  safeMatchesMediaQuery,
  safeSetLocalStorage,
} from "../utils/browser";

const startedStars = Number(safeGetLocalStorage("githubStars") ?? "0") || 0;

export const useDarkStore = create<DarkStoreType>((set, get) => ({
  dark: (() => {
    const stored = safeGetLocalStorage("isDark");
    if (stored !== null) {
      try {
        return JSON.parse(stored);
      } catch {
        // Fall back to the media query when stored data is malformed.
      }
    }
    return safeMatchesMediaQuery("(prefers-color-scheme: dark)");
  })(),
  stars: startedStars,
  version: "",
  latestVersion: "",
  refreshLatestVersion: (v: string) => {
    set(() => ({ latestVersion: v }));
  },
  setDark: (dark) => {
    set(() => ({ dark: dark }));
    safeSetLocalStorage("isDark", dark.toString());
  },
  refreshVersion: (v) => {
    set(() => ({ version: v }));
  },
  refreshStars: () => {
    if (import.meta.env.CI) {
      safeSetLocalStorage("githubStars", "0");
      set(() => ({ stars: 0, lastUpdated: new Date() }));
      return;
    }
    const lastUpdated = safeGetLocalStorage("githubStarsLastUpdated");
    let diff = 0;
    // check if lastUpdated actually exists
    if (lastUpdated !== null) {
      diff = Math.abs(new Date().getTime() - new Date(lastUpdated).getTime());
    }

    // if lastUpdated is null or the difference is greater than 2 hours
    if (lastUpdated === null || diff > 7200000) {
      getRepoStars("langflow-ai", "langflow").then((res) => {
        safeSetLocalStorage("githubStars", res?.toString() ?? "0");
        safeSetLocalStorage(
          "githubStarsLastUpdated",
          new Date().toString(),
        );
        set(() => ({ stars: res, lastUpdated: new Date() }));
      });
    }
  },
  discordCount: 0,
  refreshDiscordCount: () => {
    getDiscordCount().then((res) => {
      set(() => ({ discordCount: res }));
    });
  },
}));
