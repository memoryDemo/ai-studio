import {
  safeGetLocalStorage,
  safeMatchMedia,
  safeSetLocalStorage,
  subscribeToMediaQuery,
} from "../browser";

describe("browser utils", () => {
  const originalLocalStorageDescriptor = Object.getOwnPropertyDescriptor(
    window,
    "localStorage",
  );
  const originalMatchMedia = window.matchMedia;

  afterEach(() => {
    if (originalLocalStorageDescriptor) {
      Object.defineProperty(window, "localStorage", originalLocalStorageDescriptor);
    }

    window.matchMedia = originalMatchMedia;
  });

  it("returns null when localStorage access throws", () => {
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      get() {
        throw new DOMException("Blocked", "SecurityError");
      },
    });

    expect(safeGetLocalStorage("themePreference")).toBeNull();
    expect(() => safeSetLocalStorage("themePreference", "dark")).not.toThrow();
  });

  it("returns null when matchMedia throws", () => {
    window.matchMedia = jest.fn(() => {
      throw new Error("matchMedia unavailable");
    }) as typeof window.matchMedia;

    expect(safeMatchMedia("(prefers-color-scheme: dark)")).toBeNull();
  });

  it("subscribes with addListener fallback", () => {
    const addListener = jest.fn();
    const removeListener = jest.fn();
    const mediaQuery = {
      matches: false,
      media: "(prefers-color-scheme: dark)",
      onchange: null,
      addListener,
      removeListener,
      addEventListener: undefined,
      removeEventListener: undefined,
      dispatchEvent: jest.fn(),
    } as unknown as MediaQueryList;

    const listener = jest.fn();
    const unsubscribe = subscribeToMediaQuery(mediaQuery, listener);

    expect(addListener).toHaveBeenCalledWith(listener);

    unsubscribe();

    expect(removeListener).toHaveBeenCalledWith(listener);
  });
});
