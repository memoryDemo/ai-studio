import * as React from "react";
import { safeMatchMedia, subscribeToMediaQuery } from "@/utils/browser";

const MOBILE_BREAKPOINT = 768;

export function useIsMobile({ maxWidth }: { maxWidth?: number } = {}) {
  const breakpoint = maxWidth || MOBILE_BREAKPOINT;
  const [isMobile, setIsMobile] = React.useState<boolean | undefined>(
    undefined,
  );

  React.useEffect(() => {
    const mql = safeMatchMedia(`(max-width: ${breakpoint - 1}px)`);

    const handleResize = () => {
      if (typeof window !== "undefined") {
        setIsMobile(window.innerWidth < breakpoint);
      }
    };

    // Initial check
    handleResize();

    if (typeof window === "undefined") return;

    const unsubscribe = subscribeToMediaQuery(mql, handleResize);
    window.addEventListener("resize", handleResize);

    return () => {
      unsubscribe();
      window.removeEventListener("resize", handleResize);
    };
  }, [breakpoint]);

  return !!isMobile;
}
