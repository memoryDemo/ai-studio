// Custom Hook to manage theme logic

import { useEffect, useState } from "react";
import { useDarkStore } from "@/stores/darkStore";
import {
  safeGetLocalStorage,
  safeMatchMedia,
  safeSetLocalStorage,
  subscribeToMediaQuery,
} from "@/utils/browser";

const useTheme = () => {
  const [systemTheme, setSystemTheme] = useState(false);
  const { setDark, dark } = useDarkStore((state) => ({
    setDark: state.setDark,
    dark: state.dark,
  }));

  const handleSystemTheme = () => {
    const systemDarkMode =
      safeMatchMedia("(prefers-color-scheme: dark)")?.matches ?? false;
    setDark(systemDarkMode);
  };

  useEffect(() => {
    const themePreference = safeGetLocalStorage("themePreference");
    if (themePreference === "light") {
      setDark(false);
      setSystemTheme(false);
    } else if (themePreference === "dark") {
      setDark(true);
      setSystemTheme(false);
    } else {
      // Default to system theme
      setSystemTheme(true);
      handleSystemTheme();
    }
  }, []);

  useEffect(() => {
    if (systemTheme) {
      const mediaQuery = safeMatchMedia("(prefers-color-scheme: dark)");
      const handleChange = (e) => {
        setDark(e.matches);
      };
      return subscribeToMediaQuery(mediaQuery, handleChange);
    }
  }, [systemTheme]);

  const setThemePreference = (theme) => {
    if (theme === "light") {
      setDark(false);
      setSystemTheme(false);
    } else if (theme === "dark") {
      setDark(true);
      setSystemTheme(false);
    } else {
      setSystemTheme(true);
      handleSystemTheme();
    }
    safeSetLocalStorage("themePreference", theme);
  };

  return { systemTheme, dark, setThemePreference };
};

export default useTheme;
