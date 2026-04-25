import { AUTHORIZED_DUPLICATE_REQUESTS } from "../../../constants/constants";
import {
  safeGetLocalStorage,
  safeSetLocalStorage,
} from "../../../utils/browser";

export function checkDuplicateRequestAndStoreRequest(config) {
  const lastUrl = safeGetLocalStorage("lastUrlCalled");
  const lastMethodCalled = safeGetLocalStorage("lastMethodCalled");
  const lastRequestTime = safeGetLocalStorage("lastRequestTime");
  const lastCurrentUrl = safeGetLocalStorage("lastCurrentUrl");

  const currentUrl = window.location.pathname;
  const currentTime = Date.now();
  const isContained = AUTHORIZED_DUPLICATE_REQUESTS.some((request) =>
    config?.url!.includes(request),
  );

  if (
    config?.url === lastUrl &&
    !isContained &&
    lastMethodCalled === config.method &&
    lastMethodCalled === "get" && // Assuming you want to check only for GET requests
    lastRequestTime &&
    currentTime - parseInt(lastRequestTime, 10) < 300 &&
    lastCurrentUrl === currentUrl
  ) {
    throw new Error("Duplicate request: " + lastUrl);
  }

  safeSetLocalStorage("lastUrlCalled", config.url ?? "");
  safeSetLocalStorage("lastMethodCalled", config.method ?? "");
  safeSetLocalStorage("lastRequestTime", currentTime.toString());
  safeSetLocalStorage("lastCurrentUrl", currentUrl);
}
